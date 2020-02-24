#!/usr/bin/env python
import socket
import os
import ftplib
import time

DEBUG_LEVEL=2
BENCH = 1
def store(ftp, cmd, fp):
    ftp.voidcmd('TYPE A')
    blocksize = 100
    with ftp.transfercmd(cmd) as conn:
        while 1:
            buf = fp.read(blocksize)
            if not buf:
                break
            conn.sendall(buf)
    return ftp.voidresp()
class Minimal(object):
    def __init__(self, mode=False):
        self.passive_mode=mode
        self.contet="1\n2\n123\n"

    def test1(self):
        """
            Test QUIT
        """
        fl = True
        ftp = ftplib.FTP()
        ftp.set_debuglevel(DEBUG_LEVEL)
        fl &= self.getrepl(ftp.connect(host, port)) == '2'
        ftp.login(username, password)
        fl &= self.getrepl(ftp.quit()) == '2'
        return fl
    def test2(self):
        """
            Test USER AQUIRED
        """
        fl = True
        ftp = ftplib.FTP()
        ftp.set_debuglevel(DEBUG_LEVEL)
        fl &= self.getrepl(ftp.connect(host, port)) == '2'
        try:
            fl &= self.getrepl(ftp.sendcmd('TYPE I')) == '5'
        except:
            fl = fl
            ftp.quit()
        else:
            fl = False
        return fl
    def test3(self):
        """
            Test USER
        """
        fl = True
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        ftp.set_debuglevel(DEBUG_LEVEL)
        fl &= self.getrepl(ftp.login(username, password)) == '2'
        ftp.quit()
        return fl
    def test4(self):
        """
            Test TYPE
        """
        fl = True
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        ftp.set_debuglevel(DEBUG_LEVEL)
        ftp.login(username, password)
        fl &= self.getrepl(ftp.sendcmd('TYPE A')) == '2'
        try:
            fl &= self.getrepl(ftp.sendcmd('TYPE Q')) == '5'
        except:
            fl = fl
        else:
            fl = False
        ftp.quit()
        return fl
    def test5(self):
        """
            Test MODE
        """
        fl = True
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        ftp.set_debuglevel(DEBUG_LEVEL)
        fl &= self.getrepl(ftp.login(username, password)) == '2'
        fl &= self.getrepl(ftp.sendcmd('MODE S')) == '2'
        try:
            fl &= self.getrepl(ftp.sendcmd('MODE NOTSTREAM')) == '5'
        except:
            fl = fl
        else:
            fl = False
        ftp.quit()
        return fl
    def test6(self):
        """
            Test STRU
        """
        fl = True
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        ftp.set_debuglevel(DEBUG_LEVEL)
        fl &= self.getrepl(ftp.login(username, password)) == '2'
        fl &= self.getrepl(ftp.sendcmd('STRU F')) == '2'
        try:
            fl &= self.getrepl(ftp.sendcmd('STRU NOTFILE')) == '5'
        except:
            fl = fl
        else:
            fl = False
        ftp.quit()
        return fl
    def test7(self):
        """
            Test NOOP
        """
        fl = True
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        ftp.login(username, password)
        ftp.set_debuglevel(DEBUG_LEVEL)
        fl &= self.getrepl(ftp.sendcmd('NOOP')) == '2'
        fl &= self.getrepl(ftp.sendcmd('noop')) == '2'
        fl &= self.getrepl(ftp.sendcmd('noOp')) == '2'
        fl &= self.getrepl(ftp.sendcmd('NoOp')) == '2'
        ftp.quit()
        return fl

    def test8(self):
        """
            Test STOR + RETR
        """
        filename='tmp.tmp'
        with open(filename, 'wb+') as fp:
            fp.write(self.contet.encode('ascii'))
        
        fl = True
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        ftp.login(username, password)
        
        ftp.set_debuglevel(DEBUG_LEVEL)
        ftp.set_pasv(self.passive_mode)
        
        with open(filename, 'rb') as fd:
            fl &= self.getrepl(store(ftp, "STOR " + filename, fd)) == '2'
        contet = ""
        with open(filename, 'wb+') as fd:
            with ftp.transfercmd("RETR " + filename) as dataConnection:
                while 1:
                    data = dataConnection.recv(10);
                    if not data:
                        break
                    fd.write(data);
                    contet += data.decode("ascii")
                fl &= self.getrepl(ftp.voidresp()) == '2'
        fl &= (contet == self.contet)

        ftp.quit()
        return fl
    def test9(self):
        """
            Test FALSE RETR
        """
        fl = True
        filename="no_such_file"
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        ftp.login(username, password)
        
        ftp.set_debuglevel(DEBUG_LEVEL)
        ftp.set_pasv(self.passive_mode)
        try:
            with open(filename, 'wb+') as fd:
                with ftp.transfercmd("RETR " + filename) as dataConnection:
                    while 1:
                        data = dataConnection.recv(10);
                        if not data:
                            break
                        fd.write(data);
                        contet += data.decode("ascii")
                    fl &= self.getrepl(ftp.voidresp()) == '2'
            fl &= (contet == self.contet)
        except:
            fl = fl
        else:
            fl= False
        ftp.quit()
        return fl

    def test10(self):
        """
            Test QUIT
        """
        fl = True
        ftp = ftplib.FTP()
        ftp.set_debuglevel(DEBUG_LEVEL)
        fl &= self.getrepl(ftp.connect(host, port)) == '2'
        ftp.login(username, password)
        try:
            fl &= self.getrepl(ftp.sendcmd('No such command')) == '5'
        except:
            fl = fl
        else:
            fl = False
        time.sleep(0.9)
        # fl &= self.getrepl(ftp.voidresp()) == '2'
        fl &= self.getrepl(ftp.quit()) == '2'
        return fl
    def test11(self):
        filename='tmp.tmp'
        with open(filename, 'wb+') as fp:
            for i in range(100000):
                fp.write('000'.encode('ascii'))
        fl = True
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        ftp.login(username, password)
        
        ftp.set_debuglevel(DEBUG_LEVEL)
        ftp.set_pasv(self.passive_mode)
        with open(filename, 'rb') as fp:
            fl &= self.getrepl(store(ftp, "STOR " + filename, fp)) == '2'
        with open(filename, 'rb') as fp:
            fl &= self.getrepl(store(ftp, "STOR " + filename + '1', fp)) == '2'
        with open(filename, 'rb') as fp:
            fl &= self.getrepl(store(ftp, "STOR " + filename + '2', fp)) == '2'
        
        ftp.quit()
        return fl
    def test12(self):
        filename='tmp.tmp'
        with open(filename, 'wb+') as fp:
            for i in range(100000):
                fp.write('000'.encode('ascii'))
        fl = True
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        ftp.login(username, password)
        
        ftp.set_debuglevel(DEBUG_LEVEL)
        # ftp.set_pasv(self.passive_mode)
        try:
            fl &= self.getrepl(ftp.sendcmd("STOR 1.cpp")) == '4'
        except:
            fl = fl
        else:
            fl = False
        ftp.quit()
        return fl
    def run_tests(self):
        result = True
        tests =[
                self.test1,
                self.test2,
                self.test3,
                self.test4,
                self.test5,
                self.test6,
                self.test7,
                self.test8,
                self.test9,
                self.test10,
                self.test11,
                self.test12,
                ]
        for i in range(BENCH):
            for test in tests:
                # print(test())
                try:
                    result &= test()
                except:
                    result = False
        
        return result

    def getrepl(self, message):
        return message.split(" ")[0][0]

