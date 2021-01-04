import os
from werkzeug.utils import secure_filename
from flask import Flask

#initialize the flask app
app = Flask(__name__)

#the folder in which the uploaded images will be saved
UPLOAD_FOLDER = 'C:/Users/abdal/Flask-Task/flaskr/static/images'
#the allowed types of the uploaded files 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

"""
check if the uploaded file is one of the allowed types
"""
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           
"""
saves the uploaded file if its an allowed type, in the specified uploaded file
and returns the file name
"""        
def save_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename