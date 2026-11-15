"""Create organization and user identity tables."""
from alembic import op
import sqlalchemy as sa

revision = "0001_identity"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False, unique=True),
        sa.Column("created_at", sa.String(length=40), nullable=False),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("organization_id", sa.String(length=36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("active", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.String(length=40), nullable=False),
        sa.UniqueConstraint("organization_id", "email", name="uq_users_org_email"),
        sa.CheckConstraint("role IN ('admin','manager','agent','dispatcher','driver','viewer')", name="ck_users_role"),
    )
    op.create_index("ix_users_email", "users", ["email"])

def downgrade():
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_table("organizations")
