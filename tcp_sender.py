import socket


class TCP_sender:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        self.sock.connect((host, port))

    def write_logs(self, data):
        logs = open('logs_sender.txt', 'a')
        logs.write(str(data) + '\n')
        logs.close()

    def send_data(self, data):
        data = self.sock.sendall(data.encode())
        return data

    def disconnect(self):
        self.sock.close()
