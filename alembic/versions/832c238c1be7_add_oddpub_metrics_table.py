"""add oddpub_metrics table

Revision ID: 832c238c1be7
Revises: 52101c205c9d
Create Date: 2024-12-11 15:18:24.714630

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '832c238c1be7'
down_revision: Union[str, None] = '52101c205c9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('oddpub_metrics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('article', sa.String(), nullable=False),
    sa.Column('is_open_data', sa.Boolean(), nullable=False),
    sa.Column('open_data_category', sa.String(), nullable=True),
    sa.Column('is_reuse', sa.Boolean(), nullable=False),
    sa.Column('is_open_code', sa.Boolean(), nullable=False),
    sa.Column('is_open_data_das', sa.Boolean(), nullable=False),
    sa.Column('is_open_code_cas', sa.Boolean(), nullable=False),
    sa.Column('das', sa.String(), nullable=True),
    sa.Column('open_data_statements', sa.String(), nullable=True),
    sa.Column('cas', sa.String(), nullable=True),
    sa.Column('open_code_statements', sa.String(), nullable=True),
    sa.Column('work_id', sa.Integer(), nullable=True),
    sa.Column('provenance_id', sa.Integer(), nullable=True),
    sa.Column('document_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], name=op.f('fk_oddpub_metrics_document_id_documents')),
    sa.ForeignKeyConstraint(['provenance_id'], ['provenance.id'], name=op.f('fk_oddpub_metrics_provenance_id_provenance')),
    sa.ForeignKeyConstraint(['work_id'], ['works.id'], name=op.f('fk_oddpub_metrics_work_id_works')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_oddpub_metrics'))
    )
    op.create_index(op.f('ix_oddpub_metrics_article'), 'oddpub_metrics', ['article'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_oddpub_metrics_article'), table_name='oddpub_metrics')
    op.drop_table('oddpub_metrics')
    # ### end Alembic commands ###
