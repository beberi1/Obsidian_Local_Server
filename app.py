from flask import Flask, send_from_directory, render_template, jsonify, abort, send_file
import os
import zipfile
import io
import markdown
from werkzeug.utils import safe_join

app = Flask(__name__)

# Change path to your obsidian vault
VAULT_DIR = '/home/kai/Documents/plans'

@app.route('/')
def index():
    root_files = []
    directory_structure = []

    for root, dirs, files in os.walk(VAULT_DIR):
        rel_dir = os.path.relpath(root, VAULT_DIR)
        if rel_dir == ".":
            rel_dir = ""
            root_files = sorted(files)
        else:
            directory_structure.append((rel_dir, sorted(dirs), sorted(files)))

    return render_template('index.html', root_files=root_files, directory_structure=sorted(directory_structure))

@app.route('/view/<path:filename>')
def view_file(filename):
    file_path = safe_join(VAULT_DIR, filename)
    if not os.path.isfile(file_path):
        abort(404)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if filename.endswith('.md'):
            content = markdown.markdown(content)
        return jsonify({"content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    file_path = safe_join(VAULT_DIR, filename)
    if not os.path.exists(file_path):
        abort(404)
    return send_from_directory(VAULT_DIR, filename, as_attachment=True)

@app.route('/download_directory/<path:dirname>')
def download_directory(dirname):
    dir_path = safe_join(VAULT_DIR, dirname)
    if not os.path.isdir(dir_path):
        abort(404)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, VAULT_DIR)
                zip_file.write(file_path, arcname)
    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name=f"{dirname}.zip", mimetype="application/zip")

@app.route('/download_all')
def download_all():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(VAULT_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, VAULT_DIR)
                zip_file.write(file_path, arcname)
    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name="vault.zip", mimetype="application/zip")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
