"""Add proof document metadata for uploaded delivery evidence."""
from alembic import op
import sqlalchemy as sa

revision = "0003_proof_files"
down_revision = "0002_routepilot_data"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("proofs", sa.Column("storage_key", sa.String(80), nullable=True))
    op.add_column("proofs", sa.Column("original_filename", sa.String(255), nullable=True))
    op.add_column("proofs", sa.Column("content_type", sa.String(120), nullable=True))
    op.add_column("proofs", sa.Column("size_bytes", sa.Integer(), nullable=True))


def downgrade():
    op.drop_column("proofs", "size_bytes")
    op.drop_column("proofs", "content_type")
    op.drop_column("proofs", "original_filename")
    op.drop_column("proofs", "storage_key")
