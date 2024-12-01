"""relations between tables

Revision ID: f71ed5b12236
Revises: a30bce12cb1f
Create Date: 2024-11-29 13:22:04.841210

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f71ed5b12236'
down_revision: Union[str, None] = 'a30bce12cb1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('analysis', schema=None) as batch_op:
        batch_op.add_column(sa.Column('results', sa.JSON(), nullable=False))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False))

    with op.batch_alter_table('data', schema=None) as batch_op:
        batch_op.add_column(sa.Column('extension', sa.String(), nullable=False))
        batch_op.add_column(sa.Column('original_name', sa.String(), nullable=False))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False))

    with op.batch_alter_table('prediction', schema=None) as batch_op:
        batch_op.add_column(sa.Column('results', sa.JSON(), nullable=False))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False))

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('prediction', schema=None) as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('results')

    with op.batch_alter_table('data', schema=None) as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('original_name')
        batch_op.drop_column('extension')

    with op.batch_alter_table('analysis', schema=None) as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('results')

    # ### end Alembic commands ###
