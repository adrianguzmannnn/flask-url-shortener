import os
import json
from flask import (render_template, request, redirect, url_for, flash, abort,
                   session, jsonify, Blueprint)
from werkzeug.utils import secure_filename

DATABASE = 'urls.json'

bp = Blueprint('urlshort', __name__)


def _load_database(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


@bp.route('/')
def home():
    return render_template('home.html', codes=session.keys())


@bp.route('/your-url', methods=['GET', 'POST'])
def your_url():
    if request.method == 'POST':

        # Load the json file if it exists.
        urls = _load_database(DATABASE)

        # Retrieve the value for `Short Name`.
        key = request.form.get('code')

        # Determine whether the key provided already exists. If so,
        # return to the home page.
        if urls.get(key):
            flash('That short name already exists. Select a new name.')
            return redirect(url_for('urlshort.home'))

        # Handle urls and files.
        get_form_url = request.form.get('url', False)
        if get_form_url:
            urls.update({key: {'url': get_form_url}})
        else:
            f = request.files.get('file')
            full_name = f'{key}{secure_filename(f.filename)}'
            f.save(f'./static/uploaded_files/{full_name}')
            urls.update({key: {'file': full_name}})

        # Push the entry to the file and register to the session.
        with open(DATABASE, 'w') as f:
            json.dump(urls, f)
            session.update({key: True})

        return render_template('entry.html', code=key)

    else:

        # The user submitted a get request, so redirect home.
        return redirect(url_for('urlshort.home'))


@bp.route('/<string:code>')
def redirect_to_url(code):

    # Load the json file if it exists.
    urls = _load_database(DATABASE)

    get_code = urls.get(code)

    if get_code:
        # Return the entry for this code if it exists.
        get_code_url = get_code.get('url')
        return redirect(get_code_url) if get_code_url else \
            redirect(url_for('static', filename=f'uploaded_files/{get_code.get("file")}'))

    return abort(404)


@bp.errorhandler(404)
def page_not_found(error):
    return render_template('error.html'), 404


@bp.route('/api')
def session_api():
    return jsonify(list(session.keys()))
