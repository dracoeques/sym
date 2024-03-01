"""empty message

Revision ID: a9127f2b8fa5
Revises: b077c0ac4b2f
Create Date: 2023-07-26 15:25:27.480253

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a9127f2b8fa5'
down_revision = 'b077c0ac4b2f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('prompt_flows', sa.Column('hidden', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('prompt_flows', 'hidden')
    # ### end Alembic commands ###
