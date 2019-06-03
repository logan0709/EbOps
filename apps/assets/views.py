from . import assets
from .. import db
from ..models import Host
from sqlalchemy import distinct, func, or_
from flask import jsonify, render_template, request
from flask_login import login_required


# 主机详细信息
@assets.route("/info/<hostname>", methods=['GET', 'POST'])
@login_required
def get_host_info(hostname):
    host = Host.query.filter(Host.hostname == hostname).first()
    return render_template('assets_info.html', app="资产管理", action="资产详情", host=host)


# 更新主机信息
@assets.route("/update/<hostname>", methods=['GET', 'POST'])
@login_required
def update_host_info(hostname):
    if request.method == "GET":
        host_info = Host.query.filter(Host.hostname == hostname).first()
        return render_template('assets_update.html', app="资产管理", action="资产更新", host=host_info)
    elif request.method == "POST":
        m_host = request.form
        try:
            db.session.query(Host).filter(Host.hostname == hostname).update(m_host)
            db.session.commit()
            return "success"
        except Exception as e:
            print(str(e))
            return "fail"


# 按业务平台分类获取节点信息
@assets.route("/get_nodes", methods=['GET', 'POST'])
@login_required
def get_nodes():
    cluste_type = db.session.query(distinct(Host.platform)).all()
    nodes = [x[0] for x in cluste_type]
    # ztree 一级节点
    z_nodes = []
    for i, node in enumerate(nodes):
        cluste_temps = db.session.query(distinct(Host.cluster)).filter(Host.platform == node).order_by(
            Host.cluster).all()
        clusters = [x[0] for x in cluste_temps]
        # 二级节点
        childrens = [{'name': cluster} for cluster in clusters]
        p1_data = {
            'name': node + " ({})".format(len(clusters)),
            'open': 'true' if i == 0 else 'false',
            'children': childrens
        }
        z_nodes.append(p1_data)
    return jsonify(z_nodes)


# 获取对应集群下的主机清单，集群名称通过post参数传递
@assets.route("/get_hosts", methods=['GET', 'POST'])
def get_hosts():
    cluester = request.form.get('cluster')
    hosts_temp = Host.query.filter(Host.cluster == cluester).all()
    # hosts = [x.hostname for x in hosts_temp]
    result = []
    for i, host in enumerate(hosts_temp):
        # result.append({
        #     'id': i,
        #     'name': host.hostname,
        #     'ip': host.local_ip,
        #     'device_type': host.device_type,
        #     'device_model': host.device_model,
        #     'engine_room': host.engine_room,
        #     'frame_number': host.frame_number
        # })
        result.append(host.to_json())
    # result = [{'id': i, 'name': x.hostname} for i, x in enumerate(hosts_temp)]
    return jsonify(result)


# 资产列表主页
@assets.route("/asset", methods=['GET', 'POST'])
@login_required
def asset():
    return render_template('assets_list.html', app="资产管理", action="资产列表")


# 资产统计
@assets.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    # 按业务平台分类汇总数量
    result = db.session.query(Host.platform, func.count('*').label("count")).filter(Host.status=="在网").group_by(Host.platform).all()
    platforms = [x[0] for x in result]
    platforms_counts = [x[1] for x in result]
    device_nums = sum(platforms_counts)
    # 按机房分类获取数量
    result_jf = db.session.query(Host.engine_room, func.count('*').label("count")).filter(Host.status=="在网").group_by(Host.engine_room).all()
    engine_rooms = [x[0] for x in result_jf]
    engine_rooms_values= [{"value": v, "name": k} for k, v in result_jf]
    # 按设备类型分类获取数量
    result_type = db.session.query(Host.device_type, func.count('*').label("count")).filter(Host.status=="在网").group_by(Host.device_type).all()
    device_types = [x[0] for x in result_type]
    device_types_nums = [x[1] for x in result_type]
    # device_types_values = [{"value": v, "name": k} for k, v in result_type]
    # 统计操作系统
    linux_nums = db.session.query(func.count('*').label("count")).filter(
        or_(Host.os_version.like("linux%"), Host.os_version.like("redhat%"))).all()
    hpux_nums = db.session.query(func.count('*').label("count")).filter(
        or_(Host.os_version.like("HP%"), Host.os_version.like("hp%"))).all()
    aix_nums = db.session.query(func.count('*').label("count")).filter(
        or_(Host.os_version.like("AIX%"), Host.os_version.like("aix%"))).all()
    return render_template('assets_dashboard.html', app="资产管理", action="资产统计",  **locals())