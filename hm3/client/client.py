#!/usr/bin/env python
import socket
import os
import json
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
        # print("GOT:", json.dumps(data, indent=4, sort_keys=True), data['command'], data['data'])
        return data
    except:
        print(f"Bad JSON", flush=True)
def Ok(chars):
    data = GetCommand(chars)
    if data['message']:
        print(data['message'])
    if data['data']:
        print(data['data'])
    return data['command']
def SendJSON(connection, message):
    connection.sendall((message + '\r\n').encode())
def Hello(connection, username):
    SendJSON(   connection, 
                json.dumps({'command': "HELLO", "data": {"username": username}}, sort_keys=True)
            )
def LogIn(connection, password):
    SendJSON(   connection, 
                json.dumps({'command': "PASSWD", "data": {"password": password}}, sort_keys=True)
            )
def Help(connection):
    SendJSON(   connection, 
                json.dumps({'command': "HELP", "data": ""}, sort_keys=True)
            )
def Bye(connection):
    SendJSON(connection, json.dumps({'command': "BYE", "data": ""}, sort_keys=True))
def KeepAlive(connection):
    SendJSON(connection, json.dumps({'command': "KEEPALIVE", "data": ""}, sort_keys=True))
def Buy(connection, message):
    SendJSON(connection, json.dumps({'command': "BUY", "data": message}, sort_keys=True))
def Sell(connection, message):
    SendJSON(connection, json.dumps({'command': "SELL", "data": message}, sort_keys=True))
def Take(connection, message):
    SendJSON(connection, json.dumps({'command': "TAKE", "data": message}, sort_keys=True))
if __name__ == '__main__':
    port = os.environ.get('PORT', '1235')
    host = os.environ.get('HOST', "0.0.0.0")
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
            try:
                sock.connect((host,int(port)))
            except:
                print("Sorry, server is not avaliable")
            else:
                sock.settimeout(100.0)
                chars = characters(sock)
                print(f"Hello! It's the right time to buy or sell car!")
                username = input("Username: ")
                Hello(sock, username)
                Ok(chars)
                password = input("Password: ")
                LogIn(sock, password)
                currnet_answer = Ok(chars)
                if  currnet_answer != "OK":
                    password = input("One more time: ")
                    LogIn(sock, password)
                    currnet_answer = Ok(chars)
                while currnet_answer != "BYE":
                    command = input("Your command (may use \"HELP\"): ")
                    if command == "HELP":
                        Help(sock)
                    elif command == "BYE":
                        Bye(sock)
                    elif command == "BUY":
                        all_ = input("Would yoy like see all park? (y/n): ")
                        if all_ == 'y':
                            Buy(sock, "ALL")
                        else:
                            models = (input("Please, type models you would like (if all, type all): ")or "all").replace(",", " ").strip(" ").split()
                            colors = (input("Please, type colors you would like (if all, type all): ") or "all").replace(",", " ").strip(" ").split()
                            years = [input("Please, type the lowest year (if all, type all): ") or "all", input("Plese, type the highest year (if all, type all): ") or "all"]
                            prices = [input("Please, type the lowest price (if all, type all): ") or "all", input("Plese, type the highest price (if all, type all): ") or "all"]
                            Buy(sock, {"model" : models, 'color': colors, 'year':years, 'price':prices})
                        if Ok(chars) == "ERR":
                            continue
                        answer = input("Would you like to buy anything? (y/n): ")
                        if answer == "y":
                            try:
                                [model, color, year, price] = input("Please, type model, color, year and price of the car:").replace(",", " ").strip().split()
                            except:
                                print("Something wrong")
                                continue
                            Take(sock, {"model" : model, 'color': color, 'year':year, 'price':price})
                        else:
                            continue
                    elif command == "SELL":
                        print("Please, describe your car")
                        
                        [model, color, year, price] = input("Please, type model, color, year and price of the car:").replace(",", " ").strip().split()
                        if model.find("all") != -1 or color.find("all") != -1 or year.find("all") != -1 or price.find("all") != -1:
                            print("Bad word all")
                            continue
                        try:
                            int(year)
                            int(price)
                        except:
                            print("Something wrong")
                            continue
                        Sell(sock, {"model" : model, 'color': color, 'year':year, 'price':price})
                    else:
                        KeepAlive(sock)
                        print("Please, try one more time")
                        Ok(chars)
                        continue
                    currnet_answer = Ok(chars)