class Dir(object):
    def __init__(self, mode=False):
        self.passive_mode=mode
        self.contet="1\n2\n123\n"

    def test1(self):
        """
            Test CDUP
        """
        fl = True
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        ftp.login(username, password)
        ftp.set_debuglevel(DEBUG_LEVEL)
        # ftp.nlst()
        # ftp.mkd("tmp")

        fl &= self.getrepl(ftp.sendcmd('CDUP')) == '2'
        fl &= self.getrepl(ftp.sendcmd('CDUP')) == '2'
        fl &= self.getrepl(ftp.sendcmd('CDUP')) == '2'
        fl &= self.getrepl(ftp.sendcmd('CDUP')) == '2'
        fl &= self.getrepl(ftp.sendcmd('CDUP')) == '2'
        fl &= self.getrepl(ftp.sendcmd('CDUP')) == '2'

        ftp.quit()

        return fl
    def test2(self):
        """
            Test CWD NO MKDIR
        """
        fl = True
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        ftp.login(username, password)
        ftp.set_debuglevel(DEBUG_LEVEL)
        try:
            fl &= self.getrepl(ftp.cwd("no_dir")) == '5'
        except:
            fl = fl
        else:
            fl = False
        fl &= self.getrepl(ftp.cwd("..")) == '2'
        ftp.quit()

        return fl
    def test3(self):
        """
            Test APPE
        """
        filename='appe.tmp'
        

        with open(filename, 'wb+') as fp:
            fp.write(self.contet.encode('ascii'))
        
        fl = True
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        ftp.login(username, password)
        
        ftp.set_debuglevel(DEBUG_LEVEL)
        ftp.set_pasv(self.passive_mode)

        try:
            ftp.sendcmd('DELE ' + filename)
        except:
            fl = fl
        with open(filename, 'rb') as fp:
            fl &= self.getrepl(store(ftp, "STOR " + filename, fp)) == '2'
        
        
        
        with ftp.transfercmd('APPE ' + filename) as conn:
            buf = "4321\n"
            conn.sendall(buf.encode('ascii'))
        ftp.voidresp()

        contet = ""
        
        with open(filename, 'wb+') as fd:
            with ftp.transfercmd("RETR " + filename) as dataConnection:
                while 1:
                    data = dataConnection.recv(10);
                    if not data:
                        break
                    fd.write(data);
                    contet += data.decode("ascii")
                fl &= self.getrepl(ftp.voidresp()) == '2'
        fl &= (contet == self.contet + buf)
        fl &= self.getrepl(ftp.sendcmd('DELE ' + filename)) == '2'
        ftp.quit()
        return fl

    def test4(self):
        """
            Test APPE + WR + DEL
        """
        fl = True
        filename='appeWrite.tmp'
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        ftp.login(username, password)
        
        ftp.set_debuglevel(DEBUG_LEVEL)
        ftp.set_pasv(self.passive_mode)
        try:
            ftp.sendcmd('DELE ' + filename)
        except:
            fl = fl
        
        with ftp.transfercmd('APPE ' + filename) as conn:
            buf = "4321\n"
            conn.sendall(buf.encode('ascii'))
        ftp.voidresp()
        
            
        contet = ""
        
        with open(filename, 'wb+') as fd:
            with ftp.transfercmd("RETR " + filename) as dataConnection:
                while 1:
                    data = dataConnection.recv(10);
                    if not data:
                        break
                    fd.write(data);
                    contet += data.decode("ascii")
                fl &= self.getrepl(ftp.voidresp()) == '2'
        fl &= (contet == buf)
        ftp.quit()
        return fl
    def test5(self):
        """
            Test DELE
        """
        filename='tmp.tmp'
        with open(filename, 'wb+') as fp:
            fp.write(self.contet.encode('ascii'))
        
        fl = True
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        ftp.login(username, password)
        
        ftp.set_debuglevel(DEBUG_LEVEL)
        ftp.set_pasv(self.passive_mode)
        with open(filename, 'rb') as fp:
            store(ftp, "STOR " + filename, fp)
        ftp.sendcmd('DELE ' + filename)
        try:
            fl &= self.getrepl(ftp.sendcmd('DELE ' + filename)) == '5'
        except:
            fl = fl
        else:
            fl = False
        ftp.quit()
        return fl
    def test6(self):
        """
            Test MKDIR + RMD + CD
        """
        fl = True
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        ftp.login(username, password)
        ftp.set_debuglevel(DEBUG_LEVEL)
        fl &= (ftp.mkd("test6").find("/test6") != -1)
        try:
            fl &= self.getrepl(ftp.mkd("test6")) == '5'
        except:
            fl = fl
        else:
            fl = False

        fl &= self.getrepl(ftp.cwd("test6")) == '2'
        ftp.cwd("..")
        fl &= self.getrepl(ftp.rmd("test6")) == '2'
        ftp.quit()

        return fl

    def test7(self):
        """
            Test MKDIR + RMD + CD + NLST
        """
        fl = True
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        ftp.set_pasv(self.passive_mode)
        ftp.login(username, password)
        ftp.set_debuglevel(DEBUG_LEVEL)
        try:
            ftp.rmd("test7")
        except:
            fl = fl

        ftp.mkd("test7")
        files = ['file1', 'file2', 'file3']
        for file in files:
            with ftp.transfercmd('APPE ' + "test7/" + file) as conn:
                buf = "4321\n"
                conn.sendall(buf.encode('ascii'))
            ftp.voidresp()
        dirs = ['dir1', 'dir2', 'dir3']
        for dir_ in dirs:
            ftp.mkd("test7/" + dir_)
        nlst=[]
        with ftp.transfercmd("NLST test7") as dataConnection:
                while 1:
                    data = dataConnection.recv(10);
                    if not data:
                        break
                    nlst += data.decode('ascii')
        for file in files:
            ftp.sendcmd('DELE ' + "test7/" + file)
        for dir_ in dirs:
            ftp.rmd("test7/" + dir_)
        ftp.rmd("test7")
        actual_dirs = list(map(lambda x: "test7/" + x, dirs)) + list(map(lambda x: "test7/" + x, files))
        actual_dirs.sort()
        fl &= ('\r\n'.join(actual_dirs)+'\r\n' == ''.join(nlst))
        ftp.quit()

        return fl
    def test8(self):
        filename='tmp.tmp'
        with open(filename, 'wb+') as fp:
            fp.write(self.contet.encode('ascii'))
        
        fl = True
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        ftp.login(username, password)
        
        ftp.set_debuglevel(DEBUG_LEVEL)
        ftp.set_pasv(self.passive_mode)
        with open(filename, 'rb') as fp:
            fl &= self.getrepl(store(ftp, "STOR " + filename, fp)) == '2'
        fl &= self.getrepl(ftp.sendcmd('CDUP')) == '2'
        fl &= self.getrepl(ftp.sendcmd('CDUP')) == '2'
        fl &= self.getrepl(ftp.sendcmd('CDUP')) == '2'
        fl &= self.getrepl(ftp.sendcmd('CDUP')) == '2'
        fl &= self.getrepl(ftp.sendcmd('CDUP')) == '2'
        fl &= self.getrepl(ftp.sendcmd('CDUP')) == '2'

        contet = ""
        with open(filename, 'wb+') as fd:
            with ftp.transfercmd("RETR " + filename) as dataConnection:
                while 1:
                    data = dataConnection.recv(10);
                    if not data:
                        break
                    fd.write(data);
                    contet += data.decode("ascii")
                fl &= self.getrepl(ftp.voidresp()) == '2'
        fl &= (contet == self.contet)

        ftp.quit()
        return fl
    def run_tests(self):
        result = True
        tests =[
                self.test1,
                self.test2,
                self.test3,
                self.test4,
                self.test5,
                self.test6,
                self.test7,
                self.test8,
                ]
        for i in range(BENCH):
            for test in tests:
                print(test())
                try:
                    result &= test()
                except:
                    result = False
        
        return result
                
    def getrepl(self, message):
        return message.split(" ")[0][0]

