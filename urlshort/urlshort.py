import os
import json
from flask import render_template, request, redirect, url_for, flash, abort, session, jsonify, Blueprint
from werkzeug.utils import secure_filename

DATABASE = 'urls.json'

bp = Blueprint('urlshort', __name__)

def load_database(path):
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

        # Initialize the "database". 
        urls = load_database(DATABASE)

        # Retrieve form inputs.
        key = request.form.get('code')

        # Determine whether the key provided already exists. If so, return to the home page. 
        if urls.get(key):
            flash('That short name already exists. Select a new name.')
            return redirect(url_for('urlshort.home'))

        # Provide handling for urls and files.
        get_form_url = request.form.get('url') 
        if get_form_url:
            # Write the form inputs to a dictionary and push it to a file.
            urls.update({key: {'url': get_form_url}})
        else:
            f = request.files.get('file')
            full_name = f'{key}{secure_filename(f.filename)}'
            f.save(f'./static/uploaded_files/{full_name}')
            urls.update({key: {'file': full_name}})
        
        # Create an entry in the "database". 
        with open(DATABASE, 'w') as f:
            json.dump(urls, f)
            session.update({key: True})

        return render_template('your_url.html', code=key)

    else:

        # The user submitted a get request, so redirect home.
        return redirect(url_for('urlshort.home'))

@bp.route('/<string:code>')
def redirect_to_url(code):
    # Determine if the file exists.
    urls = load_database(DATABASE)
    if urls:
        get_code = urls.get(code)
        # Determine if there's an entry for this specific string.
        if get_code:
            get_code_url = get_code.get('url')
            if get_code_url:
                return redirect(get_code_url)
            else:
                return redirect(url_for('static', 
                                        filename=f'uploaded_files/{get_code.get("file")}'))
    
    return abort(404)

@bp.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

@bp.route('/api')
def session_api():
    return jsonify(list(session.keys()))