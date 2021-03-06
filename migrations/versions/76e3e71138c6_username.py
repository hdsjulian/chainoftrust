"""username

Revision ID: 76e3e71138c6
Revises: 1d5ae3d54109
Create Date: 2020-02-06 16:10:19.825243

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76e3e71138c6'
down_revision = '1d5ae3d54109'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('name', sa.String(length=128), nullable=True))
    op.create_index(op.f('ix_user_name'), 'user', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_name'), table_name='user')
    op.drop_column('user', 'name')
    # ### end Alembic commands ###
