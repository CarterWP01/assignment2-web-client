#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return data.split('\r\n\r\n', 1)[0].split('\n')[0].split()[1]

    def get_headers(self,data):
        return data.split('\r\n\r\n', 1)[0].split("\n")[1:]

    def get_body(self, data):
        return data.split('\r\n\r\n')[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        while True:
            part = sock.recv(1024)
            if not part:
                break  # No more data to read, exit the loop
            buffer.extend(part)
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        try:
            parsed_url = urllib.parse.urlparse(url)
            host = parsed_url.hostname

            port = parsed_url.port
            if port is None:
                port = 80

            path = parsed_url.path
            if path == '':
                path = '/'

            self.connect(host, port)

            # Send an HTTP GET request
            self.sendall(f'GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n')

            # Receive the response
            response = self.recvall(self.socket)

            headers = self.get_headers(response)
            body = self.get_body(response)
            code = self.get_code(response)

            return HTTPResponse(int(code), body)
        except Exception as e:
            return HTTPResponse(404, str(e))
        finally:
            self.socket.close()

    def POST(self, url, args=None):
        try:
            # Parse the URL to get host and port
            parsed_url = urllib.parse.urlparse(url)
            host = parsed_url.hostname
            port = parsed_url.port
            path = parsed_url.path
            # if path[0] == '/':
            #     path = path[1:] + '/'
            self.connect(host, port)

            # Prepare the headers and data for the POST request
            data = urllib.parse.urlencode(args) if args else ""

            headers = (f'Content-type: application/x-www-form-urlencoded\r\n'
                       f'Host: {host}\r\n'
                       f'Content-length: {len(data)}\r\n\r\n'
                       f'{data}')

            request = f'POST {path} HTTP/1.1\r\n{headers}'
            self.socket.sendall(request.encode('utf-8'))
            # Receive the response

            response = self.recvall(self.socket)
            code = self.get_code(response)
            body = self.get_body(response)

            # Return the HTTPResponse object
            return HTTPResponse(int(code), body)
        except Exception as e:
            print('POST request failed:', e)
            return HTTPResponse(404, str(e))
        finally:
            self.socket.close()

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ), )

