#!/usr/bin/env python
import os
import socket
import threading
from threading import Thread, Lock
import json
import time
users_lock = Lock()
cars_lock = Lock()
online_users = []
class Car:
    def __init__(self, model, color, year, price):
        self.color = color.lower()
        self.model = model.lower()
        self.year = int(year)
        self.price = int(price)
    def __str__(self):
        return f'{self.model} {self.color} {self.year} {self.price}'
    def getModel(self):
        return self.model
    def getColor(self):
        return self.color
    def getYear(self):
        return self.year
    def getPrice(self):
        return self.price
    def __eq__(self, other):
        return self.color == other.color and self.model == other.model and self.year == other.year and self.price == other.price
def serve_ftp(connection: socket.socket):
    admin = False
    def characters(sock):
        data = "initial data"
        line_characters = []
        while data:
            data = sock.recv(4096)
            for character in data:
                line_characters.append(chr(character))
                if len(line_characters) >= 2 and line_characters[-2] == '\r' and line_characters[-1] == '\n':
                    yield ''.join(line_characters[:-2])
                    line_characters = []
    def GetCommand(chars):
        request_line = next(chars)
        data = json.loads(request_line)
        try:
            data['command']
            data['data']
            print("GOT:", json.dumps(data, indent=4, sort_keys=True))
            return data
        except:
            print(f"Bad JSON", flush=True)
    def CreateJson(command, message, data=""):
        return json.dumps({'command': command, "message": message, "data": data}, sort_keys=True)
    def SendJSON(sock, message):
        print("SEND:", message, flush=True)
        connection.sendall((message + '\r\n').encode())
    def Hello(sock, chars):
        data = GetCommand(chars)
        if data['command'] != "HELLO":
            SendJSON(connection, CreateJson("ERR", "Please, login first"))
        else:
            username = data['data']['username']
            SendJSON(connection, CreateJson("PASSWD", "Please, type password"))
            return Password(sock, chars, username)
    def Password(sock, chars, username, retry=True):
        data = GetCommand(chars)
        if data['command'] != "PASSWD":
            SendJSON(connection, CreateJson("ERR", "Please, login first"))
            return
        
        with users_lock:
            if name_password.get(username) == None:
                name_password[username] = data['data']['password']
                with open(user_pass, 'a+') as fp:
                    fp.write(username + " " + data['data']['password']+ "\n")
                SendJSON(connection, CreateJson("OK", "Welocme, " + username))
                online_users.append(username)
            elif name_password[username] == data['data']['password']:
                SendJSON(connection, CreateJson("OK", "Welocme, " + username))
                online_users.append(username)
            else:
                users_lock.release()
                if retry:
                    SendJSON(connection, CreateJson("ERR", "Wrong password")) 
                    return Password(sock, chars, username, retry=False)
                Bye(sock, None, username)
                return False
        users_lock.release()
        return username
    def Bye(sock, data, username):
        SendJSON(sock, CreateJson("BYE", "See you next time, " + username))
    def Help(sock, data, username):
        SendJSON(sock, CreateJson("HELP", "You can Sell car by typping\n SELL\n" + \
        "Or buy car by typping\n BUY \nor quit by typping \n BYE \nHave a nice shopping:)"))
    def KeepAlive(sock, data, username):
        message = ""
        if admin:
            message = "Online:\n" + '\n'.join(online_users) + "\nUsers:\n" +'\n'.join(name_password.keys())
        SendJSON(connection, CreateJson("OK", message))
        time.sleep(0.5)
    def Buy(sock, data, username):
        with cars_lock:
            cur_cars = cars.copy()

        if data['data'] != "ALL":
            try:
                approp_cars = list(filter(lambda x: \
                              ((data['data']['model'][0] == "all") or (x.getModel() in data['data']['model'])) and \
                              ((data['data']['color'][0] == "all") or (x.getColor() in data['data']['color']))and \
                              ((data['data']['year'][1] == "all") or (x.getYear() <= int(data['data']['year'][1]))) and\
                              ((data['data']['year'][0] == "all") or (x.getYear() >= int(data['data']['year'][0]))) and \
                              ((data['data']['price'][1] == "all") or (x.getPrice() <= int(data['data']['price'][1]))) and\
                              ((data['data']['price'][0] == "all") or (x.getPrice() >= int(data['data']['price'][0]))), cur_cars))
            except:
                SendJSON(sock, CreateJson("ERR", "Something gone wrong"))
            else:
                SendJSON(sock, CreateJson("LIST", "Listing cars:\n", "\n".join(list(map(str, approp_cars)))))
        else:
            SendJSON(sock, CreateJson("LIST", "Listing cars:\n", "\n".join(list(map(str, cur_cars)))))
    def Take(sock, data, username):
        with cars_lock:
            try:
                wantedCar = Car(data['data']['model'], data['data']['color'], int(data['data']['year']), int(data['data']['price']))
            except:
                SendJSON(sock, CreateJson("ERR", "Something gone wrong"))
            else:
                if wantedCar in cars:
                    ind = cars.index(wantedCar)
                    cars.pop(ind)
                    SendJSON(connection, CreateJson("OK", "Good choice!\nYOU GOT IT:)"))
                    with open(cars_file, 'w') as fp:
                        for car in cars:
                            fp.write(str(car) + '\n')
                else:
                    SendJSON(connection, CreateJson("OK", "We are so sorry, we don't have this car"))
    def Sell(sock, data, username):
        try:
            newCar = Car(data['data']['model'], data['data']['color'], int(data['data']['year']), int(data['data']['price']))
        except:
            SendJSON(sock, CreateJson("ERR", "Something gone wrong"))
        else:
            with cars_lock:
                if newCar.getPrice() < 1500000:
                    cars.append(newCar)
                    with open(cars_file, 'a+') as fp:
                        fp.write(str(newCar) + '\n')
                    SendJSON(connection, CreateJson("OK", "Deal)"))
                else:
                    SendJSON(connection, CreateJson("OK", "We are so sorry, its too expesive"))
    list_responses = {
        "HELP" : Help,
        "BYE" : Bye, 
        "KEEPALIVE" : KeepAlive,
        "SELL" : Sell,
        "BUY" : Buy,
        "TAKE" : Take,
    }
    with connection:
        chars = characters(connection)
        username = Hello(connection, chars)
        if username == "admin":
            admin = True
        if username:
            while 1:
                try:
                    data = GetCommand(chars)
                except socket.timeout:
                    with users_lock:
                        if username in online_users:
                            online_users.remove(username)
                if data['command'] not in list_responses:
                    SendJSON(connection, CreateJson("ERR", "Wrong commannd"))
                    continue
                list_responses[data['command']](connection, data, username)
                if data['command'] == 'BYE':
                    break
            connection.close()
    with users_lock:
        if username in online_users:
            online_users.remove(username)
 
def run_server(port, host, client_handler):
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(5)
        while True:
            in_connection, in_addr = server_socket.accept()
            in_connection.setblocking(0)
            in_connection.settimeout(1000.0)
            print(f"200 Opened input connection with {in_addr}", flush=True)
            threading.Thread(target=client_handler, args=[in_connection]).start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '1235'))
    host = os.environ.get('HOST', "0.0.0.0")
    user_pass = os.environ.get('USERS', '/home/foxxmary/network/server/users')
    cars_file = os.environ.get('CARS', '/home/foxxmary/network/server/cars')
    name_password = {}
    with open(user_pass, 'r') as fp:
        # fp.readline()
        for line in fp:
            [name, password] = line.strip().split()
            name_password[name] = password
    # print(name_password)
    cars = []
    with open(cars_file, 'r') as fp:
        for line in fp:
            [model, color, year, price] = line.strip().split()
            cars.append(Car(model, color, year, price))
        # print(cars)
    run_server(port=port, host=host, client_handler=serve_ftp)




