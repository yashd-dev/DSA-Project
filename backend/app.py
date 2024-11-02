import numpy as np
from PIL import Image
from collections import Counter
import heapq

class HuffmanNode:
    def __init__(self, value=None, freq=None):
        self.value = value
        self.freq = freq
        self.left = None
        self.right = None
        
    def __lt__(self, other):
        return self.freq < other.freq

class JPEGCompressor:
    def __init__(self):
        # Standard JPEG quantization matrix
        self.quantization_matrix = np.array([
            [16, 11, 10, 16, 24, 40, 51, 61],
            [12, 12, 14, 19, 26, 58, 60, 55],
            [14, 13, 16, 24, 40, 57, 69, 56],
            [14, 17, 22, 29, 51, 87, 80, 62],
            [18, 22, 37, 56, 68, 109, 103, 77],
            [24, 35, 55, 64, 81, 104, 113, 92],
            [49, 64, 78, 87, 103, 121, 120, 101],
            [72, 92, 95, 98, 112, 100, 103, 99]
        ])
        
    def rgb_to_ycbcr(self, rgb):
        """Convert RGB to YCbCr color space"""
        matrix = np.array([
            [0.299, 0.587, 0.114],
            [-0.168736, -0.331264, 0.5],
            [0.5, -0.418688, -0.081312]
        ])
        
        ycbcr = np.zeros_like(rgb, dtype=float)
        for i in range(rgb.shape[0]):
            for j in range(rgb.shape[1]):
                ycbcr[i, j] = np.dot(matrix, rgb[i, j])
        
        ycbcr[:,:,1:] += 128
        return ycbcr
    
    def ycbcr_to_rgb(self, ycbcr):
        """Convert YCbCr back to RGB color space"""
        matrix = np.array([
            [1, 0, 1.402],
            [1, -0.344136, -0.714136],
            [1, 1.772, 0]
        ])
        
        ycbcr = ycbcr.copy()
        ycbcr[:,:,1:] -= 128
        
        rgb = np.zeros_like(ycbcr, dtype=float)
        for i in range(ycbcr.shape[0]):
            for j in range(ycbcr.shape[1]):
                rgb[i, j] = np.dot(matrix, ycbcr[i, j])
        
        return np.clip(rgb, 0, 255).astype(np.uint8)
    
    def dct2d(self, block):
        """Apply 2D Discrete Cosine Transform"""
        def dct1d(x):
            N = len(x)
            result = np.zeros(N)
            for k in range(N):
                sum_ = 0
                for n in range(N):
                    sum_ += x[n] * np.cos(np.pi * (2*n + 1) * k / (2*N))
                result[k] = sum_ * np.sqrt(2/N) if k != 0 else sum_ * np.sqrt(1/N)
            return result
        
        # Apply DCT to rows
        temp = np.zeros_like(block, dtype=float)
        for i in range(block.shape[0]):
            temp[i,:] = dct1d(block[i,:])
        
        # Apply DCT to columns
        result = np.zeros_like(temp)
        for j in range(block.shape[1]):
            result[:,j] = dct1d(temp[:,j])
            
        return result
    
    def idct2d(self, block):
        """Apply 2D Inverse Discrete Cosine Transform"""
        def idct1d(x):
            N = len(x)
            result = np.zeros(N)
            for n in range(N):
                sum_ = 0
                for k in range(N):
                    factor = np.sqrt(2/N) if k != 0 else np.sqrt(1/N)
                    sum_ += factor * x[k] * np.cos(np.pi * (2*n + 1) * k / (2*N))
                result[n] = sum_
            return result
        
        # Apply IDCT to rows
        temp = np.zeros_like(block, dtype=float)
        for i in range(block.shape[0]):
            temp[i,:] = idct1d(block[i,:])
        
        # Apply IDCT to columns
        result = np.zeros_like(temp)
        for j in range(block.shape[1]):
            result[:,j] = idct1d(temp[:,j])
            
        return result
    
    def compress_channel(self, channel, quality_factor=50):
        """Compress a single channel using DCT and quantization"""
        # Determine padded dimensions to be a multiple of 8
        height, width = channel.shape
        padded_height = (height + 7) // 8 * 8
        padded_width = (width + 7) // 8 * 8

        # Create padded channel
        padded_channel = np.zeros((padded_height, padded_width), dtype=float)
        padded_channel[:height, :width] = channel.astype(float) - 128

        compressed = np.zeros_like(padded_channel, dtype=float)
        
        # Adjust quantization matrix based on quality
        q_matrix = self.quantization_matrix * (100 - quality_factor) / 50
        q_matrix = np.clip(q_matrix, 1, 255)
        
        # Process 8x8 blocks
        for i in range(0, padded_height, 8):
            for j in range(0, padded_width, 8):
                block = padded_channel[i:i+8, j:j+8]
                dct_block = self.dct2d(block)
                quantized = np.round(dct_block / q_matrix)
                compressed[i:i+8, j:j+8] = quantized

        print(compressed)
        # Crop back to original size
        return compressed[:height, :width], q_matrix

    def decompress_channel(self, compressed, q_matrix):
        """Decompress a single channel"""
        height, width = compressed.shape
        decompressed = np.zeros_like(compressed, dtype=float)
        
        for i in range(0, height, 8):
            for j in range(0, width, 8):
                block = compressed[i:i+8, j:j+8] * q_matrix
                idct_block = self.idct2d(block)
                decompressed[i:i+8, j:j+8] = idct_block + 128
                
        return np.clip(decompressed, 0, 255).astype(np.uint8)

