import heapq
from collections import defaultdict
import numpy as np
from PIL import Image

class HuffmanNode:
    def __init__(self, pixel=None, freq=None):
        self.pixel = pixel
        self.freq = freq
        self.left = None
        self.right = None
    
    def __lt__(self, other):
        return self.freq < other.freq

def build_frequency_dict(image_array):
    freq_dict = defaultdict(int)
    for pixel in image_array.flatten():
        freq_dict[pixel] += 1
    return freq_dict

def build_huffman_tree(freq_dict):
    heap = [HuffmanNode(pixel, freq) for pixel, freq in freq_dict.items()]
    heapq.heapify(heap)
    
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(freq=left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)
    
    return heap[0]

def build_huffman_codes(node, code="", mapping=None):
    if mapping is None:
        mapping = {}
    
    if node.pixel is not None:
        mapping[node.pixel] = code
    else:
        build_huffman_codes(node.left, code + "0", mapping)
        build_huffman_codes(node.right, code + "1", mapping)
    
    return mapping

def compress_image(image_path):
    # Load the image
    img = Image.open(image_path)
    img_array = np.array(img)
    
    # Build frequency dictionary
    freq_dict = build_frequency_dict(img_array)
    
    # Build Huffman tree
    huffman_tree = build_huffman_tree(freq_dict)
    
    # Generate Huffman codes
    huffman_codes = build_huffman_codes(huffman_tree)
    
    # Compress the image
    compressed_data = ""
    for pixel in img_array.flatten():
        compressed_data += huffman_codes[pixel]
    
    # Convert binary string to bytes
    compressed_bytes = int(compressed_data, 2).to_bytes((len(compressed_data) + 7) // 8, byteorder='big')
    
    return compressed_bytes, huffman_tree, img_array.shape

def decompress_image(compressed_bytes, huffman_tree, shape):
    # Convert bytes back to binary string
    binary_data = ''.join(format(byte, '08b') for byte in compressed_bytes)
    
    # Traverse the Huffman tree to decode
    decoded_pixels = []
    current_node = huffman_tree
    for bit in binary_data:
        if bit == '0':
            current_node = current_node.left
        else:
            current_node = current_node.right
        
        if current_node.pixel is not None:
            decoded_pixels.append(current_node.pixel)
            current_node = huffman_tree
    
    # Reshape the decoded pixels into the original image shape
    decompressed_array = np.array(decoded_pixels[:np.prod(shape)], dtype=np.uint8).reshape(shape)
    return Image.fromarray(decompressed_array)

# Example usage
if __name__ == "__main__":
    input_image_path = "input_image.png"
    output_image_path = "decompressed_image.png"
    
    compressed_data, huffman_tree, original_shape = compress_image(input_image_path)
    decompressed_image = decompress_image(compressed_data, huffman_tree, original_shape)
    decompressed_image.save(output_image_path)
    
    print(f"Original image size: {os.path.getsize(input_image_path)} bytes")
    print(f"Compressed data size: {len(compressed_data)} bytes")
    print(f"Compression ratio: {len(compressed_data) / os.path.getsize(input_image_path):.2f}")