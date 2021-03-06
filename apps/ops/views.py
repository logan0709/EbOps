from . import ops
from .. import db
from ..models import OpsItem, OpsInfo, OpsResult, OpsEvent, OpsUndo
from datetime import datetime
from sqlalchemy import and_
from flask import render_template, request, jsonify
from flask_login import login_required


# 获取对应date 最新的执行记录结果
def get_result(ops_infos, date):
    results = []
    for item in ops_infos:
        # 根据item_id和date匹配执行结果，并按时间排序，取当天最后执行时间
        result = OpsResult.query.filter(and_(OpsResult.item_id == item.item_id,
                                             OpsResult.date == date)).order_by(OpsResult.time.desc()).first()
        results.append((item, result))
    return results


# 获取对应date 未执行记录原因
def get_undo_task(date):
    # 根据date匹配未执行原因的作业计划item_id, 并去重处理
    result_temps = OpsUndo.query.filter(OpsUndo.datetime.like(date+'%')).all()
    results = [x.item_id for x in result_temps]
    # 去重
    return set(results)


@ops.route("/<ops_type>", methods=['GET', 'POST'])
@login_required
def index(ops_type):
    # 查找ims对应的作业计划名称
    _ops_items = db.session.query(OpsItem.c_name).filter(OpsItem.t_name == ops_type).all()
    # 查找具体作业计划执行项
    _ops_infos = OpsInfo.query.filter(OpsInfo.t_name == ops_type).order_by(OpsInfo.id).all()
    ops_item = _ops_items[0][0]
    # 判断请求中是否带有日期，不带日期默认为当天
    if request.args.get('date_from'):
        date = request.args.get('date_from')
    else:
        date = datetime.now().strftime('%Y%m%d')
    # 根据日期和作业计划项item_id 获取执行记录
    _ops_results = get_result(_ops_infos, date)
    undo_tasks = get_undo_task(date)
    return render_template('ops_ims.html', app='作业计划', action=ops_item, ops_item=ops_item, ops_results=_ops_results,
                           undo_tasks=undo_tasks)


# @ops.route("/sec",methods=['GET','POST'])
# @login_required
# def sec():
#     _ops_items = db.session.query(OpsItem.c_name).filter(OpsItem.t_name == 'sec').all()
#     _ops_infos = db.session.query(OpsInfo.id, OpsInfo.content, OpsInfo.cycle).filter(OpsInfo.t_name == 'sec').all()
#     ops_item = _ops_items[0][0]
#     return render_template('ops_item.html', app='作业计划', action=ops_item, ops_item=ops_item, ops_infos=_ops_infos)
#
#
# @ops.route("/vpmn",methods=['GET','POST'])
# @login_required
# def vpmn():
#     _ops_items = db.session.query(OpsItem.c_name).filter(OpsItem.t_name == 'vpmn').all()
#     _ops_infos = db.session.query(OpsInfo.id, OpsInfo.content, OpsInfo.cycle).filter(OpsInfo.t_name == 'vpmn').all()
#     ops_item = _ops_items[0][0]
#     return render_template('ops_item.html', app='作业计划', action=ops_item, ops_item=ops_item, ops_infos=_ops_infos)
#
#
# @ops.route("/vss",methods=['GET','POST'])
# @login_required
# def vss():
#     _ops_items = db.session.query(OpsItem.c_name).filter(OpsItem.t_name == 'vss').all()
#     _ops_infos = db.session.query(OpsInfo.id, OpsInfo.content, OpsInfo.cycle).filter(OpsInfo.t_name == 'vss').all()
#     ops_item = _ops_items[0][0]
#     return render_template('ops_item.html', app='作业计划', action=ops_item, ops_item=ops_item, ops_infos=_ops_infos)
#
#
# @ops.route("/cl",methods=['GET','POST'])
# @login_required
# def cl():
#     _ops_items = db.session.query(OpsItem.c_name).filter(OpsItem.t_name == 'cl').all()
#     _ops_infos = db.session.query(OpsInfo.id, OpsInfo.content, OpsInfo.cycle).filter(OpsInfo.t_name == 'cl').all()
#     ops_item = _ops_items[0][0]
#     return render_template('ops_item.html', app='作业计划', action=ops_item, ops_item=ops_item, ops_infos=_ops_infos)


# 查看执行完整日志
@ops.route("/log/<log_id>")
@login_required
def ops_log(log_id):
    return render_template('ops_log.html', log_id=log_id)


@ops.route("/req")
@login_required
def request_log():
    import os
    from ..settings import OPS_LOG_FOLDER
    log_id = request.args.get('log_id')
    # filepath = '/Users/EB/PycharmProjects/EbOps'
    filename = log_id + '.txt'
    result = ''
    try:
        date = log_id.split('_')[2][:8]
        filepath = OPS_LOG_FOLDER + date
        with open(os.path.join(filepath, filename), encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                result += line + '\r\n'
            f.close()
    except Exception as e:
        print(str(e))
        result = "\n日志文件不存在"
    logs = {
        "data": result,
        "end": True,
        "mark": "7bbfef0c-103d-4b4f-8f43-39e7121db223"
    }
    return jsonify(logs)


# 查询任务详情
@ops.route("/task/<log_id>")
@login_required
def task(log_id):
    # 根据log_id获取对应的作业项目item_id
    # item_id = '_'.join(log_id.split('_')[:2])
    item_id = request.args.get('item_id')
    item = OpsInfo.query.filter(OpsInfo.item_id == item_id).one()
    # 查询对应任务编号log_id 执行总体结果, 多条结果时返回最新一条
    result = OpsResult.query.filter(OpsResult.log_id == log_id).order_by(OpsResult.time.desc()).first()
    # 查询任务明细
    events = OpsEvent.query.filter(OpsEvent.log_id == log_id).all()
    succ_events = [event for event in events if event.status == "succ"]
    fail_events = [event for event in events if event.status == "fail"]
    return render_template('ops_task.html', app='作业计划', action="任务详情", log_id=log_id, item=item, result=result,
                           succ_events=succ_events, fail_events=fail_events)


# 查看任务执行明细情况
@ops.route("/task/<log_id>/history")
@login_required
def task_history(log_id):
    # 查询对应任务编号log_id 执行总体结果
    result = OpsResult.query.filter(OpsResult.log_id == log_id).order_by(OpsResult.time.desc()).first()
    item_id = result.item_id
    # item_id = '_'.join(log_id.split('_')[:2])
    item = OpsInfo.query.filter(OpsInfo.item_id == item_id).one()
    # 获取get请求传过来的页数,没有传参数，默认为1
    page = int(request.args.get('page', 1))
    # 分页显示，每页10条数据
    paginate = OpsEvent.query.filter(OpsEvent.log_id == log_id).paginate(page, per_page=10, error_out=False)
    task_events = paginate.items
    return render_template('ops_task_history.html', app='作业计划', action="任务详情", log_id=log_id, item=item,
                           events=task_events, paginate=paginate)


# 获取作业计划最后执行时间
@ops.route("/get_checktime", methods=['GET', 'POST'])
@login_required
def get_checktime():
    item_id = request.form.get('item_id')
    check_log = db.session.query(OpsResult).filter(OpsResult.item_id==item_id).order_by(OpsResult.date.desc()).first()
    if check_log:
        checktime = str(check_log.date) + ":" + str(check_log.time)
        result = {
            'flag': "success",
            'message': "上次执行时间: {}".format(checktime)
        }
    else:
        result = {
            'flag': "success",
            'message': "未查询到执行记录"
        }
    return jsonify(result)