class Pasv(object):
    def __init__(self):
        self.contet="1\n2\n123\n"
        self.passive_mode=True

    def test1(self):
        """
            Test STOR + PASV
        """
        filename='tmp.tmp'
        with open(filename, 'wb+') as fp:
            fp.write(self.contet.encode('ascii'))
        
        fl = True
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        ftp.login(username, password)
        
        ftp.set_debuglevel(DEBUG_LEVEL)
        ftp.set_pasv(self.passive_mode)
        with open(filename, 'rb') as fp:
            fl &= self.getrepl(store(ftp, "STOR " + filename, fp)) == '2'
        ftp.quit()
        return fl
    def test2(self):
        """
            Test RETR + PASV
        """
        filename='tmp.tmp'
        contet = ""
        fl = True
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        ftp.login(username, password)
        
        ftp.set_debuglevel(DEBUG_LEVEL)
        ftp.set_pasv(self.passive_mode)
        with open(filename, 'wb+') as fd:
            with ftp.transfercmd("RETR " + filename) as dataConnection:
                while 1:
                    data = dataConnection.recv(10);
                    if not data:
                        break
                    fd.write(data);
                    contet += data.decode("ascii")
                fl &= self.getrepl(ftp.voidresp()) == '2'
        fl &= (contet == self.contet)

        ftp.quit()
        return fl
    def run_tests(self):
        result = True
        tests =[self.test1,
                self.test2,
                ]
        for i in range(BENCH):
            for test in tests:
                # print(test())
                try:
                    result &= test()
                except:
                    result = False
        
        return result
        
            

    def getrepl(self, message):
        return message.split(" ")[0][0]

