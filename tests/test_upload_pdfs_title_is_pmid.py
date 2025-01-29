from unittest.mock import MagicMock, patch
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dsst_etl.models import Documents, Identifier, OddpubMetrics, Works, Base
from dsst_etl.upload_pdfs_title_is_pmid import DocumentInventoryPMID
import boto3
from botocore.config import Config


@pytest.fixture(params=['mock', 'minio'])
def s3_client(request):
    if request.param == 'mock':
        # Create a mock S3 client
        mock_client = MagicMock()
        
        # Set up default mock behaviors
        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [{'Contents': [{'Key': '12345678.pdf'}]}]
        mock_client.get_paginator.return_value = mock_paginator
        
        mock_body = MagicMock()
        mock_body.read.return_value = b'test content'
        mock_client.get_object.return_value = {'Body': mock_body}
        
        return mock_client
    else:
        # Return real MinIO client
        return boto3.client(
            's3',
            endpoint_url='http://localhost:9000',
            aws_access_key_id='minioadmin',
            aws_secret_access_key='minioadmin',
            region_name='us-east-1',
            config=Config(signature_version='s3v4')
        )


@pytest.fixture
def db_session():
    # Create an in-memory SQLite database for testing
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    session = Session(engine)
    yield session
    session.close()


@pytest.fixture
def uploader(db_session, s3_client):
    with patch('dsst_etl.upload_pdfs_title_is_pmid.get_bucket_name') as mock_get_bucket_name:
        mock_get_bucket_name.return_value = 'dsst-pdfs'
        
        # Initialize the class with the session
        uploader = DocumentInventoryPMID(db_session, oddpub_host_api='http://mock-api:8071')
        # Override the S3 client
        uploader.s3_client = s3_client

        # For MinIO, ensure test file exists
        if not isinstance(s3_client, MagicMock):
            try:
                s3_client.head_bucket(Bucket='dsst-pdfs')
            except:
                s3_client.create_bucket(Bucket='dsst-pdfs')
            s3_client.put_object(
                Bucket='dsst-pdfs',
                Key='12345678.pdf',
                Body=b'test content'
            )
        
        return uploader


@patch('requests.post')
def test_process_s3_inventory_success(mock_post, uploader, db_session):
    # Mock the POST request
    def mock_post_side_effect(url, *args, **kwargs):
        if url == 'http://mock-api:8071/oddpub':
            mock_response = MagicMock()
            mock_response.json.return_value = {
               'article': 'test1.txt', 
                'is_open_data': False, 
                'open_data_category': '', 
                'is_reuse': False, 
                'is_open_code': False, 
                'is_open_data_das': False, 
                'is_open_code_cas': False, 
                'das': None, 
                'open_data_statements': '', 
                'cas': None, 
                'open_code_statements': ''
            }
            mock_response.status_code = 200
            return mock_response
        else:
            raise ValueError(f"Unexpected URL: {url}")

    mock_post.side_effect = mock_post_side_effect

    # Run the method
    uploader.run()

    # Assertions
    assert db_session.query(Documents).count() == 1, "Documents table should have 1 row"
    assert db_session.query(Identifier).count() == 1, "Identifier table should have 1 row"
    assert db_session.query(Works).count() == 1, "Works table should have 1 row"
    assert db_session.query(OddpubMetrics).count() == 1, "OddpubMetrics table should have 1 row"

    # Check that the POST request was made to the correct URL
    mock_post.assert_called_with(
        'http://mock-api:8071/oddpub',
        files={'file': b'test content'}
    )


def test_process_s3_inventory_failure(uploader, db_session, s3_client):
    if isinstance(s3_client, MagicMock):
        # For mock client, force an exception
        s3_client.get_paginator.side_effect = Exception("Test exception")
    else:
        # For MinIO client, use an invalid bucket to force failure
        uploader.s3_client = boto3.client(
            's3',
            endpoint_url='http://localhost:9000',
            aws_access_key_id='invalid',
            aws_secret_access_key='invalid',
            region_name='us-east-1',
            config=Config(signature_version='s3v4')
        )

    with patch('dsst_etl.upload_pdfs_title_is_pmid.logger') as mock_logger:
        # Run the method
        uploader.run()

        # Assertions
        mock_logger.error.assert_called()  # Just verify error was logged
        assert db_session.query(Documents).count() == 0
        assert db_session.query(Identifier).count() == 0
        assert db_session.query(Works).count() == 0
        assert db_session.query(OddpubMetrics).count() == 0