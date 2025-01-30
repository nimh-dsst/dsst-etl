from unittest.mock import MagicMock, patch
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dsst_etl.models import Documents, Identifier, OddpubMetrics, Works, Base
from dsst_etl.inventory_pdfs_pmid import DocumentInventoryPMID
import boto3
from botocore.config import Config
import io
import requests


@pytest.fixture(params=['mock', 'minio'])
def s3_client(request):
    if request.param == 'mock':
        # Create a mock S3 client
        mock_client = MagicMock()
        
        # Set up default mock behaviors
        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [{'Contents': [
            {'Key': 'test1.pdf'},
            {'Key': 'test2.pdf'}
        ]}]
        mock_client.get_paginator.return_value = mock_paginator
        
        # Mock get_object to return different content for each file
        def mock_get_object(Bucket, Key):
            class MockBody:
                def __init__(self, key):
                    self.key = key
                    with open(f'tests/pdf-test/{key}', 'rb') as f:
                        self._content = f.read()
                
                def read(self):
                    return self._content

            return {'Body': MockBody(Key)}
        
        mock_client.get_object.side_effect = mock_get_object
        
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
def inventory(db_session, s3_client):
    with patch('dsst_etl.inventory_pdfs_pmid.get_bucket_name') as mock_get_bucket_name:
        mock_get_bucket_name.return_value = 'dsst-pdfs'
        
        # Initialize the class with the session
        inventory = DocumentInventoryPMID(db_session, oddpub_host_api='http://mock-api:8071')
        # Override the S3 client
        inventory.s3_client = s3_client

        # For MinIO, ensure test files exist
        if not isinstance(s3_client, MagicMock):
            try:
                # Delete and recreate bucket to ensure clean state
                try:
                    # List and delete all objects
                    paginator = s3_client.get_paginator('list_objects_v2')
                    for page in paginator.paginate(Bucket='dsst-pdfs'):
                        for obj in page.get('Contents', []):
                            s3_client.delete_object(Bucket='dsst-pdfs', Key=obj['Key'])
                    s3_client.delete_bucket(Bucket='dsst-pdfs')
                except:
                    pass  # Bucket might not exist
                
                s3_client.create_bucket(Bucket='dsst-pdfs')
            except:
                pass  # Bucket might already exist
            
            # Upload test files
            for test_file in ['test1.pdf', 'test2.pdf']:
                with open(f'tests/pdf-test/{test_file}', 'rb') as f:
                    s3_client.put_object(
                        Bucket='dsst-pdfs',
                        Key=test_file,
                        Body=f.read()
                    )
        
        return inventory


@patch('requests.post')
def test_process_s3_inventory_success(mock_post, inventory, db_session):
    # Track which files are being processed
    current_file = None

    def mock_post_side_effect(url, files, *args, **kwargs):
        if url == 'http://mock-api:8071/oddpub':
            mock_response = MagicMock()
            mock_response.json.return_value = {
               'article': current_file,  # Use the tracked file
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

    # Patch the _run_oddpub_analysis method to track the current file
    original_run_oddpub = inventory._run_oddpub_analysis
    def wrapped_run_oddpub(key, file_content, work, document, provenance):
        nonlocal current_file
        current_file = key
        return original_run_oddpub(key, file_content, work, document, provenance)
    
    inventory._run_oddpub_analysis = wrapped_run_oddpub
    mock_post.side_effect = mock_post_side_effect

    try:
        # Run the method
        inventory.run()

        # Assertions - we expect 2 entries since we have 2 test PDFs
        assert db_session.query(Documents).count() == 2, "Documents table should have 2 rows"
        assert db_session.query(Identifier).count() == 2, "Identifier table should have 2 rows"
        assert db_session.query(Works).count() == 2, "Works table should have 2 rows"
        assert db_session.query(OddpubMetrics).count() == 2, "OddpubMetrics table should have 2 rows"

        # Verify mock_post was called twice, once for each PDF
        assert mock_post.call_count == 2, "POST request should be called twice"
    finally:
        # Restore the original method
        inventory._run_oddpub_analysis = original_run_oddpub


def test_process_s3_inventory_failure(inventory, db_session, s3_client):
    if isinstance(s3_client, MagicMock):
        # For mock client, force an exception
        s3_client.get_paginator.side_effect = Exception("Test exception")
    else:
        # For MinIO client, use an invalid bucket to force failure
        inventory.s3_client = boto3.client(
            's3',
            endpoint_url='http://localhost:9000',
            aws_access_key_id='invalid',
            aws_secret_access_key='invalid',
            region_name='us-east-1',
            config=Config(signature_version='s3v4')
        )

    with patch('dsst_etl.inventory_pdfs_pmid.logger') as mock_logger:
        # Run the method
        inventory.run()

        # Assertions
        mock_logger.error.assert_called()  # Just verify error was logged
        assert db_session.query(Documents).count() == 0
        assert db_session.query(Identifier).count() == 0
        assert db_session.query(Works).count() == 0
        assert db_session.query(OddpubMetrics).count() == 0