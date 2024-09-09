from flask import Flask, render_template, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
import shutil
import tempfile

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'png'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

MAX_IMAGE_SIZE = 1000  # Maximum image size (width or height)

def encode_text_to_image(text):
    # Calculate the number of pixels needed based on the text length and maximum image size
    num_pixels = min(len(text), MAX_IMAGE_SIZE ** 2)
    img_width = min(int(np.ceil(np.sqrt(num_pixels))), MAX_IMAGE_SIZE)
    img_height = (num_pixels + img_width - 1) // img_width
    
    # Create a blank image
    encoded_img = np.zeros((img_height, img_width), dtype=np.uint8)
    
    # Encode text into image pixels
    for i, char in enumerate(text):
        row = i // img_width
        col = i % img_width
        encoded_img[row, col] = ord(char)
    
    return encoded_img

def split_text_into_chunks(text, chunk_size):
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]

def encode_text_file_to_images(input_text, input_file_path):
    if input_text:
        text = input_text
        # Create a temporary file in the uploads folder
        with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=app.config['UPLOAD_FOLDER']) as temp_file:
            temp_file.write(text)
            input_file_path = temp_file.name
    
    if input_file_path:
        with open(input_file_path, 'r') as file:
            text = file.read()
        
        chunk_size = MAX_IMAGE_SIZE ** 2
        text_chunks = list(split_text_into_chunks(text, chunk_size))
        
        output_image_paths = []
        for idx, chunk in enumerate(text_chunks):
            encoded_image = encode_text_to_image(chunk)
            output_image_path = os.path.join(os.path.expanduser('~'), 'Downloads', f"{os.path.splitext(os.path.basename(input_file_path))[0]}_encoded_{idx + 1}.png")
            cv2.imwrite(output_image_path, encoded_image)
            output_image_paths.append(output_image_path)
        
        return output_image_paths
    else:
        return None  # Handle the case where no input is provided

def decode_image_to_text(encoded_img):
    # Flatten the image and decode it back to text
    text = ''.join([chr(char) for char in encoded_img.flatten() if char != 0])
    return text

def decode_image_file_to_text(input_image_paths):
    decoded_texts = []
    for input_image_path in input_image_paths:
        # Read encoded image
        encoded_image = cv2.imread(input_image_path, cv2.IMREAD_GRAYSCALE)
        
        # Decode image back to text
        decoded_text = decode_image_to_text(encoded_image)
        decoded_texts.append(decoded_text)
    
    # Write decoded text to temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
        for text in decoded_texts:
            temp_file.write(text)
        temp_file_path = temp_file.name

    # Move the temporary file to the downloads folder
    download_path = os.path.join(os.path.expanduser('~'), 'Downloads', os.path.basename(temp_file_path))
    shutil.move(temp_file_path, download_path)

    return download_path

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encode', methods=['POST'])
def encode():
    text_input = request.form.get('text_input')
    file = request.files.get('file')

    # Check if both text_input and file are missing
    if not text_input and not file:
        return redirect(request.url)

    file_path = None  # Initialize file_path variable
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

    # Call encode function
    encoded_image_paths = encode_text_file_to_images(text_input, file_path)

    # Redirect to index page with result
    return render_template('index.html', result=f'Encoded image(s) saved at: {encoded_image_paths}', image_paths=encoded_image_paths)

@app.route('/decode', methods=['POST'])
def decode():
    files = request.files.getlist('file')

    if not files or any(file.filename == '' for file in files):
        return redirect(request.url)

    file_paths = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            file_paths.append(file_path)

    # Call decode function
    output_text_file_path = decode_image_file_to_text(file_paths)

    # Redirect to index page with result
    return render_template('index.html', result=f'Decoded text saved at: {output_text_file_path}', text_file_path=output_text_file_path)

@app.route('/download')
def download():
    file_path = request.args.get('file_path')
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run()
