import os
import unittest
from pathlib import Path

from src.analysis import DigitCounterAnalysis
from src.database import Database, AnalysisExists


class TestDatabase(unittest.TestCase):
    def setUp(self) -> None:
        # when running from base directory need to add 'tests/' prefix
        self.test_root_dir = '' if os.getcwd().endswith('tests') else 'tests/'

        self.data_folder = f'{self.test_root_dir}data'
        self.users_db_file = f'{self.data_folder}/users.pickle'
        self.analyses_db_file = f'{self.data_folder}/analyses.pickle'
        self.upload_folder = f'{self.data_folder}/users_files'
        self.user_file = 'simple_data.tsv'
        self.user_filepath = f'{self.upload_folder}/{self.user_file}'

    def tearDown(self) -> None:
        Path(self.users_db_file).unlink(missing_ok=True)
        Path(self.analyses_db_file).unlink(missing_ok=True)

    def test_init(self):
        Database(self.users_db_file, self.analyses_db_file, self.upload_folder)
        self.assertTrue(Path(self.users_db_file).exists())
        self.assertTrue(Path(self.analyses_db_file).exists())

    def test_get_files(self):
        db = Database(self.users_db_file, self.analyses_db_file, self.upload_folder)
        self.assertListEqual(db.get_filenames(), [self.user_file])

    def test_add_analysis(self):
        analysis = DigitCounterAnalysis(self.user_filepath)
        db = Database(self.users_db_file, self.analyses_db_file, self.upload_folder)
        db.add_analysis(analysis)
        self.assertEqual(analysis, db.get_analysis(analysis.id))

    def test_add_same_analysis(self):
        analysis = DigitCounterAnalysis(self.user_filepath)
        db = Database(self.users_db_file, self.analyses_db_file, self.upload_folder)
        db.add_analysis(analysis)
        with self.assertRaises(AnalysisExists):
            db.add_analysis(analysis)


if __name__ == '__main__':
    unittest.main()
