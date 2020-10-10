# url-shortener
A forked repository with minor improvements.

The following improvements were made to `urlshort.py`.
```diff
@@ -1,58 +1,86 @@
-from flask import render_template, request, redirect, url_for, flash, abort, session, jsonify, Blueprint
+import os
 import json
-import os.path
+from flask import (render_template, request, redirect, url_for, flash, abort,
+                   session, jsonify, Blueprint)
 from werkzeug.utils import secure_filename

-bp = Blueprint('urlshort',__name__)
+DATABASE = 'urls.json'
+
+bp = Blueprint('urlshort', __name__)
+
+
+def _load_database(path):
+    if os.path.exists(path):
+        with open(path) as f:
+            return json.load(f)
+    return {}
+

 @bp.route('/')
 def home():
     return render_template('home.html', codes=session.keys())

-@bp.route('/your-url', methods=['GET','POST'])
+
+@bp.route('/your-url', methods=['GET', 'POST'])
 def your_url():
     if request.method == 'POST':
-        urls = {}

-        if os.path.exists('urls.json'):
-            with open('urls.json') as urls_file:
-                urls = json.load(urls_file)
+        # Load the json file if it exists.
+        urls = _load_database(DATABASE)
+
+        # Retrieve the value for `Short Name`.
+        key = request.form.get('code')

-        if request.form['code'] in urls.keys():
-            flash('That short name has already been taken. Please select another name.')
+        # Determine whether the key provided already exists. If so,
+        # return to the home page.
+        if urls.get(key):
+            flash('That short name already exists. Select a new name.')
             return redirect(url_for('urlshort.home'))

-        if 'url' in request.form.keys():
-            urls[request.form['code']] = {'url':request.form['url']}
+        # Handle urls and files.
+        get_form_url = request.form.get('url', False)
+        if get_form_url:
+            urls.update({key: {'url': get_form_url}})
         else:
-            f = request.files['file']
-            full_name = request.form['code'] + secure_filename(f.filename)
-            f.save('/Users/nickwalter/Desktop/url-shortener/urlshort/static/user_files/' + full_name)
-            urls[request.form['code']] = {'file':full_name}
+            f = request.files.get('file')
+            full_name = f'{key}{secure_filename(f.filename)}'
+            f.save(f'./static/uploaded_files/{full_name}')
+            urls.update({key: {'file': full_name}})

+        # Push the entry to the file and register to the session.
+        with open(DATABASE, 'w') as f:
+            json.dump(urls, f)
+            session.update({key: True})
+
+        return render_template('entry.html', code=key)

-        with open('urls.json','w') as url_file:
-            json.dump(urls, url_file)
-            session[request.form['code']] = True
-        return render_template('your_url.html', code=request.form['code'])
     else:
+
+        # The user submitted a get request, so redirect home.
         return redirect(url_for('urlshort.home'))

+
 @bp.route('/<string:code>')
 def redirect_to_url(code):
-    if os.path.exists('urls.json'):
-        with open('urls.json') as urls_file:
-            urls = json.load(urls_file)
-            if code in urls.keys():
-                if 'url' in urls[code].keys():
-                    return redirect(urls[code]['url'])
-                else:
-                    return redirect(url_for('static', filename='user_files/' + urls[code]['file']))
+
+    # Load the json file if it exists.
+    urls = _load_database(DATABASE)
+
+    get_code = urls.get(code)
+
+    if get_code:
+        # Return the entry for this code if it exists.
+        get_code_url = get_code.get('url')
+        return redirect(get_code_url) if get_code_url else \
+            redirect(url_for('static', filename=f'uploaded_files/{get_code.get("file")}'))
+
+
 @bp.errorhandler(404)
 def page_not_found(error):
-    return render_template('page_not_found.html'), 404
+    return render_template('error.html'), 404
+
```

This is a basic Flask application showing the ability to redirect urls and capture form inputs.
![example](example.png)