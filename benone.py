#!/usr/bin/env python3

import argparse
import json

from flask import Flask, render_template, request


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


def create_app(cfg: dict):
    app = Flask(__name__)
    if cfg['ENV'] == 'development':
        # refreshing application
        app.config = {
            **app.config,
            'SEND_FILE_MAX_AGE_DEFAULT': 0,
            'TEMPLATES_AUTO_RELOAD': True
        }
    elif cfg['ENV'] == 'production':
        pass
    else:
        raise WrongEnvironment(cfg['ENV'])

    app.config['ENV'] = cfg['ENV']

    @app.context_processor
    def inject_globals():
        return {
        }

    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    @app.route('/api/files', methods=['GET'])
    def send_users_files():
        return {
            'files': []
        }

    @app.route('/api/upload', methods=['POST'])
    def get_user_file():
        data = request.get_json()

    app.run(host=cfg['HOST'], port=cfg['PORT'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BeNone is an Service for benning your data!')
    parser.add_argument('-c', '--config', type=str, default='cfg.json', help='config filename')

    args = parser.parse_args()
    with open(args.config, 'r') as cfg_file:
        config = json.load(cfg_file)

    create_app(config)
