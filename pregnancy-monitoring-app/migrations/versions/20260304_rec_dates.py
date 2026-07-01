"""add recommendation validity dates

Revision ID: 20260304_rec_dates
Revises:
Create Date: 2026-03-04
"""

from alembic import op
import sqlalchemy as sa


revision = '20260304_rec_dates'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('medical_recommendations', sa.Column('start_date', sa.Date(), nullable=True))
    op.add_column('medical_recommendations', sa.Column('end_date', sa.Date(), nullable=True))

    op.execute(
        """
        UPDATE medical_recommendations
        SET start_date = COALESCE(DATE(created_at), CURRENT_DATE),
            end_date = COALESCE(DATE(created_at), CURRENT_DATE)
        WHERE start_date IS NULL OR end_date IS NULL
        """
    )

    op.alter_column('medical_recommendations', 'start_date', nullable=False)
    op.alter_column('medical_recommendations', 'end_date', nullable=False)


def downgrade():
    op.drop_column('medical_recommendations', 'end_date')
    op.drop_column('medical_recommendations', 'start_date')
