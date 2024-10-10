import os
from PIL import Image

def xor(byte1, byte2):
    repeated_key = (byte2 * (len(byte1) // len(byte2) + 1))[:len(byte1)]
    return bytes([b1 ^ b2 for b1, b2 in zip(byte1, repeated_key)])

def bits_to_text(bits):
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        chars.append(chr(int(byte, 2)))
    return ''.join(chars)

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

def extract_lsb(image_path, num_bits):
    img = Image.open(image_path)
    img = img.convert("RGB")
    
    pixels = list(img.getdata())
    
    secret_bits = ""
    for pixel in pixels:
        if len(secret_bits) < num_bits:
            secret_bits += str(pixel[0] & 1) 
        if len(secret_bits) < num_bits:
            secret_bits += str(pixel[1] & 1)
        if len(secret_bits) < num_bits:
            secret_bits += str(pixel[2] & 1)

        if len(secret_bits) >= num_bits:
            break
    
    secret_message = bits_to_text(secret_bits)
    return secret_message

def encrypt(pt, key):
    return xor(pt, key)

if __name__ == "__main__":
    pt = open('./encrypt.py','rb').read()
    ct = open('./encrypt.py.afd','rb').read()

    key = xor(pt,ct)[:8]

    files_list = list_files_in_directory('./')
    files_list.remove('./encrypt.py')
    files_list.remove('./solve.py')
    files_list.remove('./do_not_open.jpeg')

    for i in files_list:
        pt = open(i,'rb').read()

        with open('./org/' + i[1:-4], 'wb') as f:
            f.write(encrypt(pt,key))
            f.close()

    print("Done.....")

    secret_mesg = extract_lsb('./org/im7.png', 100 * 8) # gunakan 100 bytes telebih dahulu untuk menebak ukuran bytes dari secret msg yang ditingalkan
    print(secret_mesg)

    print("Done.....")
