import json
from pathlib import Path
from typing import Optional

from src.analysis import DigitCounterAnalysis


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

    def as_dict(self):
        return self.__dict__


class Database:
    def __init__(self, users_db_file: str, analyses_db_file: str):
        # store files to know where to save databases
        self.users_file = Path(users_db_file)
        self.analyses_file = Path(analyses_db_file)

        # load databases
        self.users = Database.load_default_db(users_db_file)
        self.analyses = Database.load_default_db(analyses_db_file)

    def save(self):
        Database.store(self.users_file, self.users)
        Database.store(self.analyses_file, self.analyses)

    def add_user(self, user: User):
        if user.id in self.users:
            raise UserExists(user.id)
        self.users[user.id] = user

    def add_analysis(self, analysis: DigitCounterAnalysis):
        if analysis.id in self.analyses:
            raise AnalysisExists(analysis.id)
        self.analyses[analysis.id] = analysis

    def get_user(self, username: str) -> Optional[User]:
        return self.users.get(username)

    def get_analysis(self, file_hash: str) -> Optional[DigitCounterAnalysis]:
        return self.analyses.get(file_hash)

    @staticmethod
    def load_default_db(filename: str) -> dict:
        if not (file := Path(filename)).exists():
            # initialize database
            Database.store(file, {})

        return Database.load(file)

    @staticmethod
    def store(file: Path, data: dict):
        file.parent.mkdir(parents=True, exist_ok=True)
        with file.open('w') as f:
            json.dump(data, f)

    @staticmethod
    def load(file: Path) -> dict:
        with file.open('r') as f:
            return json.load(f)
