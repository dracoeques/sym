"""empty message

Revision ID: 13e018db4474
Revises: 193edaf21cd2
Create Date: 2023-06-29 10:52:01.672624

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '13e018db4474'
down_revision = '193edaf21cd2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('nodes')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('nodes',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('id_prompt_flow', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('node_type', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('created_on', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('updated_on', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['id_prompt_flow'], ['prompt_flows.id'], name='nodes_id_prompt_flow_fkey'),
    sa.PrimaryKeyConstraint('id', name='nodes_pkey')
    )
    # ### end Alembic commands ###