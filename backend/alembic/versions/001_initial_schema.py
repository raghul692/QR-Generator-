"""initial schema - 12 normalized tables

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-23

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. qr_categories
    op.create_table(
        'qr_categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('color', sa.String(length=20), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('idx_categories_slug', 'qr_categories', ['slug'], unique=False)

    # 2. qr_templates
    op.create_table(
        'qr_templates',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('config_json', sa.Text(), nullable=False),
        sa.Column('is_builtin', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_templates_name', 'qr_templates', ['name'], unique=False)

    # 3. qr_history
    op.create_table(
        'qr_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('qr_type', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('encoded_data', sa.Text(), nullable=True),
        sa.Column('preview_path', sa.String(length=500), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('customization_json', sa.Text(), nullable=True),
        sa.Column('download_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_favorite', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['qr_categories.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['template_id'], ['qr_templates.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_history_category', 'qr_history', ['category_id'], unique=False)
    op.create_index('idx_history_created', 'qr_history', ['created_at'], unique=False)
    op.create_index('idx_history_favorite', 'qr_history', ['is_favorite'], unique=False)
    op.create_index('idx_history_qr_type', 'qr_history', ['qr_type'], unique=False)

    # 4. qr_bulk_jobs
    op.create_table(
        'qr_bulk_jobs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('job_name', sa.String(length=255), nullable=False),
        sa.Column('source_filename', sa.String(length=500), nullable=False),
        sa.Column('total_rows', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('processed_rows', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('qr_type', sa.String(length=50), nullable=False, server_default='url'),
        sa.Column('column_mapping', sa.Text(), nullable=True),
        sa.Column('zip_path', sa.String(length=500), nullable=True),
        sa.Column('error_log', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_bulk_status', 'qr_bulk_jobs', ['status'], unique=False)

    # 5. qr_exports
    op.create_table(
        'qr_exports',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('qr_id', sa.Integer(), nullable=True),
        sa.Column('export_type', sa.String(length=20), nullable=False),
        sa.Column('format', sa.String(length=20), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_size', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['qr_id'], ['qr_history.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_exports_format', 'qr_exports', ['format'], unique=False)
    op.create_index('idx_exports_qr', 'qr_exports', ['qr_id'], unique=False)

    # 6. analytics
    op.create_table(
        'analytics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('metric_type', sa.String(length=50), nullable=False),
        sa.Column('metric_key', sa.String(length=100), nullable=False),
        sa.Column('metric_value', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('metric_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('metric_type', 'metric_key', 'metric_date', name='uq_analytics')
    )
    op.create_index('idx_analytics_date', 'analytics', ['metric_date'], unique=False)
    op.create_index('idx_analytics_type', 'analytics', ['metric_type'], unique=False)

    # 7. settings
    op.create_table(
        'settings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False, server_default='general'),
        sa.Column('data_type', sa.String(length=20), nullable=False, server_default='string'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    op.create_index('idx_settings_category', 'settings', ['category'], unique=False)

    # 8. activity_logs
    op.create_table(
        'activity_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('module', sa.String(length=50), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_activity_action', 'activity_logs', ['action'], unique=False)
    op.create_index('idx_activity_created', 'activity_logs', ['created_at'], unique=False)
    op.create_index('idx_activity_module', 'activity_logs', ['module'], unique=False)

    # 9. backup_logs
    op.create_table(
        'backup_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('backup_type', sa.String(length=20), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_size', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='success'),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_backup_type', 'backup_logs', ['backup_type'], unique=False)

    # 10. dynamic_qrs
    op.create_table(
        'dynamic_qrs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('short_code', sa.String(length=20), nullable=False),
        sa.Column('target_url', sa.Text(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('qr_history_id', sa.Integer(), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('scan_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['qr_history_id'], ['qr_history.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('short_code')
    )
    op.create_index('idx_dynamic_history_id', 'dynamic_qrs', ['qr_history_id'], unique=False)
    op.create_index('idx_dynamic_short_code', 'dynamic_qrs', ['short_code'], unique=False)

    # 11. scan_logs
    op.create_table(
        'scan_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('dynamic_qr_id', sa.Integer(), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('device_type', sa.String(length=50), nullable=True),
        sa.Column('browser', sa.String(length=50), nullable=True),
        sa.Column('referer', sa.String(length=500), nullable=True),
        sa.Column('scanned_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['dynamic_qr_id'], ['dynamic_qrs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_scan_dynamic_id', 'scan_logs', ['dynamic_qr_id'], unique=False)
    op.create_index('idx_scan_scanned_at', 'scan_logs', ['scanned_at'], unique=False)

    # 12. api_keys
    op.create_table(
        'api_keys',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('key_prefix', sa.String(length=10), nullable=False),
        sa.Column('key_hash', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('rate_limit', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key_hash')
    )
    op.create_index('idx_api_keys_hash', 'api_keys', ['key_hash'], unique=False)


def downgrade() -> None:
    op.drop_table('api_keys')
    op.drop_table('scan_logs')
    op.drop_table('dynamic_qrs')
    op.drop_table('backup_logs')
    op.drop_table('activity_logs')
    op.drop_table('settings')
    op.drop_table('analytics')
    op.drop_table('qr_exports')
    op.drop_table('qr_bulk_jobs')
    op.drop_table('qr_history')
    op.drop_table('qr_templates')
    op.drop_table('qr_categories')
