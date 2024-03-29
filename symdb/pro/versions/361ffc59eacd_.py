"""empty message

Revision ID: 361ffc59eacd
Revises: 9c1d6c2cd8ba
Create Date: 2024-01-23 12:46:15.656784

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '361ffc59eacd'
down_revision = '9c1d6c2cd8ba'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('first_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('avatar_image', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'avatar_image')
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
    # ### end Alembic commands ###
