"""empty message

Revision ID: 91e0b6d7bbe5
Revises: 2985e279047f
Create Date: 2024-02-02 12:37:42.590123

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91e0b6d7bbe5'
down_revision = '2985e279047f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('profiles', sa.Column('seed_text', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('profiles', 'seed_text')
    # ### end Alembic commands ###