"""Create tenant-scoped SignalDesk operational tables."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0002_signaldesk_data"
down_revision = "0001_identity"
branch_labels = None
depends_on = None


def _has_table(name):
    return inspect(op.get_bind()).has_table(name)


def _has_column(table, column):
    return column in {c["name"] for c in inspect(op.get_bind()).get_columns(table)}


def upgrade():
    if not _has_table("tickets"):
        op.create_table(
            "tickets",
            sa.Column("id", sa.String(80), primary_key=True),
            sa.Column("title", sa.String(200), nullable=False),
            sa.Column("queue", sa.String(80), nullable=False),
            sa.Column("account_tier", sa.String(32), nullable=False),
            sa.Column("priority", sa.String(16), nullable=False),
            sa.Column("status", sa.String(24), nullable=False, server_default="open"),
            sa.Column("assignee", sa.String(120)),
            sa.Column("created_at", sa.String(40), nullable=False),
            sa.Column("due_at", sa.String(40), nullable=False),
            sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        )
    elif not _has_column("tickets", "organization_id"):
        op.add_column("tickets", sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=True))

    if not _has_table("ticket_events"):
        op.create_table(
            "ticket_events",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("ticket_id", sa.String(80), sa.ForeignKey("tickets.id"), nullable=False),
            sa.Column("event_type", sa.String(40), nullable=False),
            sa.Column("actor", sa.String(320), nullable=False),
            sa.Column("details", sa.Text(), nullable=False),
            sa.Column("created_at", sa.String(40), nullable=False),
            sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        )
    elif not _has_column("ticket_events", "organization_id"):
        op.add_column("ticket_events", sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=True))

    for table in ("tickets", "ticket_events"):
        op.create_index("ix_" + table + "_organization_id", table, ["organization_id"], if_not_exists=True)


def downgrade():
    for table in ("ticket_events", "tickets"):
        if _has_table(table):
            op.drop_index("ix_" + table + "_organization_id", table_name=table, if_exists=True)
