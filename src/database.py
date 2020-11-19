import pickle
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


class Database:
    """Class for communicating with all files and databases.

    Currently databases are stored as serialized objects in .pickle files.
    Through this objects server can obtain list of files uploaded by users.
    Two databases are available:
        - users: with all users
        - analyses: with all analyses performed on data
    """

    def __init__(self, users_db_file: str, analyses_db_file: str, upload_folder: str):
        # load file with help
        with open('docs/help.html') as help_file:
            self._app_help = help_file.read()

        # store files to know where to save databases
        self._users_file = Path(users_db_file)
        self._analyses_file = Path(analyses_db_file)

        # load databases
        self._users = Database.load_default_db(users_db_file)
        self._analyses = Database.load_default_db(analyses_db_file)

        self._path_to_files = upload_folder
        # be sure that folder exists
        Path(self._path_to_files).mkdir(parents=True, exist_ok=True)

    def save(self):
        """After changes, store databases files"""
        Database.store(self._users_file, self._users)
        Database.store(self._analyses_file, self._analyses)

    def get_filenames(self):
        """Get filenames to users files uploaded to server"""
        paths = Path(self._path_to_files).glob('**/*')
        filenames = [file.name for file in paths if file.is_file()]
        return filenames

    def get_app_help(self):
        """App usage help stored at 'docs/help.html'"""
        return self._app_help

    def add_user(self, user: User):
        if user.id in self._users:
            raise UserExists(user.id)
        self._users[user.id] = user
        self.save()

    def add_analysis(self, analysis: DigitCounterAnalysis):
        """Add new analysis.

        Analysis id is basically file content hash + extension used to analyze.
        Adding same analysis raising exception.
        """

        # check if analysis in database
        if analysis.id in self._analyses:
            raise AnalysisExists(analysis.id)
        self._analyses[analysis.id] = analysis
        self.save()

    def get_user(self, username: str) -> Optional[User]:
        return self._users.get(username)

    def get_analysis(self, analysis_id: str) -> Optional[DigitCounterAnalysis]:
        """Based on `analysis_id = file hash + extension`, get analysis from database"""
        return self._analyses.get(analysis_id)

    @staticmethod
    def load_default_db(filename: str) -> dict:
        """Load default database, currently pickled file"""
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
