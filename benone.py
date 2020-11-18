#!/usr/bin/env python3

import argparse
import os
import sys
from pathlib import Path

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from src.analysis import DigitCounterAnalysis, WrongFile, Reader
from src.config import AppConfig
from src.database import Database
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

    database = Database('data/users.pickle', 'data/analyses.pickle', app_config)

    @app.context_processor
    def inject_globals():
        return {}

    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    @app.route('/api/files', methods=['GET'])
    def files_list():
        """Get available files uploaded by users."""
        return {
            'files': database.get_filenames(),
        }

    @app.route('/api/extensions', methods=['GET'])
    def extensions_list():
        """Get available extensions to use when parsing file."""
        return {
            'extensions': Reader.get_supported_extensions(),
        }

    @app.route('/api/analyze', methods=['POST'])
    def analyze_file():
        """Analyze file for Benford's Law.

        First check if analysis not in database, if True - just load
        it and show to user, if not - do analysis.

        """
        try:
            data = request.get_json()
            ext = data['ext']
            filename = data['filename']
            filename = secure_filename(filename)
            filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # analysis id is file hash, if done once, do not do it again
            analysis_id = Reader.file_id(Path(filename), ext)

            # try to get analysis from database using file hash as id
            if not (analysis := database.get_analysis(analysis_id)):
                analysis = DigitCounterAnalysis(filename, ext=ext)
                database.add_analysis(analysis)
        except WrongFile as e:
            Term.error(str(e))
            return {'success': False, 'error': str(e)}, 400
        except (KeyError, TypeError) as e:
            Term.error(str(e))
            return {'success': False, 'error': str(e)}, 400
        except Exception as e:
            Term.error(str(e))
            return {'success': False, 'error': str(e)}, 400

        return {
                   'success': True,
                   'stats': analysis.get_stats(),
                   'counters': analysis.get_counters('simple'),
                   'frequenters': analysis.get_frequenters('simple'),
                   'lead_frequenters': analysis.get_frequenters('lead'),
                   'benfords_law': analysis.get_benfords_law_pvalues(),
               }, 200

    @app.route('/api/upload', methods=['POST'])
    def get_user_file():
        """Get file from user.

        If file with same name exists - check if content is the
        same, if yes - do not save file, if not - return error
        that names must be unique (for now).

        """
        # check if the post request has the file part
        if 'file' not in request.files:
            return {'success': False, 'error': 'No file'}, 400
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return {'success': False, 'error': 'File not selected'}, 400
        if file:
            filename = secure_filename(file.filename)
            filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # if file exists and content is same do not save again
            if (stored_file := Path(filename)).exists():
                if Reader.same_files(stored_file, file):
                    return {'success': True}, 200
                # same filename but different content - not allowed, sorry
                else:
                    return {'success': False, 'error': 'File with the same name already exists'
                                                       'unfortunately it is not allowed yet'}, 400
            # everything's ok, save file under UPLOAD_FOLDER
            file.save(filename)
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
