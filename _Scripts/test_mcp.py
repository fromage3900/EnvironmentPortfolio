import socket
s = socket.socket()
s.settimeout(2)
result = s.connect_ex(('127.0.0.1', 9316))
print(f'Port 9316: OPEN' if result == 0 else 'Port 9316: CLOSED')
s.close()