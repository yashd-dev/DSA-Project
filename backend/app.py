from flask import Flask, request, send_file, jsonify
from PIL import Image
from flask_cors import CORS
import io
import traceback

app = Flask(__name__)
CORS(app)

@app.route('/compress/jpeg', methods=['POST'])
def compress_jpeg():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
            
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        try:
            img = Image.open(file)
        except Exception as e:
            print(f"Invalid image file: {str(e)}")
            return jsonify({'error': 'Invalid image file'}), 400
            
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        try:
            quality = int(request.form.get('quality', 50))
            if quality < 1 or quality > 100:
                return jsonify({'error': 'Quality must be between 1 and 100'}), 400
        except ValueError:
            return jsonify({'error': 'Quality must be a number'}), 400
            
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG', quality=quality)
        img_io.seek(0)
        
        print(f"Image size: {img_io.getbuffer().nbytes} bytes")
        
        return send_file(
            img_io,
            mimetype='image/jpeg',
            as_attachment=True,
            download_name='compressed.jpg'
        )
        
    except Exception as e:
        print(f"Error during compression: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/hello')
def hello():
    return 'Hello World!'

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)