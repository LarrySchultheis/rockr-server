"""empty message

Revision ID: 38d2c698add5
Revises: e4ea06fdf5c8
Create Date: 2023-07-22 10:20:00.451969

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "38d2c698add5"
down_revision = "e4ea06fdf5c8"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("message", schema=None) as batch_op:
        batch_op.drop_column("user_message_group_id")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("message", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "user_message_group_id",
                sa.INTEGER(),
                autoincrement=False,
                nullable=True,
            )
        )

    # ### end Alembic commands ###
