#!/usr/bin/env python3

import argparse
import json
import os
import sys

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from src.config import AppConfig
from src.utils import Term


class WrongRequest(Exception):
    pass


class WrongEnvironment(Exception):
    """Exception raised when wrong environment is set.

    Attributes:
        env -- input environment value which cased exception
        message -- explanation of the error
    """

    def __init__(self, env: str, message: str = 'Wrong environment, options = ["production", "development"]'):
        self.env = env
        self.message = message
        super().__init__(self.message)


def get_analysis(filename: str):
    pass


def create_app(app_config: AppConfig):
    app = Flask(__name__)
    if app_config.ENV == 'development':
        # refreshing application
        app.config = {
            **app.config,
            'SEND_FILE_MAX_AGE_DEFAULT': 0,
            'TEMPLATES_AUTO_RELOAD': True
        }
    elif app_config.ENV == 'production':
        pass
    else:
        raise WrongEnvironment(app_config.ENV)

    app.config = {**app.config, **app_config.__dict__}

    @app.context_processor
    def inject_globals():
        return {
        }

    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    @app.route('/api/analyses', methods=['GET'])
    def send_users_files():
        return {
            'user_files': [],
            'others_files': [],
        }

    @app.route('/api/upload', methods=['POST'])
    def get_user_file():

        # check if the post request has the file part
        if 'file' not in request.files:
            return {'success': False}, 400
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return {'success': False}, 400
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return {'success': True}, 200

    app.run(host=app.config['HOST'], port=app.config['PORT'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BeNone is an Service for benning your data!')
    parser.add_argument('-c', '--config', type=str, default='cfg.json', help='config filename')

    args = parser.parse_args()
    try:
        config = AppConfig(args.config)
    except ValueError:
        Term.error(f'Invalid configuration file = {args.config}')
        sys.exit(1)

    create_app(config)
