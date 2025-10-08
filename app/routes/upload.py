from flask import Blueprint, request, jsonify, current_app
import os

upload_bp = Blueprint('upload', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@upload_bp.route('/upload-data', methods=['POST'])
def upload_data():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if file and allowed_file(file.filename):
        filename = file.filename
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(save_path)
        return jsonify({'message': f'File saved to {save_path}', 'file_path': save_path})
    else:
        return jsonify({'error': 'File type not allowed'}), 400
