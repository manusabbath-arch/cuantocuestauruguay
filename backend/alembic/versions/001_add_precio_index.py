"""Add composite index on precio(producto_id, fecha)

Revision ID: 001_add_precio_index
Revises: 
Create Date: 2026-01-26 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_add_precio_index'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create composite index for faster queries on precio by producto and date
    op.create_index(
        'ix_precio_producto_id_fecha',
        'precios',
        ['producto_id', 'fecha'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_precio_producto_id_fecha', table_name='precios')
