from flask import Flask, render_template, url_for, request, redirect, flash
from werkzeug.utils import secure_filename
import os
from models import Feature, Character
from predict import Predict
import config
from api import df_api

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

UPLOAD_FOLDER = 'static/uploads/'

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():  # put application's code here

    features = []
    contents = [{'name': "노란색큐브", 'job': '에반'}, {'name': "검제큐브", 'job': '검제'}, {'name': "헤카테큐브", 'job': '헤카테'}]

    for idx, content in enumerate(contents):
        feature = Character()
        feature.name = content['name']
        feature.job = content['job']
        feature.id = idx + 1
        features.append(feature)

    return render_template('index_2.html', features=features)
    # return render_template('index.html')


@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        predict = Predict()
        character_list = predict.api('static/uploads/' + filename)
        flash("Image successfully uploaded and displayed below")

        api = df_api(config.df_api)
        api.api_basic_info("검제큐브", "베가본드")
        character_list = api.api_basic_info_get_all(character_list)
        character_list = api.api_character_info_get_all(character_list)

        print(character_list[0].__dict__)

        return render_template('index_2.html', filename=filename, features=character_list)
    else:
        flash("Allowed image types are - png, jpg, jpeg, git")
        return redirect(request.url)


@app.route('/display_image/<filename>')
def display_image(filename):
    print("display image")
    return redirect(url_for('static', filename='uploads/ocr_' + filename), code=301)


if __name__ == '__main__':
    app.run()
