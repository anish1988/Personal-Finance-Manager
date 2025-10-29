"""add new columns to transactions table

Revision ID: a902d0e05401
Revises: 7a0194310297
Create Date: 2025-10-29 09:12:10.254751

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a902d0e05401'
down_revision: Union[str, Sequence[str], None] = '7a0194310297'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.add_column('transactions', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('transactions', sa.Column('tx_date', sa.Date(), nullable=True))
    op.add_column('transactions', sa.Column('currency', sa.String(length=10), nullable=False, server_default='INR'))
    op.add_column('transactions', sa.Column('transaction_type', sa.String(length=32), nullable=True))
    op.add_column('transactions', sa.Column('category_id', sa.Integer(), nullable=True))
    op.add_column('transactions', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.add_column('transactions', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))

    # optional: migrate data from old columns
    op.execute("UPDATE transactions SET tx_date = date WHERE tx_date IS NULL;")
    op.execute("UPDATE transactions SET transaction_type = type WHERE transaction_type IS NULL;")

def downgrade():
    op.drop_column('transactions', 'updated_at')
    op.drop_column('transactions', 'created_at')
    op.drop_column('transactions', 'category_id')
    op.drop_column('transactions', 'transaction_type')
    op.drop_column('transactions', 'currency')
    op.drop_column('transactions', 'tx_date')
    op.drop_column('transactions', 'user_id')
