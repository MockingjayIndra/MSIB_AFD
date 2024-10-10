import os
from PIL import Image

KEY = os.urandom(8)

def text_to_bits(text):
    return ''.join(format(ord(char), '08b') for char in text)

def embed_lsb(image_path, secret_file, output_image_path):
    img = Image.open(image_path)
    img = img.convert("RGB")
    
    pixels = list(img.getdata())
    
    with open(secret_file, 'r') as file:
        secret_text = file.read()
    
    secret_bits = text_to_bits(secret_text)
    
    if len(secret_bits) > len(pixels) * 3:
        raise ValueError("Image is too small to hold the secret text.")
    
    encoded_pixels = []
    bit_index = 0
    for pixel in pixels:
        if bit_index < len(secret_bits):
            r = pixel[0] & ~1 | int(secret_bits[bit_index])  # Modify LSB of red
            bit_index += 1
        else:
            r = pixel[0]

        if bit_index < len(secret_bits):
            g = pixel[1] & ~1 | int(secret_bits[bit_index])  # Modify LSB of green
            bit_index += 1
        else:
            g = pixel[1]

        if bit_index < len(secret_bits):
            b = pixel[2] & ~1 | int(secret_bits[bit_index])  # Modify LSB of blue
            bit_index += 1
        else:
            b = pixel[2]

        encoded_pixels.append((r, g, b))

    encoded_pixels.extend(pixels[len(encoded_pixels):])

    encoded_img = Image.new(img.mode, img.size)
    encoded_img.putdata(encoded_pixels)
    
    encoded_img.save(output_image_path)
    print(f"Secret message embedded into {output_image_path}")

def list_files_in_directory(directory_path):
    files = []
    try:
        for entry in os.listdir(directory_path):
            full_path = os.path.join(directory_path, entry)
            if os.path.isfile(full_path):
                files.append(full_path)
    except FileNotFoundError:
        print(f"The directory {directory_path} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return files

def xor(byte1, byte2):
    repeated_key = (byte2 * (len(byte1) // len(byte2) + 1))[:len(byte1)]
    return bytes([b1 ^ b2 for b1, b2 in zip(byte1, repeated_key)])

def encrypt(pt, key):
    return xor(pt, key)

if __name__ == "__main__":
    embed_lsb('./im7.png', 'secret.txt', './im7_new.png')

    files_list = list_files_in_directory('./')
    files_list.remove('./secret.txt')
    files_list.remove('./whoopzzz.jpeg')

    for i in files_list:
        pt = open(i,'rb').read()

        with open(i + '.afd', 'wb') as f:
            f.write(encrypt(pt,KEY))
            f.close()

    print("Done Encrypting.....")