class HuffmanCompressor:
    def build_tree(self, data):
        """Build Huffman tree from frequency data"""
        # Count frequency of each value
        freq = Counter(data)
        
        # Create priority queue
        heap = []
        for value, frequency in freq.items():
            node = HuffmanNode(value, frequency)
            heapq.heappush(heap, node)
        
        # Build tree
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            
            internal = HuffmanNode(freq=left.freq + right.freq)
            internal.left = left
            internal.right = right
            
            heapq.heappush(heap, internal)
            
        return heap[0] if heap else None
    
    def build_codes(self, root):
        """Build Huffman codes from tree"""
        codes = {}
        
        def traverse(node, code=""):
            if node is None:
                return
                
            if node.value is not None:
                codes[node.value] = code
                return
                
            traverse(node.left, code + "0")
            traverse(node.right, code + "1")
            
        traverse(root)
        return codes
    
    def encode(self, data):
        """Encode data using Huffman coding"""
        root = self.build_tree(data)
        codes = self.build_codes(root)
        
        # Convert data to bit string
        encoded = "".join(codes[value] for value in data)
        
        # Pack bits into bytes
        # Add padding to make length multiple of 8
        padding = (8 - len(encoded) % 8) % 8
        encoded += "0" * padding
        
        # Convert bit string to bytes
        encoded_bytes = bytearray()
        for i in range(0, len(encoded), 8):
            encoded_bytes.append(int(encoded[i:i+8], 2))
            
        return encoded_bytes, codes, padding
    
    def decode(self, encoded_bytes, codes, padding):
        """Decode Huffman-encoded data"""
        # Convert bytes back to bit string
        encoded = "".join(f"{byte:08b}" for byte in encoded_bytes)
        
        # Remove padding
        encoded = encoded[:-padding] if padding else encoded
        
        # Create reverse lookup
        reverse_codes = {code: value for value, code in codes.items()}
        
        # Decode
        decoded = []
        current_code = ""
        for bit in encoded:
            current_code += bit
            if current_code in reverse_codes:
                decoded.append(reverse_codes[current_code])
                current_code = ""
                
        return decoded

# Example Flask routes:

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import numpy as np
from PIL import Image
import io
import logging
import traceback

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

jpeg_compressor = JPEGCompressor()
huffman_compressor = HuffmanCompressor()

@app.route('/compress/jpeg', methods=['POST'])
def compress_jpeg():
    try:
        # Check if file exists in request
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
            
        file = request.files['image']
        
        # Check if filename is empty
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        # Check if file is actually an image
        try:
            img = Image.open(file)
            img.verify()  # Verify it's actually an image
        except Exception as e:
            logger.error(f"Invalid image file: {str(e)}")
            return jsonify({'error': 'Invalid image file'}), 400
            
        # Reopen image after verify
        file.seek(0)
        img = Image.open(file)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        # Get quality parameter
        quality = int(request.form.get('quality', 50))
        if quality < 1 or quality > 100:
            return jsonify({'error': 'Quality must be between 1 and 100'}), 400
            
        # Convert to numpy array
        img_array = np.array(img)
        logger.debug(f"Image shape: {img_array.shape}")
        
        # Convert to YCbCr
        ycbcr = jpeg_compressor.rgb_to_ycbcr(img_array)
        
        # Compress each channel
        compressed_y, qm_y = jpeg_compressor.compress_channel(ycbcr[:,:,0], quality)
        compressed_cb, qm_cb = jpeg_compressor.compress_channel(ycbcr[:,:,1], quality)
        compressed_cr, qm_cr = jpeg_compressor.compress_channel(ycbcr[:,:,2], quality)
        
        # Combine channels
        compressed = np.stack([compressed_y, compressed_cb, compressed_cr], axis=-1)
        
        # Convert back to RGB
        decompressed_y = jpeg_compressor.decompress_channel(compressed[:,:,0], qm_y)
        decompressed_cb = jpeg_compressor.decompress_channel(compressed[:,:,1], qm_cb)
        decompressed_cr = jpeg_compressor.decompress_channel(compressed[:,:,2], qm_cr)
        
        ycbcr = np.stack([decompressed_y, decompressed_cb, decompressed_cr], axis=-1)
        rgb = jpeg_compressor.ycbcr_to_rgb(ycbcr)
        
        # Convert to PIL Image and save to bytes
        output = Image.fromarray(rgb)
        img_io = io.BytesIO()
        output.save(img_io, 'JPEG', quality=quality)
        img_io.seek(0)

        logger.debug(f"Sending compressed image to client")
        
        return send_file(
            img_io,
            mimetype='image/jpeg',
            as_attachment=True,
            download_name='compressed.jpg'
        )
        
    except Exception as e:
        logger.error(f"Error during compression: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/hello')
def hello():
    return 'Hello World!'

if __name__ == "__main__":
    app.run(debug=True)