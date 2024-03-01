"""empty message

Revision ID: c7631b1f30b2
Revises: 575850f5e5de
Create Date: 2023-12-04 11:24:28.404556

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7631b1f30b2'
down_revision = '575850f5e5de'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('media_feeds', sa.Column('description', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('media_feeds', 'description')
    # ### end Alembic commands ###
