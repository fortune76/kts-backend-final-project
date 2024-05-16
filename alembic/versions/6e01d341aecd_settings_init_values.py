"""settings init values

Revision ID: 6e01d341aecd
Revises: ee727c04750b
Create Date: 2024-05-16 18:16:35.070171

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e01d341aecd'
down_revision: Union[str, None] = 'ee727c04750b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('INSERT INTO game_settings VALUES (1, 30, 4, 500, 0, 500)')
    op.execute("INSERT INTO shares VALUES (1, 'Gazprom', 200)")
    op.execute("INSERT INTO shares VALUES (2, 'Sberbank', 250)")


def downgrade() -> None:
    op.execute('DELETE FROM game_settings WHERE id = 1')
    op.execute('DELETE FROM shares WHERE id = 1 OR id = 2')

