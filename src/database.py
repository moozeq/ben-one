import pickle
from pathlib import Path
from typing import Optional

from src.analysis import DigitCounterAnalysis
from src.config import AppConfig


class UserExists(Exception):
    """Exception raised when user already exists."""

    def __init__(self, user_id: str):
        self.message = f'User is already in database, id = {user_id}'
        super().__init__(self.message)


class AnalysisExists(Exception):
    """Exception raised when analysis is already in database."""

    def __init__(self, a_hash: str):
        self.message = f'Analysis has been already done, hash = {a_hash}'
        super().__init__(self.message)


class User:
    def __init__(self, name: str):
        self.id = name


class Database:
    def __init__(self, users_db_file: str, analyses_db_file: str, app_config: AppConfig):
        # store files to know where to save databases
        self._users_file = Path(users_db_file)
        self._analyses_file = Path(analyses_db_file)

        # load databases
        self._users = Database.load_default_db(users_db_file)
        self._analyses = Database.load_default_db(analyses_db_file)

        self._path_to_files = app_config.UPLOAD_FOLDER
        # be sure that folder exists
        Path(self._path_to_files).mkdir(parents=True, exist_ok=True)

    def save(self):
        Database.store(self._users_file, self._users)
        Database.store(self._analyses_file, self._analyses)

    def get_filenames(self):
        paths = Path(self._path_to_files).glob('**/*')
        filenames = [file.name for file in paths if file.is_file()]
        return filenames

    def add_user(self, user: User):
        if user.id in self._users:
            raise UserExists(user.id)
        self._users[user.id] = user
        self.save()

    def add_analysis(self, analysis: DigitCounterAnalysis):
        if analysis.id in self._analyses:
            raise AnalysisExists(analysis.id)
        self._analyses[analysis.id] = analysis
        self.save()

    def get_user(self, username: str) -> Optional[User]:
        return self._users.get(username)

    def get_analysis(self, file_hash: str) -> Optional[DigitCounterAnalysis]:
        return self._analyses.get(file_hash)

    @staticmethod
    def load_default_db(filename: str) -> dict:
        if not (file := Path(filename)).exists():
            # initialize database
            Database.store(file, {})

        return Database.load(file)

    @staticmethod
    def store(file: Path, data: dict):
        file.parent.mkdir(parents=True, exist_ok=True)
        with file.open('wb') as f:
            pickle.dump(data, f)

    @staticmethod
    def load(file: Path) -> dict:
        with file.open('rb') as f:
            return pickle.load(f)
