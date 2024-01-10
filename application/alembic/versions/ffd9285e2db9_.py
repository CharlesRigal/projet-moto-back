"""empty message

Revision ID: ffd9285e2db9
Revises: ca67a7840cb4
Create Date: 2024-01-09 01:04:02.595029

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ffd9285e2db9'
down_revision: Union[str, None] = 'ca67a7840cb4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('friendships', sa.Column('requesting_user_id', sa.UUID(), nullable=True))
    op.add_column('friendships', sa.Column('target_user_id', sa.UUID(), nullable=True))
    op.drop_constraint('friendships_user_id_2_fkey', 'friendships', type_='foreignkey')
    op.drop_constraint('friendships_user_id_1_fkey', 'friendships', type_='foreignkey')
    op.create_foreign_key(None, 'friendships', 'users', ['requesting_user_id'], ['id'])
    op.create_foreign_key(None, 'friendships', 'users', ['target_user_id'], ['id'])
    op.drop_column('friendships', 'user_id_2')
    op.drop_column('friendships', 'user_id_1')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('friendships', sa.Column('user_id_1', sa.UUID(), autoincrement=False, nullable=True))
    op.add_column('friendships', sa.Column('user_id_2', sa.UUID(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'friendships', type_='foreignkey')
    op.drop_constraint(None, 'friendships', type_='foreignkey')
    op.create_foreign_key('friendships_user_id_1_fkey', 'friendships', 'users', ['user_id_1'], ['id'])
    op.create_foreign_key('friendships_user_id_2_fkey', 'friendships', 'users', ['user_id_2'], ['id'])
    op.drop_column('friendships', 'target_user_id')
    op.drop_column('friendships', 'requesting_user_id')
    # ### end Alembic commands ###
