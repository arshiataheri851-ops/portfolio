"""Create tenant-scoped RoutePilot operational tables."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0002_routepilot_data"
down_revision = "0001_identity"
branch_labels = None
depends_on = None


def _has_table(name):
    return inspect(op.get_bind()).has_table(name)


def _has_column(table, column):
    return column in {c["name"] for c in inspect(op.get_bind()).get_columns(table)}


def upgrade():
    if not _has_table("vehicles"):
        op.create_table(
            "vehicles",
            sa.Column("id", sa.String(80), primary_key=True),
            sa.Column("label", sa.String(120), nullable=False),
            sa.Column("status", sa.String(32), nullable=False, server_default="idle"),
            sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        )
    elif not _has_column("vehicles", "organization_id"):
        op.add_column("vehicles", sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=True))

    if not _has_table("positions"):
        op.create_table(
            "positions",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("vehicle_id", sa.String(80), sa.ForeignKey("vehicles.id"), nullable=False),
            sa.Column("latitude", sa.Float(), nullable=False),
            sa.Column("longitude", sa.Float(), nullable=False),
            sa.Column("recorded_at", sa.String(40), nullable=False),
            sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        )
    elif not _has_column("positions", "organization_id"):
        op.add_column("positions", sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=True))

    if not _has_table("deliveries"):
        op.create_table(
            "deliveries",
            sa.Column("id", sa.String(80), primary_key=True),
            sa.Column("recipient", sa.String(120), nullable=False),
            sa.Column("address", sa.String(240), nullable=False),
            sa.Column("route_id", sa.String(80), nullable=False),
            sa.Column("vehicle_id", sa.String(80), sa.ForeignKey("vehicles.id"), nullable=True),
            sa.Column("status", sa.String(32), nullable=False, server_default="scheduled"),
            sa.Column("eta", sa.String(40)),
            sa.Column("created_at", sa.String(40), nullable=False),
            sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        )
    elif not _has_column("deliveries", "organization_id"):
        op.add_column("deliveries", sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=True))

    if not _has_table("proofs"):
        op.create_table(
            "proofs",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("delivery_id", sa.String(80), sa.ForeignKey("deliveries.id"), nullable=False),
            sa.Column("recipient_name", sa.String(120), nullable=False),
            sa.Column("method", sa.String(32), nullable=False),
            sa.Column("note", sa.Text(), nullable=False, server_default=""),
            sa.Column("captured_at", sa.String(40), nullable=False),
            sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        )
    elif not _has_column("proofs", "organization_id"):
        op.add_column("proofs", sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=True))

    for table in ("vehicles", "positions", "deliveries", "proofs"):
        op.create_index("ix_" + table + "_organization_id", table, ["organization_id"], if_not_exists=True)


def downgrade():
    for table in ("proofs", "deliveries", "positions", "vehicles"):
        if _has_table(table):
            op.drop_index("ix_" + table + "_organization_id", table_name=table, if_exists=True)
            # Operational tables predate this migration in SQLite installations;
            # do not drop them during downgrade.
            if table in {"proofs", "deliveries", "positions", "vehicles"}:
                pass
