"""empty message

Revision ID: ca67a7840cb4
Revises: 
Create Date: 2024-01-09 00:36:35.393875

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca67a7840cb4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('friendships', sa.Column('user_id_1', sa.UUID(), nullable=True))
    op.add_column('friendships', sa.Column('user_id_2', sa.UUID(), nullable=True))
    op.create_foreign_key(None, 'friendships', 'users', ['user_id_2'], ['id'])
    op.create_foreign_key(None, 'friendships', 'users', ['user_id_1'], ['id'])
    op.drop_column('friendships', 'id_user1')
    op.drop_column('friendships', 'id_user2')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('friendships', sa.Column('id_user2', sa.UUID(), autoincrement=False, nullable=True))
    op.add_column('friendships', sa.Column('id_user1', sa.UUID(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'friendships', type_='foreignkey')
    op.drop_constraint(None, 'friendships', type_='foreignkey')
    op.drop_column('friendships', 'user_id_2')
    op.drop_column('friendships', 'user_id_1')
    # ### end Alembic commands ###
