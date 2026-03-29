import io
from PIL import Image

DELIMITER = "1111111111111110"

def text_to_binary(text: str) -> str:
    """Converts a UTF-8 string to a binary string representation and appends delimiter."""
    bytes_data = text.encode('utf-8')
    binary_message = ''.join(format(b, '08b') for b in bytes_data)
    return binary_message + DELIMITER

def binary_to_text(binary_data: str) -> str:
    """Converts a binary string back to a UTF-8 string."""
    all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]
    byte_array = bytearray()
    for b in all_bytes:
        if len(b) == 8:
            byte_array.append(int(b, 2))
    return byte_array.decode('utf-8', errors='replace')

def encode(image_bytes: bytes, secret_message: str) -> bytes:
    """Encodes a secret message into an image using LSB steganography."""
    image = Image.open(io.BytesIO(image_bytes))
    
    # Ensure image has RGB channels to modify
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGBA")
        
    binary_message = text_to_binary(secret_message)
    data_len = len(binary_message)
    
    pixels = list(image.getdata())
    
    # Calculate maximum capacity in bits
    # We modify the LSB of R, G, B components (first 3 channels)
    max_bits = len(pixels) * 3
    
    if data_len > max_bits:
        raise ValueError("Image is too small to hold the given message.")
        
    encoded_pixels = []
    bit_index = 0
    
    for pixel in pixels:
        new_pixel = list(pixel)
        # Modify RGB (always indices 0, 1, 2)
        for i in range(3):
            if bit_index < data_len:
                # Modify the LSB: clear it with bitwise AND, set it with bitwise OR
                new_pixel[i] = (new_pixel[i] & ~1) | int(binary_message[bit_index])
                bit_index += 1
        encoded_pixels.append(tuple(new_pixel))
        
    # Reconstruct the image
    encoded_image = Image.new(image.mode, image.size)
    encoded_image.putdata(encoded_pixels)
    
    # Save as PNG to avoid compression loss
    output_buffer = io.BytesIO()
    encoded_image.save(output_buffer, format="PNG")
    return output_buffer.getvalue()

def decode(image_bytes: bytes) -> str:
    """Decodes a secret message from an image using LSB steganography."""
    image = Image.open(io.BytesIO(image_bytes))
    
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGBA")
        
    pixels = list(image.getdata())
    
    binary_data = ""
    delimiter_len = len(DELIMITER)
    
    for pixel in pixels:
        for i in range(3):
            binary_data += str(pixel[i] & 1)
            
            # Check if we hit the delimiter
            if len(binary_data) >= delimiter_len and binary_data[-delimiter_len:] == DELIMITER:
                actual_binary = binary_data[:-delimiter_len]
                return binary_to_text(actual_binary)
                
    raise ValueError("No hidden message found in the image (delimiter missing).")
