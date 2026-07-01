"""add patient age field

Revision ID: 20260528_patient_age
Revises: 20260304_rec_dates
Create Date: 2026-05-28
"""

from alembic import op
import sqlalchemy as sa


revision = '20260528_patient_age'
down_revision = '20260304_rec_dates'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('patients', sa.Column('age', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('patients', 'age')
