"""empty message

Revision ID: c1e1c001f238
Revises: 
Create Date: 2019-04-26 10:11:16.820380

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c1e1c001f238'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('hostname', table_name='host')
    op.drop_index('ix_host_cluster', table_name='host')
    op.drop_index('ix_host_type', table_name='host')
    op.drop_table('host')
    op.drop_table('history')
    op.drop_table('jobs')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('jobs',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('cron_time', mysql.VARCHAR(length=64), nullable=False),
    sa.Column('content', mysql.VARCHAR(length=64), nullable=False),
    sa.Column('status', mysql.SMALLINT(display_width=6), autoincrement=False, nullable=True),
    sa.Column('name', mysql.VARCHAR(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('history',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('hostname', mysql.VARCHAR(length=32), nullable=False),
    sa.Column('checktime', mysql.VARCHAR(length=64), nullable=False),
    sa.Column('type', mysql.VARCHAR(length=32), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('host',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('type', mysql.VARCHAR(length=32), nullable=False),
    sa.Column('cluster', mysql.VARCHAR(length=32), nullable=False),
    sa.Column('hostname', mysql.VARCHAR(length=32), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_host_type', 'host', ['type'], unique=False)
    op.create_index('ix_host_cluster', 'host', ['cluster'], unique=False)
    op.create_index('hostname', 'host', ['hostname'], unique=True)
    # ### end Alembic commands ###
