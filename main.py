from wtforms import validators, SubmitField, FileField
from flask_wtf import FlaskForm
from flask import render_template,redirect,url_for
from flask import Flask
from flask import request
import numpy as np
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
from keras.applications.resnet50 import preprocess_input
from keras.models import load_model
import tensorflow as tf
import io
import os

def load_keras_model():
    """Load in the pre-trained model"""
    global model
    model = load_model('resnet.h5')
    global graph
    graph = tf.get_default_graph()

class ReusableForm(FlaskForm):
    """User entry form for entering specifics for generation"""
    # Starting seed
    file = FileField("Image File to Classify:",validators=[validators.InputRequired()])

    # Submit button
    submit = SubmitField("Classify")

def pred_fruit(model, file):

    try:        
        
        img = Image.open(file)
        width, height = img.size

        if height >= width:
            basewidth = 244
            wpercent = (basewidth/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))

        if height < width:
            hsize = 244
            hpercent = (hsize/float(img.size[1]))
            basewidth = int((float(img.size[0])*float(hpercent)))    

        img = img.resize((basewidth,hsize), Image.ANTIALIAS)
        width, height = img.size
        left = (width - 244)/2
        top = (height - 244)/2
        right = (width + 244)/2
        bottom = (height +244)/2
        img = img.crop((left, top, right, bottom))

        arr = np.array(img)

        if arr.shape == (244,244,3):
            with graph.as_default():
                testfruit = arr
                testfruit = np.expand_dims(testfruit,axis=0)
                testfruit = preprocess_input(testfruit)
                pred  = model.predict(testfruit)
                text = str(int(np.max(pred)*100))+'% '+ ['Apple','Orange','Pear'][pred.argmax()]          

        else: 
            img = Image.open(errpath)
            text = 'Image dim error!'
    except:
        img = Image.open(errpath)
        text = 'Image read error!' 
    
    new_im = Image.new('RGB', (344, 360),'ivory')
    draw = ImageDraw.Draw(new_im)
    new_im.paste(img, (50,50))
    
    font = ImageFont.load_default()
    #font = ImageFont.truetype("arial.ttf", 24)
    w, h = draw.textsize(text,font)
    draw.text(((244-w)/2+50,310),text,(0,0,0),font=font) 
    
    new_im.save(filepath)

#Flask App

app = Flask(__name__)
# PREDICT_FOLDER = os.path.join('static', 'predict')
# app.config['PREDICT_FOLDER'] = PREDICT_FOLDER

filepath = os.path.join('static', 'predict.png')
errpath = os.path.join('static', 'error.png')

# Home page
@app.route("/", methods=['GET', 'POST'])
def home():
    """Home page of app with form"""
   
    if os.path.exists(filepath): 
        os.remove(filepath)
    
    # Create form
    form = ReusableForm()        
    # On form entry and all conditions met
    if request.method == 'POST' and form.validate():
        # Extract information
        file = request.files['file']
        pred_fruit(model, file)
        return render_template('prediction.html', output = filepath)          
    
    if request.method == 'GET':    
        return render_template('index.html', form=form)
    
@app.route('/clear')
def clear():
    return redirect(url_for('home'))

if __name__ == "__main__":
    print(("* Loading Keras model and Flask starting server..."
           "\nplease wait until server has fully started *"))
    load_keras_model()
    app.secret_key = 'super secret key'
    app.run(host='127.0.0.1', port=8080)
