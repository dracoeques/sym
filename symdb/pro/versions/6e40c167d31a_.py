"""empty message

Revision ID: 6e40c167d31a
Revises: be98c84a8d04
Create Date: 2023-06-29 10:38:13.474901

"""
from alembic import op
import sqlalchemy as sa
import pgvector

# revision identifiers, used by Alembic.
revision = '6e40c167d31a'
down_revision = 'be98c84a8d04'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('texts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(), nullable=True),
    sa.Column('openai_embedding', pgvector.sqlalchemy.Vector(dim=1536), nullable=True),
    sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_on', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id_textparent', sa.Integer(), nullable=True),
    sa.Column('start_index', sa.Integer(), nullable=True),
    sa.Column('end_index', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('profiles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_on', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('prompts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('id_text', sa.Integer(), nullable=True),
    sa.Column('id_profile', sa.Integer(), nullable=True),
    sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_on', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['id_profile'], ['users.id'], ),
    sa.ForeignKeyConstraint(['id_text'], ['texts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('prompts')
    op.drop_table('profiles')
    op.drop_table('texts')
    # ### end Alembic commands ###
