"""001_add_invoice_constraints_and_sequences

Revision ID: 74de654889e9
Revises: 
Create Date: 2025-07-25 22:37:38.219333

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '74de654889e9'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Migration 001: Add invoice constraints and sequences
    
    Implements:
    - Composite unique constraints (invoice_number, tenant_id) for multi-tenant support
    - Database sequences for atomic counter operations
    - Invoice number reservation table
    - Duplicate scan and fix for existing data
    """
    
    # Add tenant_id column to invoices table if it doesn't exist
    try:
        op.add_column('invoices', sa.Column('tenant_id', sa.String(50), nullable=False, server_default='default'))
    except Exception:
        # Column might already exist, ignore error
        pass
    
    # Add trace_id column for request correlation (FR-9 requirement)
    try:
        op.add_column('invoices', sa.Column('trace_id', sa.String(64), nullable=True))
        op.create_index('idx_invoice_trace_id', 'invoices', ['trace_id'])
    except Exception:
        # Column might already exist, ignore error
        pass
    
    # Add generation_metadata column for debugging (FR-9 requirement)
    try:
        op.add_column('invoices', sa.Column('generation_metadata', sa.JSON, nullable=True))
    except Exception:
        # Column might already exist, ignore error
        pass
    
    # Add retry_count and last_error columns (FR-9 requirement)
    try:
        op.add_column('invoices', sa.Column('retry_count', sa.Integer, nullable=False, server_default='0'))
        op.add_column('invoices', sa.Column('last_error', sa.Text, nullable=True))
    except Exception:
        # Columns might already exist, ignore error
        pass
    
    # Scan for duplicate invoice numbers and fix them
    connection = op.get_bind()
    
    # Find duplicates
    duplicates_query = """
        SELECT invoice_number, COUNT(*) as count 
        FROM invoices 
        GROUP BY invoice_number 
        HAVING COUNT(*) > 1
    """
    
    duplicates = connection.execute(sa.text(duplicates_query)).fetchall()
    
    if duplicates:
        print(f"Found {len(duplicates)} duplicate invoice number groups. Fixing...")
        
        for duplicate in duplicates:
            invoice_number = duplicate[0]
            
            # Get all invoices with this number
            invoices_query = """
                SELECT id, invoice_number, created_at 
                FROM invoices 
                WHERE invoice_number = :invoice_number 
                ORDER BY created_at ASC
            """
            
            invoices = connection.execute(
                sa.text(invoices_query), 
                {'invoice_number': invoice_number}
            ).fetchall()
            
            # Keep the first one, rename the others
            for i, invoice in enumerate(invoices[1:], start=1):
                new_number = f"{invoice_number}_DUP_{i}"
                
                update_query = """
                    UPDATE invoices 
                    SET invoice_number = :new_number 
                    WHERE id = :invoice_id
                """
                
                connection.execute(
                    sa.text(update_query),
                    {'new_number': new_number, 'invoice_id': invoice[0]}
                )
                
                print(f"Renamed duplicate invoice {invoice[0]} from {invoice_number} to {new_number}")
    
    # Add composite unique constraint (invoice_number, tenant_id)
    try:
        op.create_unique_constraint(
            'uq_invoice_number_tenant',
            'invoices',
            ['invoice_number', 'tenant_id']
        )
    except Exception as e:
        print(f"Warning: Could not create unique constraint: {e}")
    
    # Create invoice sequences table for SQLite compatibility
    op.create_table(
        'invoice_sequences',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('sequence_name', sa.String(100), nullable=False, unique=True),
        sa.Column('current_value', sa.Integer, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.current_timestamp())
    )
    
    # Create invoice number reservations table
    op.create_table(
        'invoice_number_reservations',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('invoice_number', sa.String(50), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False),
        sa.Column('reserved_at', sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='reserved')
    )
    
    # Create indexes for performance
    op.create_index('idx_reservations_expires', 'invoice_number_reservations', ['expires_at'])
    op.create_index('idx_reservations_tenant', 'invoice_number_reservations', ['tenant_id'])
    op.create_index('idx_reservations_number_tenant', 'invoice_number_reservations', ['invoice_number', 'tenant_id'])
    
    # Create index on invoice batch_id for performance
    try:
        op.create_index('idx_invoice_batch_id', 'invoices', ['generation_batch_id'])
    except Exception:
        # Index might already exist or column might not exist
        pass
    
    print("Migration 001 completed: Added invoice constraints and sequences")


def downgrade() -> None:
    """
    Downgrade migration 001
    """
    
    # Drop indexes
    try:
        op.drop_index('idx_reservations_expires')
        op.drop_index('idx_reservations_tenant') 
        op.drop_index('idx_reservations_number_tenant')
        op.drop_index('idx_invoice_trace_id')
        op.drop_index('idx_invoice_batch_id')
    except Exception:
        pass
    
    # Drop tables
    try:
        op.drop_table('invoice_number_reservations')
        op.drop_table('invoice_sequences')
    except Exception:
        pass
    
    # Drop unique constraint
    try:
        op.drop_constraint('uq_invoice_number_tenant', 'invoices', type_='unique')
    except Exception:
        pass
    
    # Drop columns (be careful with data loss)
    try:
        op.drop_column('invoices', 'tenant_id')
        op.drop_column('invoices', 'trace_id')
        op.drop_column('invoices', 'generation_metadata')
        op.drop_column('invoices', 'retry_count')
        op.drop_column('invoices', 'last_error')
    except Exception:
        pass
    
    print("Migration 001 downgraded: Removed invoice constraints and sequences")
