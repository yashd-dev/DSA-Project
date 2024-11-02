import numpy as np
from PIL import Image

class SimpleJPEGCompressor:
    def __init__(self):
        # Standard JPEG quantization matrix for luminance (Y) channel
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
        
        ycbcr = rgb @ matrix.T
        ycbcr[:, :, 1:] += 128
        return ycbcr

    def ycbcr_to_rgb(self, ycbcr):
        """Convert YCbCr back to RGB color space"""
        matrix = np.array([
            [1, 0, 1.402],
            [1, -0.344136, -0.714136],
            [1, 1.772, 0]
        ])
        
        ycbcr = ycbcr.copy()
        ycbcr[:, :, 1:] -= 128
        
        rgb = ycbcr @ matrix.T
        return np.clip(rgb, 0, 255).astype(np.uint8)
    
    def dct2d(self, block):
        """Compute 2D Discrete Cosine Transform of an 8x8 block"""
        return np.round(np.fft.fftshift(np.fft.dct(np.fft.dct(block.T, norm='ortho').T, norm='ortho')))
    
    def idct2d(self, block):
        """Compute 2D Inverse Discrete Cosine Transform of an 8x8 block"""
        return np.round(np.fft.idct(np.fft.idct(np.fft.ifftshift(block).T, norm='ortho').T, norm='ortho'))
    
    def quantize_block(self, dct_block, quality_factor=50):
        """Quantize DCT coefficients using the quantization matrix scaled by quality factor"""
        scale = (100 - quality_factor) / 50 if quality_factor < 50 else 2 - (quality_factor / 50)
        q_matrix = np.clip(self.quantization_matrix * scale, 1, 255)
        return np.round(dct_block / q_matrix).astype(int)
    
    def dequantize_block(self, quantized_block, quality_factor=50):
        """Reverse the quantization by scaling back"""
        scale = (100 - quality_factor) / 50 if quality_factor < 50 else 2 - (quality_factor / 50)
        q_matrix = np.clip(self.quantization_matrix * scale, 1, 255)
        return (quantized_block * q_matrix).astype(float)

    def compress_channel(self, channel, quality_factor=50):
        """Compress a single channel by dividing into 8x8 blocks, applying DCT, and quantizing"""
        height, width = channel.shape
        compressed = np.zeros_like(channel, dtype=int)
        
        # Process 8x8 blocks
        for i in range(0, height, 8):
            for j in range(0, width, 8):
                block = channel[i:i+8, j:j+8] - 128  # Shift range to -128 to 127
                dct_block = self.dct2d(block)
                compressed[i:i+8, j:j+8] = self.quantize_block(dct_block, quality_factor)
                
        return compressed

    def decompress_channel(self, compressed, quality_factor=50):
        """Decompress a single channel by dequantizing and applying IDCT to 8x8 blocks"""
        height, width = compressed.shape
        decompressed = np.zeros_like(compressed, dtype=float)
        
        for i in range(0, height, 8):
            for j in range(0, width, 8):
                quantized_block = compressed[i:i+8, j:j+8]
                dequantized_block = self.dequantize_block(quantized_block, quality_factor)
                decompressed[i:i+8, j:j+8] = self.idct2d(dequantized_block) + 128  # Shift back to 0-255 range
                
        return np.clip(decompressed, 0, 255).astype(np.uint8)

    def compress(self, image, quality_factor=50):
        """Compress the input image"""
        img_array = np.array(image.convert('RGB'))
        
        # Convert to YCbCr color space
        ycbcr = self.rgb_to_ycbcr(img_array)
        
        # Compress each channel
        compressed_y = self.compress_channel(ycbcr[:, :, 0], quality_factor)
        compressed_cb = self.compress_channel(ycbcr[:, :, 1], quality_factor)
        compressed_cr = self.compress_channel(ycbcr[:, :, 2], quality_factor)
        
        # Return compressed data
        return (compressed_y, compressed_cb, compressed_cr), quality_factor

    def decompress(self, compressed, quality_factor=50):
        """Decompress the compressed image data"""
        compressed_y, compressed_cb, compressed_cr = compressed
        
        # Decompress each channel
        decompressed_y = self.decompress_channel(compressed_y, quality_factor)
        decompressed_cb = self.decompress_channel(compressed_cb, quality_factor)
        decompressed_cr = self.decompress_channel(compressed_cr, quality_factor)
        
        # Stack channels back and convert to RGB
        ycbcr = np.stack([decompressed_y, decompressed_cb, decompressed_cr], axis=-1)
        rgb = self.ycbcr_to_rgb(ycbcr)
        
        return Image.fromarray(rgb)
