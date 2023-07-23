"""empty message

Revision ID: c1676adfbbad
Revises: 38d98faccb70
Create Date: 2023-07-02 10:42:59.529625

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c1676adfbbad"
down_revision = "38d98faccb70"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("instrument", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("description", sa.String(length=128), nullable=False)
        )
        batch_op.drop_column("name")

    with op.batch_alter_table("musical_interest", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("description", sa.String(length=128), nullable=False)
        )
        batch_op.drop_column("value")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("musical_interest", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "value", sa.VARCHAR(length=128), autoincrement=False, nullable=False
            )
        )
        batch_op.drop_column("description")

    with op.batch_alter_table("instrument", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "name", sa.VARCHAR(length=128), autoincrement=False, nullable=False
            )
        )
        batch_op.drop_column("description")

    # ### end Alembic commands ###
