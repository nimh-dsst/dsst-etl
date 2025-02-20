"""Add Identifier table

Revision ID: 0b2196c1c66b
Revises: 52101c205c9d
Create Date: 2024-12-24 14:22:25.117856

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b2196c1c66b'
down_revision: Union[str, None] = '52101c205c9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('identifier',
    sa.Column('core_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('pmid', sa.Integer(), nullable=True),
    sa.Column('pmcid', sa.String(), nullable=True),
    sa.Column('doi', sa.String(), nullable=True),
    sa.Column('document_id', sa.Integer(), nullable=False),
    sa.Column('provenance_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], name=op.f('fk_identifier_document_id_documents')),
    sa.ForeignKeyConstraint(['provenance_id'], ['provenance.id'], name=op.f('fk_identifier_provenance_id_provenance')),
    sa.PrimaryKeyConstraint('core_id', name=op.f('pk_identifier'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('identifier')
    # ### end Alembic commands ###