class Pass(object):
    def __init__(self):
        self.contet="1\n2\n123\n"
        self.passive_mode=False

    def test1(self):
        """
            Test PASS
        """
        fl = True
        ftp = ftplib.FTP()
        ftp.set_debuglevel(DEBUG_LEVEL)
        ftp.connect(host, port)
        fl &= self.getrepl(ftp.sendcmd('USER ' + username)) == '3'
        fl &= self.getrepl(ftp.sendcmd('PASS ' + password)) == '2'

        ftp.quit()
        return fl
    def test2(self):
        """
            Test ILLIGAL NAME
        """
        fl = True
        ftp = ftplib.FTP()
        ftp.set_debuglevel(DEBUG_LEVEL)
        ftp.connect(host, port)

        try:
            fl &= self.getrepl(ftp.sendcmd('USER ' + "123username")) == '5'
        except:
            fl = fl
        else:
            fl = False
        fl &= self.getrepl(ftp.sendcmd('USER ' + username)) == '3'
        
        try:
            fl &= self.getrepl(ftp.sendcmd('PASS ' + "password")) == '5'
        except:
            fl = fl
        else:
            fl = False
        ftp.quit()
        return fl
    def test3(self):
        """
            Test CHANGE USERS
        """
        fl = True
        ftp = ftplib.FTP()
        ftp.set_debuglevel(DEBUG_LEVEL)
        ftp.connect(host, port)
        ftp.set_pasv(self.passive_mode)
        ftp.login(username, password)

        filename='tmp.tmp'
        with open(filename, 'wb+') as fp:
            fp.write(self.contet.encode('ascii'))
        
        fl = True
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        ftp.login(username, password)
        
        ftp.set_debuglevel(DEBUG_LEVEL)
        ftp.set_pasv(self.passive_mode)
        with open(filename, 'rb') as fp:
            fl &= self.getrepl(store(ftp, "STOR " + filename, fp)) == '2'
        
        ftp.login(username1, password1)
        try:
            contet = ""
            with open(filename, 'wb+') as fd:
                with ftp.transfercmd("RETR " + filename) as dataConnection:
                    while 1:
                        data = dataConnection.recv(10);
                        if not data:
                            break
                        fd.write(data);
                        contet += data.decode("ascii")
                    fl &= self.getrepl(ftp.voidresp()) == '2'
            fl &= (contet == self.contet)
        except:
            fl = fl
        else:
            fl = False
        ftp.quit()

        return fl
    def test4(self):
        """
            Test PASS?
        """
        fl = True
        ftp = ftplib.FTP()
        ftp.set_debuglevel(DEBUG_LEVEL)
        ftp.connect(host, port)
        fl &= self.getrepl(ftp.sendcmd('USER ' + username)) == '3'
        try:
            fl &= self.getrepl(ftp.sendcmd('CUP ' + password)) == '5'
        except:
            fl = fl
        else:
            fl = False

        ftp.quit()
        return fl
    def run_tests(self):
        result = True
        tests =[self.test1,
                self.test2,
                self.test3,
                self.test4,
                ]
        for i in range(BENCH):
            for test in tests:
                # print(test())
                try:
                    result &= test()
                except:
                    result = False
        return result
            

    def getrepl(self, message):
        return message.split(" ")[0][0]

