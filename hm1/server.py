#!/usr/bin/env python

import os
import socket
import threading
from pathlib import Path
from typing import Union
import gzip
import re
from socket import _GLOBAL_DEFAULT_TIMEOUT

CONTENT_DIR = os.environ.get('HW1_DIRECTORY', '/home/foxxmary/network/server/data')

def serve_ftp(connection: socket.socket):
    Logged_in = False
    Root_dir = None
    Cur_Mode ='S'
    def characters(sock):
        data = "initial data"
        line_characters = []
        while data:
            data = sock.recv(4096)
            print(data.decode('ascii'))
            for character in data:
                line_characters.append(chr(character))
                if len(line_characters) >= 2 and line_characters[-2] == '\r' and line_characters[-1] == '\n':
                    yield ''.join(line_characters[:-2])
                    line_characters = []
    def GetCommand(chars):
        request_line = next(chars)
        space = request_line.find(" ")
        if space == -1:
            return request_line.upper(), ''
        command, message = request_line[:space], request_line[space + 1:]
        return command.upper(), message

    def Send(sock, message):
        print("send:", message.encode('ascii'), flush=True)
        sock.sendall(message.encode('ascii'))
    def getDir():
        current_dir = os.getcwd()
        return current_dir
    def Ok(sock):
        ready_message = "150 Ok to connect\r\n"
        Send(sock, ready_message)
    def Read_dueto_Mode(sock, filename, mode='wb'):
        
        if Cur_Mode == 'S':
            blocksize = 1024
            with open(filename, mode) as fp:
                while 1:
                    buf = sock.recv(blocksize)
                    if not buf:
                        break
                    fp.write(buf)
            return 0
        elif Cur_Mode == 'B':
            data = sock.recv(3)
            header = bytearray(data)
            descriptor = header[0]
            length = header[1] * 256 + header[2]
            blocksize = 100 if length >= 100 else length
            print(descriptor, length, blocksize)
            with open(filename, mode) as fp:
                while length > 0:
                    buf = sock.recv(blocksize)
                    length -= len(buf)
                    if not buf:
                        break
                    fp.write(buf)
            return length
    def Write_dueto_Mode(sock, filename):
        if Cur_Mode == 'S':
            with open(filename, 'rb') as fp:
                blocksize = 1024
                while 1:
                    buf = fp.read(blocksize)
                    if not buf:
                        break
                    sock.sendall(buf)
            return 0
        elif Cur_Mode == 'B':
            with open(filename, 'rb') as fp:
                content = fp.read()
                
                length = len(content)
                descriptor = 64
                blocksize = 100 if length >= 100 else length
                
                header = bytearray()
                header.append(descriptor)
                header.append(length // 256)
                header.append(length % 256)

                sock.sendall(header)
                l = 0
                while l < length:
                    sock.sendall(content[l: min(l + blocksize, length)])
                    l = min(l + blocksize, length)
            return 0
    #==========================================================
    def User(sock, message):
        if not use_password:
            Send(sock, f"230 Logged {message} in.\r\n")
            return 'User', 'anonimous'
        else:
            if name_password.get(message) is not None:
                name = message
                Send(sock, f'331 Please specify the password.\r\n')
                command, message = GetCommand(chars)
                
                if command != 'PASS':
                    Send(sock, f'530 Please login with USER and PASS.\r\n')
                    return 'User', None
                
                if name_password[name] == message:
                    Send(sock, f"230 Logged {name} in.\r\n")
                    return 'User', name
                else:
                    Send(sock, f'530 Login incorrect.\r\n')
                    return 'User', None
            else:
                Send(sock, f'530 Permission denied\r\n')
                return 'User', None
    
    def Type(sock, message):
        if message != 'A' and  message != 'I' and message != 'A N' and message != 'L 8':
            Send(sock, f"500 Unrecognised TYPE command.\r\n")
        else:
            Send(sock, f"200 Switching to {message}\r\n")
        return 'Type', None
    
    def Mode(sock, message):
        if message != 'S' and message != 'B':
            Send(sock, f"500 Unrecognised MODE command.\r\n")
        else:
            Send(sock, f"200 Switching to {message}\r\n")
        return 'Mode', message

    def Stru(sock, message):
        if message != 'F':
            Send(sock, f"500 Unrecognised MODE command.\r\n")
        else:
            Send(sock, f"200 Switching to {message}\r\n")
        return 'Stru', None

    def Quit(sock, message):
        Send(sock, f"221 Goodbye.\r\n")
        return 'close connection', None
    
    def Noop(sock, message):
        Send(sock, f"200 NOOP ok.\r\n")
        return 'Noop', None

    def Retr(sock, message):
        dir_ = getDir()
        if os.path.exists(dir_ + '/' + message) and os.path.isfile(dir_ + '/' + message):
            Ok(connection)
            Write_dueto_Mode(sock, dir_ + '/' + message)
            return 'Retr', 'OK'
        else:
            Send(connection, f"550 Couldnt find file.\r\n")
        return 'Retr', None
    
    def Stor(sock, message):
        Ok(connection)
        dir_ = getDir()
        length = Read_dueto_Mode(sock, dir_+ '/' + message)
        if length != 0:
            Send(connection, f"550 Bad connection\r\n")
            return 'Stor', None
        return 'Stor', 'OK'
    
    def Cdup(sock, message):
        current_dir = os.getcwd()
        if current_dir != Root_dir:
            try:
                os.chdir('/'.join(current_dir.split('/')[:-1]))
            except:
                Send(sock, f"550 Failed.\r\n")
        Send(sock, f"250 Directory successfully changed.\r\n")
        return 'Cdup', None
    
    def Cwd(sock, message):
        current_dir = os.getcwd()
        if os.path.exists(current_dir + '/' + message):
            try:
                os.chdir(current_dir + '/' + message)
            except:
                Send(sock, f"550 Failed to change directory.\r\n")
            Send(sock, f"250 Directory successfully changed.\r\n")
        else:
            Send(sock, f"550 Failed to change directory.\r\n")
        return 'Cdup', None
    
    def Appe(sock, message):
        dir_ = getDir()
        Ok(connection)
        length = Read_dueto_Mode(sock, dir_ + '/' + message, mode='ab')
        if length != 0:
            Send(connection, f"550 Bad connection\r\n")
            return 'Appe', None
        return 'Appe', 'OK'
   
    def Dele(sock, message):
        dir_ = getDir()
        if os.path.exists(dir_ + '/' + message):
            try:
                os.remove(dir_ + '/' + message)
            except:
                Send(sock, f'550 Delete operation failed.\r\n')
            Send(sock, f'250 Delete operation successful.\r\n')
        else:
            Send(sock, f'550 Delete operation failed.\r\n')
        return 'Dele', None
    
    def Mkd(sock, message):
        dir_ = getDir()
        if os.path.exists(dir_ + '/' + message):
            Send(sock, f"550 Create directory operation failed.\r\n")
        else:
            try:
                os.mkdir(dir_ + '/' + message)
            except:
                Send(sock, f"550 Create directory operation failed.\r\n")
            Send(sock, f"257 \"/{message}\"created\r\n")
        return 'Mkd', None
    
    def Rmd(sock, message):
        dir_ = getDir()
        if os.path.exists(dir_ + '/' + message):
            try:
                os.rmdir(dir_ + '/' + message)
            except:
                Send(sock, f"550 Delete directory operation failed somehow.\r\n")
            else:
                Send(sock, f"250 \"/{message}\"deleted\r\n")
        else:
            Send(sock, f"550 Delete directory operation failed.\r\n")
        return 'Rmd', None
    
    def Nlst(sock, message):
        dir_ = os.getcwd()
        if message:
            dir_ = dir_ + '/' + message
        if os.path.exists(dir_) and os.path.isdir(dir_):
            Ok(connection)
            dirs = os.listdir(dir_)
            dirs = list(map(lambda x: message + '/' + x, dirs))
            dirs.sort()
            dirs = '\r\n'.join(dirs) + '\r\n'
            blocksize = 1024
            l = 0
            while 1:
                buf = dirs[l: min(l + blocksize, len(dirs))].encode('ascii')
                l = min(l + blocksize, len(dirs))
                if not buf:
                    break
                sock.sendall(buf)
            return 'Nlst', 'OK'
        else:
            Send(connection, f'500 No dir.')
        return 'Nlst', None
    
    def Port(sock, message):
        message = message.replace(")","")
        message = message.replace("(","")
        host = '.'.join(message.split(',')[:4])
        port = int(message.split(',')[4]) * 256 + int(message.split(',')[5])
        Send(sock, f"200 Got {host}:{port}\r\n")
        return 'Port', (host, port)

    def Pasv(sock, message):
        socket_port = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        host = sock.getsockname()[0]
        socket_port.bind((host, 0))
        port = socket_port.getsockname()[1]

        response = ','.join(host.split(".") + [str(port // 256), str(port % 256)])
        return 'Pasv', (socket_port, response)
    #==========================================================
    list_responses = {
        'USER' : User,
        'QUIT' : Quit,
        'PORT' : Port,
        'TYPE' : Type,
        'MODE' : Mode,
        'STRU' : Stru,
        'RETR' : Retr,
        'STOR' : Stor,
        'NOOP' : Noop,
        'CDUP' : Cdup,
        'CWD'  : Cwd,
        'APPE' : Appe,
        'DELE' : Dele,
        'MKD'  : Mkd,
        'RMD'  : Rmd,
        'NLST' : Nlst,
        'PASV' : Pasv,
    }
    
    list_port_passv = ['RETR', 'STOR', 'NLST', 'APPE']
    
    def PortModeThread(sock, host_port, chars):
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as socket_port:
            command, message = GetCommand(chars)
            if command not in list_responses:
                Send(connection, f'500 Unknown command {command}.\r\n')
                return
            elif command not in list_port_passv:
                return
            socket_port.connect(host_port)
            response_message, response = list_responses[command](sock=socket_port, message=message)
            if response:
                Send(sock, f'226 Transfer complete.\r\n')
    
    def PasvModeThread(sock, response, chars):
        socket_port, response = response
        socket_port.listen(1)
        Send(sock, f'227 Entering Passive Mode ({response}).\n')
        
        in_connection, in_addr = socket_port.accept()
        in_connection.settimeout(1.0)

        command, message = GetCommand(chars)
        if command not in list_responses:
            Send(connection, f'500 Unknown command {command}.\r\n')
            return
        elif command not in list_port_passv:
            return
        response_message, response = list_responses[command](sock=in_connection, message=message)
        
        if response:
            Send(sock, f'226 Transfer complete.\r\n')
        socket_port.close()
    with connection:
        chars = characters(connection)
        hello_message = "200 Hello, World!\r\n"
        Send(connection, hello_message)
        while True:
            command, message = GetCommand(chars)
            if command not in list_responses:
                Send(connection, f'500 Unknown command {command}.\r\n')
                continue
            print(command, message, flush=True)
            
            if command not in ['USER', 'QUIT'] and not Logged_in:
                Send(connection, f'530 Please login with USER.\r\n')
                continue

            if command in list_port_passv:
                Send(connection, f'425 Use PORT or PASV first.\r\n')
                continue
            response_message, response = list_responses[command](sock=connection, message=message)
            
            if response_message == 'close connection':
                break
            elif response_message == 'Mode':
                Cur_Mode = response
            elif response_message == 'User' and response is not None:
                Root_dir = CONTENT_DIR + '/' + response
                if not os.path.exists(Root_dir):
                    os.mkdir(Root_dir)
                os.chdir(Root_dir)
                Logged_in = True
            elif response_message == 'Port':
                PortModeThread(connection, response, chars)
            elif response_message == 'Pasv':
                PasvModeThread(connection, response, chars)

        connection.close()

def run_server(port, host, client_handler):
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(5)
        while True:
            in_connection, in_addr = server_socket.accept()
            in_connection.settimeout(2.0)
            print(f"200 Opened input connection with {in_addr}", flush=True)
            threading.Thread(target=client_handler, args=[in_connection]).start()

if __name__ == '__main__':
    mode = os.environ.get('HW1_MODE', 'server')
    test = os.environ.get('HW1_TEST', 'all')
    port = os.environ.get('HW1_PORT', '1234')
    host = os.environ.get('HW1_HOST', "0.0.0.0")
    use_password = (os.environ.get('HW1_AUTH_DISABLED', "0") == '0')
    if use_password:
        user_pass = os.environ.get('HW1_USERS', '/home/foxxmary/network/server/users')
        name_password = {}
        with open(user_pass, 'r') as fp:
            fp.readline()
            for line in fp:
                [name, password] = line.strip().split(" ")
                name_password[name] = password
    port = int(port)
    run_server(port=port, host=host, client_handler=serve_ftp)




