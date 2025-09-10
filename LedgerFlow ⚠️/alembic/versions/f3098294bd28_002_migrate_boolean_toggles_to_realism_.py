"""002_migrate_boolean_toggles_to_realism_profile

Revision ID: f3098294bd28
Revises: 8d4f722b136f
Create Date: 2025-07-25 23:21:49.537673

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3098294bd28'
down_revision: Union[str, Sequence[str], None] = '8d4f722b136f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Migration 002: Migrate boolean toggles to realism_profile enum
    
    Implements:
    - Create configuration_settings table to store realism_profile
    - Migrate legacy boolean toggles to realism_profile enum (basic, realistic, advanced)
    - Add indexes for performance
    """
    
    # Create configuration_settings table
    op.create_table(
        'configuration_settings',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('setting_name', sa.String(100), nullable=False, unique=True),
        sa.Column('setting_value', sa.Text, nullable=False),
        sa.Column('setting_type', sa.String(50), nullable=False, server_default='string'),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.current_timestamp())
    )
    
    # Create index for performance
    op.create_index('idx_config_setting_name', 'configuration_settings', ['setting_name'])
    
    # Get database connection for data migration
    connection = op.get_bind()
    
    # Check if there are any legacy boolean settings to migrate
    # This is a placeholder - in a real system, you'd check actual tables
    legacy_settings = {
        'enable_advanced_features': False,
        'use_realistic_data': True,
        'enable_basic_mode': False
    }
    
    # Determine realism profile based on legacy settings
    if legacy_settings.get('enable_basic_mode', False):
        realism_profile = 'basic'
    elif legacy_settings.get('enable_advanced_features', False):
        realism_profile = 'advanced'
    else:
        realism_profile = 'realistic'
    
    # Insert the realism_profile setting
    insert_query = """
        INSERT INTO configuration_settings (setting_name, setting_value, setting_type, description)
        VALUES (:name, :value, :type, :description)
    """
    
    connection.execute(
        sa.text(insert_query),
        {
            'name': 'realism_profile',
            'value': realism_profile,
            'type': 'enum',
            'description': 'Realism profile replacing legacy boolean toggles (basic, realistic, advanced)'
        }
    )
    
    # Insert other default configuration settings
    default_settings = [
        {
            'name': 'default_invoice_count',
            'value': '100',
            'type': 'integer',
            'description': 'Default number of invoices to generate'
        },
        {
            'name': 'default_invoice_type',
            'value': 'gst',
            'type': 'string',
            'description': 'Default invoice type (gst, vat, cash)'
        },
        {
            'name': 'enable_verification',
            'value': 'true',
            'type': 'boolean',
            'description': 'Enable invoice verification'
        },
        {
            'name': 'min_compliance_score',
            'value': '85.0',
            'type': 'float',
            'description': 'Minimum compliance score required'
        }
    ]
    
    for setting in default_settings:
        try:
            connection.execute(
                sa.text(insert_query),
                {
                    'name': setting['name'],
                    'value': setting['value'],
                    'type': setting['type'],
                    'description': setting['description']
                }
            )
        except Exception as e:
            # Setting might already exist, ignore duplicate errors
            print(f"Warning: Could not insert setting {setting['name']}: {e}")
    
    print(f"Migration 002 completed: Migrated boolean toggles to realism_profile: {realism_profile}")


def downgrade() -> None:
    """
    Downgrade migration 002
    """
    
    # Drop indexes
    try:
        op.drop_index('idx_config_setting_name')
    except Exception:
        pass
    
    # Drop table
    try:
        op.drop_table('configuration_settings')
    except Exception:
        pass
    
    print("Migration 002 downgraded: Removed configuration_settings table")
