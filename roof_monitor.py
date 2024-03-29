import socket
import threading
import re
import configparser
import time

def load_config():
    config = configparser.ConfigParser()
    config.read('roof_status.conf')
    return config['DEFAULT']['server_address'], int(config['DEFAULT']['server_port']), config['DEFAULT']['status_file_path']

def roof_server_polling(server_address, server_port, status_file_path):
    while True:
        try:
            with socket.create_connection((server_address, server_port), timeout=10) as sock:
                sock.settimeout(10.0)
                while True:
                    data = sock.recv(1024).decode('utf-8')
                    if not data:
                        raise Exception("Connection closed by the server")
                    print(f"Data from Roof Server: {data}")
                    match = re.search(r'Stat=\s*(\d)', data)
                    if match:
                        stat = int(match.group(1))
                        roof_status = 0 if stat == 0 else 1
                        update_status_file(status_file_path, roof_status)
                    else:
                        update_status_file(status_file_path, 2)

        except socket.timeout:
            print("Connection timed out. Attempting to reconnect...")
            update_status_file(status_file_path, 2)

        except Exception as e:
            print(f"Connection error: {e}")
            update_status_file(status_file_path, 2)

        print("Attempting to reconnect in 10 seconds...")
        time.sleep(10)

def update_status_file(status_file_path, status):
    try:
        with open(status_file_path, "w") as file:
            file.write(str(status))
        print(f"Updated roof status to {status} in {status_file_path}")
    except Exception as e:
        print(f"Error updating status file: {e}")

if __name__ == "__main__":
    server_address, server_port, status_file_path = load_config()
    # Start roof server monitoring in a separate thread
    thread = threading.Thread(target=roof_server_polling, args=(server_address, server_port, status_file_path))
    thread.start()
