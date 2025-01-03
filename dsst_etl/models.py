from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
# Apply the naming convention to the metadata
metadata = MetaData(naming_convention=naming_convention)
Base = declarative_base(metadata=metadata)


class Works(Base):
    __tablename__ = "works"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())
    initial_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    primary_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    provenance_id = Column(Integer, ForeignKey("provenance.id"))


class Documents(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    hash_data = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=func.now())
    s3uri = Column(Text, nullable=False)
    provenance_id = Column(Integer, ForeignKey("provenance.id"))


class Provenance(Base):
    __tablename__ = "provenance"

    id = Column(Integer, primary_key=True)
    pipeline_name = Column(String(255))
    version = Column(String(50))
    compute = Column(Text)
    personnel = Column(Text)
    comment = Column(Text)


class RTransparentPublication(Base):
    __tablename__ = "rtransparent_publication"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)

    # Mandatory fields
    is_open_code = Column(Boolean, nullable=True)
    is_open_data = Column(Boolean, nullable=True)

    # Optional fields
    year = Column(Integer, nullable=True)
    filename = Column(String, nullable=True)
    pmcid_pmc = Column(Integer, nullable=True)
    pmid = Column(Integer, nullable=True)
    doi = Column(String, nullable=True)
    year_epub = Column(Integer, nullable=True)
    year_ppub = Column(Integer, nullable=True)
    journal = Column(String, nullable=True)
    publisher = Column(String, nullable=True)
    affiliation_country = Column(String, nullable=True)
    affiliation_institution = Column(String, nullable=True)
    type = Column(String, nullable=True)
    data_text = Column(String, nullable=True)  # Assuming LongStr is a long text
    is_relevant_data = Column(Boolean, nullable=True)
    com_specific_db = Column(String, nullable=True)
    com_general_db = Column(String, nullable=True)
    com_github_data = Column(String, nullable=True)
    dataset = Column(String, nullable=True)
    com_file_formats = Column(String, nullable=True)
    com_supplemental_data = Column(String, nullable=True)
    com_data_availibility = Column(String, nullable=True)
    code_text = Column(String, nullable=True)  # Assuming LongStr is a long text
    is_relevant_code = Column(Boolean, nullable=True)
    com_code = Column(String, nullable=True)
    com_suppl_code = Column(String, nullable=True)
    is_coi_pred = Column(Boolean, nullable=True)
    coi_text = Column(String, nullable=True)  # Assuming LongStr is a long text
    is_coi_pmc_fn = Column(Boolean, nullable=True)
    is_coi_pmc_title = Column(Boolean, nullable=True)
    is_relevant_coi = Column(Boolean, nullable=True)
    is_relevant_coi_hi = Column(Boolean, nullable=True)
    is_relevant_coi_lo = Column(Boolean, nullable=True)
    is_explicit_coi = Column(Boolean, nullable=True)
    coi_1 = Column(Boolean, nullable=True)
    coi_2 = Column(Boolean, nullable=True)
    coi_disclosure_1 = Column(Boolean, nullable=True)
    commercial_1 = Column(Boolean, nullable=True)
    benefit_1 = Column(Boolean, nullable=True)
    consultant_1 = Column(Boolean, nullable=True)
    grants_1 = Column(Boolean, nullable=True)
    brief_1 = Column(Boolean, nullable=True)
    fees_1 = Column(Boolean, nullable=True)
    consults_1 = Column(Boolean, nullable=True)
    connect_1 = Column(Boolean, nullable=True)
    connect_2 = Column(Boolean, nullable=True)
    commercial_ack_1 = Column(Boolean, nullable=True)
    rights_1 = Column(Boolean, nullable=True)
    founder_1 = Column(Boolean, nullable=True)
    advisor_1 = Column(Boolean, nullable=True)
    paid_1 = Column(Boolean, nullable=True)
    board_1 = Column(Boolean, nullable=True)
    no_coi_1 = Column(Boolean, nullable=True)
    no_funder_role_1 = Column(Boolean, nullable=True)
    fund_text = Column(String, nullable=True)  # Assuming LongStr is a long text
    fund_pmc_institute = Column(String, nullable=True)
    fund_pmc_source = Column(String, nullable=True)
    fund_pmc_anysource = Column(String, nullable=True)
    is_fund_pmc_group = Column(Boolean, nullable=True)
    is_fund_pmc_title = Column(Boolean, nullable=True)
    is_fund_pmc_anysource = Column(Boolean, nullable=True)
    is_relevant_fund = Column(Boolean, nullable=True)
    is_explicit_fund = Column(Boolean, nullable=True)
    support_1 = Column(Boolean, nullable=True)
    support_3 = Column(Boolean, nullable=True)
    support_4 = Column(Boolean, nullable=True)
    support_5 = Column(Boolean, nullable=True)
    support_6 = Column(Boolean, nullable=True)
    support_7 = Column(Boolean, nullable=True)
    support_8 = Column(Boolean, nullable=True)
    support_9 = Column(Boolean, nullable=True)
    support_10 = Column(Boolean, nullable=True)
    developed_1 = Column(Boolean, nullable=True)
    received_1 = Column(Boolean, nullable=True)
    received_2 = Column(Boolean, nullable=True)
    recipient_1 = Column(Boolean, nullable=True)
    authors_1 = Column(Boolean, nullable=True)
    authors_2 = Column(Boolean, nullable=True)
    thank_1 = Column(Boolean, nullable=True)
    thank_2 = Column(Boolean, nullable=True)
    fund_1 = Column(Boolean, nullable=True)
    fund_2 = Column(Boolean, nullable=True)
    fund_3 = Column(Boolean, nullable=True)
    supported_1 = Column(Boolean, nullable=True)
    financial_1 = Column(Boolean, nullable=True)
    financial_2 = Column(Boolean, nullable=True)
    financial_3 = Column(Boolean, nullable=True)
    grant_1 = Column(Boolean, nullable=True)
    french_1 = Column(Boolean, nullable=True)
    common_1 = Column(Boolean, nullable=True)
    common_2 = Column(Boolean, nullable=True)
    common_3 = Column(Boolean, nullable=True)
    common_4 = Column(Boolean, nullable=True)
    common_5 = Column(Boolean, nullable=True)
    acknow_1 = Column(Boolean, nullable=True)
    disclosure_1 = Column(Boolean, nullable=True)
    disclosure_2 = Column(Boolean, nullable=True)
    fund_ack = Column(Boolean, nullable=True)
    project_ack = Column(Boolean, nullable=True)
    is_register_pred = Column(Boolean, nullable=True)
    register_text = Column(String, nullable=True)  # Assuming LongStr is a long text
    is_research = Column(Boolean, nullable=True)
    is_review = Column(Boolean, nullable=True)
    is_reg_pmc_title = Column(Boolean, nullable=True)
    is_relevant_reg = Column(Boolean, nullable=True)
    is_method = Column(Boolean, nullable=True)
    is_NCT = Column(Boolean, nullable=True)
    is_explicit_reg = Column(Boolean, nullable=True)
    prospero_1 = Column(Boolean, nullable=True)
    registered_1 = Column(Boolean, nullable=True)
    registered_2 = Column(Boolean, nullable=True)
    registered_3 = Column(Boolean, nullable=True)
    registered_4 = Column(Boolean, nullable=True)
    registered_5 = Column(Boolean, nullable=True)
    not_registered_1 = Column(Boolean, nullable=True)
    registration_1 = Column(Boolean, nullable=True)
    registration_2 = Column(Boolean, nullable=True)
    registration_3 = Column(Boolean, nullable=True)
    registration_4 = Column(Boolean, nullable=True)
    registry_1 = Column(Boolean, nullable=True)
    reg_title_1 = Column(Boolean, nullable=True)
    reg_title_2 = Column(Boolean, nullable=True)
    reg_title_3 = Column(Boolean, nullable=True)
    reg_title_4 = Column(Boolean, nullable=True)
    funded_ct_1 = Column(Boolean, nullable=True)
    ct_2 = Column(Boolean, nullable=True)
    ct_3 = Column(Boolean, nullable=True)
    protocol_1 = Column(Boolean, nullable=True)
    is_success = Column(Boolean, nullable=True)
    is_art = Column(Boolean, nullable=True)
    field = Column(String, nullable=True)
    score = Column(Float, nullable=True)
    jif = Column(Float, nullable=True)
    eigenfactor_score = Column(Float, nullable=True)
    n_cite = Column(Float, nullable=True)

    # Extra fields
    affiliation_aff_id = Column(String, nullable=True)
    affiliation_all = Column(String, nullable=True)
    article = Column(String, nullable=True)
    author = Column(String, nullable=True)
    author_aff_id = Column(String, nullable=True)
    correspondence = Column(String, nullable=True)
    date_epub = Column(String, nullable=True)
    date_ppub = Column(String, nullable=True)
    funding_text = Column(String, nullable=True)  # Assuming LongStr is a long text
    is_explicit = Column(Boolean, nullable=True)
    is_fund_pred = Column(Boolean, nullable=True)
    is_funded_pred = Column(Boolean, nullable=True)
    is_relevant = Column(Boolean, nullable=True)
    is_supplement = Column(Boolean, nullable=True)
    issn_epub = Column(String, nullable=True)
    issn_ppub = Column(String, nullable=True)
    journal_iso = Column(String, nullable=True)
    journal_nlm = Column(String, nullable=True)
    license = Column(String, nullable=True)
    n_affiliation = Column(String, nullable=True)
    n_auth = Column(String, nullable=True)
    n_fig_body = Column(String, nullable=True)
    n_fig_floats = Column(String, nullable=True)
    n_ref = Column(String, nullable=True)
    n_table_body = Column(String, nullable=True)
    n_table_floats = Column(String, nullable=True)
    open_code_statements = Column(
        String, nullable=True
    )  # Assuming LongStr is a long text
    open_data_category = Column(
        String, nullable=True
    )  # Assuming LongStr is a long text
    open_data_statements = Column(
        String, nullable=True
    )  # Assuming LongStr is a long text
    pii = Column(String, nullable=True)
    pmcid_uid = Column(String, nullable=True)
    publisher_id = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    title = Column(String, nullable=True)
    is_data_pred = Column(Boolean, nullable=True)
    is_code_pred = Column(Boolean, nullable=True)
    funder = Column(String, nullable=True)

    work_id = Column(Integer, ForeignKey("works.id"), nullable=True)
    provenance_id = Column(Integer, ForeignKey("provenance.id"), nullable=True)


class Identifier(Base):
    __tablename__ = "identifier"

    core_id = Column(Integer, primary_key=True, autoincrement=True)
    pmid = Column(Integer, nullable=True)
    pmcid = Column(String, nullable=True)
    doi = Column(String, nullable=True)
    document_id = Column(ForeignKey("documents.id"), nullable=False)
    provenance_id = Column(ForeignKey("provenance.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())


class OddpubMetrics(Base):
    __tablename__ = "oddpub_metrics"

    id = Column(Integer, primary_key=True)
    article = Column(String, unique=True, nullable=True, index=True)
    is_open_data = Column(Boolean, nullable=True, default=False)
    open_data_category = Column(String)
    is_reuse = Column(Boolean, nullable=True, default=False)
    is_open_code = Column(Boolean, nullable=True, default=False)
    is_open_data_das = Column(Boolean, nullable=True, default=False)
    is_open_code_cas = Column(Boolean, nullable=True, default=False)
    das = Column(String)
    open_data_statements = Column(String)
    cas = Column(String)
    open_code_statements = Column(String)
    work_id = Column(Integer, ForeignKey("works.id"), nullable=True)
    provenance_id = Column(Integer, ForeignKey("provenance.id"), nullable=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
