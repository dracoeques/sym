"""empty message

Revision ID: 457a2cc0f225
Revises: eb97cd8b8d7f
Create Date: 2023-09-22 15:47:19.392916

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '457a2cc0f225'
down_revision = 'eb97cd8b8d7f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('edges', sa.Column('deleted', sa.Boolean(), nullable=True))
    op.add_column('nodes', sa.Column('deleted', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('nodes', 'deleted')
    op.drop_column('edges', 'deleted')
    # ### end Alembic commands ###
