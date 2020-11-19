import json


class AppConfig:
    """Class used to load config from file"""

    DEF_UPLOAD_FOLDER = "data/users_files"
    DEF_ENV = "production"
    DEF_HOST = "127.0.0.1"
    DEF_PORT = 5000

    def __init__(self, config_filename: str):
        with open(config_filename, 'r') as cfg_file:
            config = json.load(cfg_file)

        self.UPLOAD_FOLDER = config.get("UPLOAD_FOLDER", AppConfig.DEF_UPLOAD_FOLDER)
        self.ENV = config.get("ENV", AppConfig.DEF_ENV)
        self.HOST = config.get("HOST", AppConfig.DEF_HOST)
        self.PORT = config.get("PORT", AppConfig.DEF_PORT)
