"""Add DataFile table for storing text files with image data and labels

Revision ID: 20240101000001
Revises: bcdac2010f33
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20240101000001'
down_revision: Union[str, None] = 'bcdac2010f33'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create DataFile table
    op.create_table('data_files',
        sa.Column('file_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('dataset_id', sa.Integer(), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('cloud_id', sa.String(length=255), nullable=False),
        sa.Column('cloud_url', sa.String(length=500), nullable=False),
        sa.Column('content_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.dataset_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('file_id'),
        sa.UniqueConstraint('cloud_id')
    )
    
    # Create indexes for better query performance
    op.create_index('idx_data_files_dataset_id', 'data_files', ['dataset_id'])
    op.create_index('idx_data_files_uploaded_by', 'data_files', ['uploaded_by'])
    op.create_index('idx_data_files_content_type', 'data_files', ['content_type'])
    op.create_index('idx_data_files_is_public', 'data_files', ['is_public'])
    op.create_index('idx_data_files_created_at', 'data_files', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_data_files_created_at')
    op.drop_index('idx_data_files_is_public')
    op.drop_index('idx_data_files_content_type')
    op.drop_index('idx_data_files_uploaded_by')
    op.drop_index('idx_data_files_dataset_id')
    
    # Drop table
    op.drop_table('data_files')
