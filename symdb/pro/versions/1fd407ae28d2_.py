"""empty message

Revision ID: 1fd407ae28d2
Revises: f61b5a835459
Create Date: 2023-07-11 11:35:34.587344

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1fd407ae28d2'
down_revision = 'f61b5a835459'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('prompt_runs', sa.Column('id_profile', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'prompt_runs', 'profiles', ['id_profile'], ['id'])
    op.add_column('user_feedbacks', sa.Column('id_prompt_run', sa.Integer(), nullable=True))
    op.add_column('user_feedbacks', sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.create_foreign_key(None, 'user_feedbacks', 'prompt_runs', ['id_prompt_run'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_feedbacks', type_='foreignkey')
    op.drop_column('user_feedbacks', 'payload')
    op.drop_column('user_feedbacks', 'id_prompt_run')
    op.drop_constraint(None, 'prompt_runs', type_='foreignkey')
    op.drop_column('prompt_runs', 'id_profile')
    # ### end Alembic commands ###
