# test_upload_rtransparent_data.py
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from sqlalchemy import inspect
from dsst_etl import get_db_engine
from dsst_etl.upload_rtransparent_data import RTransparentDataUploader
from dsst_etl.models import RTransparentPublication
import numpy as np
from dsst_etl.db import get_db_session, init_db
import logging

from tests.base_test import BaseTest # type: ignore 

logger = logging.getLogger(__name__)

class TestRTransparentDataUploader(BaseTest):

    def mock_data(self):
        logger.info("Creating mock data")
        data = {
            "year": [2024, 2023, 2022],
            "filename": ['test.feather', 'test2.feather', 'test3.feather'],
            "pmcid_pmc": [123456, 123457, 123458],
            "doi": ['10.1000/123456', '10.1000/123457', '10.1000/123458']
        }
        df = pd.DataFrame(data=data)
        logger.info(df)
        return df
        

    def setUp(self):
        super().setUp()
        self.uploader = RTransparentDataUploader(self.session)


    @patch('pandas.read_feather')
    def test_read_file_feather(self, mock_read_feather):
        mock_read_feather.return_value = self.mock_data()
        result = self.uploader._read_file('test.feather')
        mock_read_feather.assert_called_once_with('test.feather')
        self.assertEqual(len(result), 3)

    @patch('pandas.read_parquet')
    def test_read_file_parquet(self, mock_read_parquet):
        mock_read_parquet.return_value = self.mock_data()
        result = self.uploader._read_file('test.parquet')
        mock_read_parquet.assert_called_once_with('test.parquet')
        self.assertEqual(len(result), 3)

    def test_read_file_invalid_format(self):
        with self.assertRaises(ValueError):
            self.uploader._read_file('test.txt')

    def test_upload_data(self):
        self.uploader._read_file = MagicMock(return_value=self.mock_data())

        self.uploader.upload_data('test.feather', n_rows=1)

        assert self.session.query(RTransparentPublication).count() == 3


if __name__ == '__main__':
    unittest.main()