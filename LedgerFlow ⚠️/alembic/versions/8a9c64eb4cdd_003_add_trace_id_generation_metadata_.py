"""003_add_trace_id_generation_metadata_retry_count_last_error_columns

Revision ID: 8a9c64eb4cdd
Revises: f3098294bd28
Create Date: 2025-07-25 23:39:41.633313

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a9c64eb4cdd'
down_revision: Union[str, Sequence[str], None] = 'f3098294bd28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add trace_id, generation_metadata, retry_count, last_error columns to invoices table."""
    # Add trace_id column for request correlation (FR-9)
    op.add_column('invoices', sa.Column('trace_id', sa.String(64), nullable=True))
    op.create_index('idx_invoice_trace_id', 'invoices', ['trace_id'])
    
    # Add generation_metadata column for debugging context (FR-9)
    op.add_column('invoices', sa.Column('generation_metadata', sa.JSON, nullable=True))
    
    # Add retry_count column for tracking retry attempts (FR-9)
    op.add_column('invoices', sa.Column('retry_count', sa.Integer, nullable=False, server_default='0'))
    
    # Add last_error column for error tracking (FR-9)
    op.add_column('invoices', sa.Column('last_error', sa.Text, nullable=True))
    
    # Add tenant_id column for multi-tenant support (FR-7)
    op.add_column('invoices', sa.Column('tenant_id', sa.String(50), nullable=False, server_default='default'))
    op.create_index('idx_invoice_tenant_id', 'invoices', ['tenant_id'])
    
    # Add composite unique constraint for invoice_number + tenant_id (FR-7)
    # First drop the existing unique constraint on invoice_number
    op.drop_constraint('invoices_invoice_number_key', 'invoices', type_='unique')
    
    # Add new composite unique constraint
    op.create_unique_constraint('uq_invoice_number_tenant', 'invoices', ['invoice_number', 'tenant_id'])


def downgrade() -> None:
    """Remove trace_id, generation_metadata, retry_count, last_error columns from invoices table."""
    # Drop composite unique constraint
    op.drop_constraint('uq_invoice_number_tenant', 'invoices', type_='unique')
    
    # Restore original unique constraint on invoice_number
    op.create_unique_constraint('invoices_invoice_number_key', 'invoices', ['invoice_number'])
    
    # Drop indexes
    op.drop_index('idx_invoice_tenant_id', 'invoices')
    op.drop_index('idx_invoice_trace_id', 'invoices')
    
    # Drop columns
    op.drop_column('invoices', 'tenant_id')
    op.drop_column('invoices', 'last_error')
    op.drop_column('invoices', 'retry_count')
    op.drop_column('invoices', 'generation_metadata')
    op.drop_column('invoices', 'trace_id')