class Block(object):
    def __init__(self):
        self.contet="1\n2\n123\n"
        self.passive_mode=False

    def test1(self):
        """
            Test RETR + STOR in BLOCK
        """
        fl = True
        ftp = ftplib.FTP()
        ftp.set_debuglevel(DEBUG_LEVEL)
        ftp.connect(host, port)
        ftp.set_pasv(self.passive_mode)
        ftp.login(username, password)
        
        host_port = ftp.sendcmd('MODE B')
        host_port = ftp.sendcmd('PASV')
        host_port = host_port.split(" ")[-1].replace(")","").replace("(","").replace(".","")
        host_loc = '.'.join(host_port.split(",")[:4])
        port_loc = int(host_port.split(",")[4]) * 256 + int(host_port.split(",")[5])
        
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
            sock.connect((host_loc,port_loc))
            ftp.sendcmd("STOR Block.tmp")
            contet = self.contet
            my_bytes = bytearray()
            my_bytes.append(64)
            len_ = len(contet.encode('ascii'))
            my_bytes.append(len_ // 256)
            my_bytes.append(len_ % 256)
            sock.sendall(my_bytes)
            sock.sendall(contet.encode('ascii'))
        ftp.voidresp()
        
        host_port = ftp.sendcmd('MODE B')
        host_port = ftp.sendcmd('PASV')
        host_port = host_port.split(" ")[-1].replace(")","").replace("(","").replace(".","")
        host_loc = '.'.join(host_port.split(",")[:4])
        port_loc = int(host_port.split(",")[4]) * 256 + int(host_port.split(",")[5])
        
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
            sock.connect((host_loc,port_loc))
            ftp.sendcmd("RETR Block.tmp")
            data = sock.recv(3)
            header = bytearray(data)
            descriptor = header[0]
            if descriptor != 64:
                fl = False
            length = header[1] * 256 + header[2]
            blocksize = 100 if length >= 100 else length
            new_content = ""
            while length > 0:
                buf = sock.recv(blocksize)
                length -= len(buf)
                new_content += buf.decode("ascii")
        ftp.voidresp()
        fl &= (contet == new_content)
        ftp.quit()
        return fl
    def run_tests(self):
        result = True
        tests =[self.test1
                ]
        for i in range(BENCH):
            for test in tests:
                # print(test())
                try:
                    result &= test()
                except:
                    result = False
        return result
            

    def getrepl(self, message):
        return message.split(" ")[0][0]

name_tests = {
    'minimal' : Minimal,
    'dir' : Dir,
    'passive' : Pasv,
    'auth' : Pass,
    'trans-mode-block': Block
}
if __name__ == '__main__':
    test = os.environ.get('HW1_TEST', 'all')
    port = os.environ.get('HW1_PORT', '21')
    host = os.environ.get('HW1_HOST', "0.0.0.0")
    DEBUG_LEVEL = 0 if os.environ.get('HW1_QUIET', '1') == '1' else 2 
    DEBUG_LEVEL = 2
    port = int(port)
    
    use_password = (os.environ.get('HW1_AUTH_DISABLED', "0") == '0')
    username='anonim'
    password ='password'
    if use_password:
        user_pass = os.environ.get('HW1_USERS', '/home/foxxmary/network/server/users')
        name_password = {}
        names = []
        with open(user_pass, 'r') as fp:
            fp.readline()
            for line in fp:
                [name, password] = line.strip().split(" ")
                names.append(name)
                name_password[name] = password
            username1 = names[0]
            password1 = name_password[names[0]]
            # username = names[1]
            # password = name_password[names[1]]
    
    if test != 'all':
        testing = name_tests[test]()
        result = testing.run_tests()
        if result:
            print('ok')
        else:
            print('fail')
    else:
        for test in name_tests:
            testing = name_tests[test]()
            result = testing.run_tests()
        if result:
            print('ok')
        else:
            print('fail')