#!/usr/bin/python

import socket, inspect, threading, os, pickle, re, ConfigParser, subprocess, time
from threading import Timer
from JeevesCore import *

try:
    with open('servers.dat', 'rb') as f:
        servers = pickle.load(f)
except:
    config = ConfigParser.RawConfigParser()
    config.readfp(open('default.cfg'))
    servers = {config.get('default', 'server'):[config.get('default', 'nick'), config.get('default', 'pass'), [config.get('default', 'channel')]]}
    with open('servers.dat', 'wb') as f:
        pickle.dump(servers, f)

owner = "Shukaro"

comKey = '.'

class Server:

    def __init__(self, serv, port, nick, pw, chan):
        self.server = serv
        self.port = port
        self.nick = nick
        self.pw = pw
        self.chan = chan
        self.comKey = comKey
        self.owner = owner
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tag = self.server + ":" + str(self.port) + " :: "
        self.isConnected = False
        self.identified = False
        
    def connect(self):
        try:
            print("Connecting to " + self.server + ":" + str(self.port) + "...\r\n")
            self.irc.connect((self.server, self.port))
        except:
            print("Connection to " + self.server + ":" + str(self.port) + " failed.")
            exit(0)
        print("Connection to " + self.server + ":" + str(self.port) + " succeeded!")
        print(self.tag + "Sending USER")
        self.irc.send("USER " + self.nick + " 8 * :" + self.nick + "\r\n")
        print(self.tag + "Sending NICK")
        self.irc.send("NICK " + self.nick + '\r\n')
        print(self.tag + "Sending PASS")
        self.irc.send("PASS " + self.pw + '\r\n')
        self.isConnected = True
        print(self.tag + "Listening")
        self.listen()
    
    def listen(self):
        while self.isConnected:
            msg = self.irc.recv(4096)
            m = splitMsg(msg)

            #Respond to PING and identify if necessary
            if msg.find('PING :') != -1:
                print(self.tag + "Ponging with: " + msg[msg.find('PING :')+6:].strip('\r\n'))
                self.irc.send("PONG :" + msg[msg.find('PING :')+6:].strip('\r\n') + '\r\n')
                if not self.identified:
                    print(self.tag + "Identifying")
                    self.irc.send("PRIVMSG nickserv :identify " + self.pw + "\r\n")
                    self.identified = True
                    for c in self.chan:
                        joinChan(self, c)
            
            #Passing on tells
            if getCommand(m) == 'PRIVMSG':
                try:
                    with open('tells.dat', 'rb') as f:
                        data = pickle.load(f)
                except:
                    data = {}
                for key in data.keys():
                    if getNick(m).lower() == key:
                        if len(data[key]) != 0:
                            sendNtc(self, getNick(m), "You have " + str(len(data[key])) + " new message(s).")
                            for e in data[key]:
                                msg = e.split(' ', 2)
                                sendNtc(self, getNick(m), msg[0] + ' on ' + msg[1] + ' - ' + msg[2])
                            data[key] = []
                            with open('tells.dat', 'wb') as f:
                                pickle.dump(data, f)

            if getIgnore(m) and getNick(m) != self.owner:
                continue

            #Moniter for URLs
            urls = re.findall(r'(https?://\S+)', getMessage(self, m))
            for url in urls:
                if 'twitter.com' in url and '/status/' in url:
                    getTweet(self, m, url)
            
            #Command monitering
            if getCommand(m) == 'PRIVMSG' and getMessage(self, m).startswith(self.comKey):
                msg = getMessage(self, m)[1:].strip('\r\n')
                cmd = msg.split()[0]
                msg = msg[len(cmd)+1:]
                if cmd == 'tell':
                    tell(self, msg, getChannel(self, m), getNick(m))
                elif cmd == 'part':
                    part(self, msg, getChannel(self, m), getNick(m))
                elif cmd == 'join':
                    join(self, msg, getChannel(self, m), getNick(m))
                elif cmd == 'removechannel':
                    removechannel(self, msg, getChannel(self, m), getNick(m))
                elif cmd == 'addchannel':
                    addchannel(self, msg, getChannel(self, m), getNick(m))
                elif cmd == 'removeserver':
                    removeserver(self, msg, getChannel(self, m), getNick(m))
                elif cmd == 'addserver':
                    addserver(self, msg, getChannel(self, m), getNick(m))
                elif cmd == 'quit':
                    quit(self, msg, getChannel(self, m), getNick(m))
                elif cmd == 'ignore':
                    ignore(self, msg, getChannel(self, m), getNick(m))
                elif cmd == 'unignore':
                    unignore(self, msg, getChannel(self, m), getNick(m))
                elif cmd == 'ignorelist':
                    ignorelist(self, msg, getChannel(self, m), getNick(m))
                elif cmd == 'unignoreall':
                    unignoreall(self, msg, getChannel(self, m), getNick(m))

#Commands
def tell(self, m, c, n):
    data = {}
    try:
        with open('tells.dat', 'rb') as f:
            data = pickle.load(f)
    except:
        with open('tells.dat', 'wb') as f:
            pickle.dump(data, f, -1)
    try:
        nick = m.split(' ')[0].lower()
        message = m.split(' ', 1)[1]
    except:
        sendMsg(self, c, "Incorrect syntax, use " + self.comKey + "tell nick message")
        return
    try:
        data[nick].append(n + ' ' + getTimeStamp() + ' ' + message)
    except:
        data[nick] = []
        data[nick].append(n + ' ' + getTimeStamp() + ' ' + message)
    sendMsg(self, c, "I'll pass that along")
    with open('tells.dat', 'wb') as f:
        pickle.dump(data, f)

def ignore(self, m, c, n):
    if n != self.owner:
        sendMsg(self, c, "I\'m sorry, but only authorized users may do that.")
        return
    data = []
    try:
        with open('ignore.dat', 'rb') as f:
            data = pickle.load(f)
        if m in data:
            sendMsg(self, c, "Already ignoring " + m)
        else:
            sendMsg(self, c, "Ignoring " + m)
            data.append(m)
        with open('ignore.dat', 'wb') as f:
            pickle.dump(data, f)
    except:
        sendMsg(self, c, "Ignoring " + m)
        data.append(m)
        with open('ignore.dat', 'wb') as f:
            pickle.dump(data, f)

def unignore(self, m, c, n):
    if n != self.owner:
        sendMsg(self, c, "I\'m sorry, but only authorized users may do that.")
        return
    data = []
    try:
        with open('ignore.dat', 'rb') as f:
            data = pickle.load(f)
        if m in data:
            sendMsg(self, c, "Unignoring " + m)
            data.remove(m)
        else:
            sendMsg(self, c, "Already unignoring " + m)
        with open('ignore.dat', 'wb') as f:
            pickle.dump(data, f)
    except:
        sendMsg(self, c, "Already unignoring " + m)
        with open('ignore.dat', 'wb') as f:
            pickle.dump(data, f)

def unignoreall(self, m, c, n):
    if n != self.owner:
        sendMsg(self, c, "I\'m sorry, but only authorized users may do that.")
        return
    data = []
    sendMsg(self, c, "Clearing the ignore list")
    with open('ignore.dat', 'wb') as f:
            pickle.dump(data, f)

def ignorelist(self, m, c, n):
    if n != self.owner:
        sendMsg(self, c, "I\'m sorry, but only authorized users may do that.")
        return
    data = []
    try:
        with open('ignore.dat', 'rb') as f:
            data = pickle.load(f)
        sendMsg(self, c, "Ignoring the following ::")
        for m in data:
            sendMsg(self, c, m)
    except:
        sendMsg(self, c, "Ignoring nothing")

        
def part(self, m, c, n):
    if n != self.owner:
        sendMsg(self, c, "I\'m sorry, but only authorized users may do that.")
        return
    if not m.startswith("#"):
        sendMsg(self, c, "Incorrect syntax, use " + self.comKey + "part #chan")
        return
    sendMsg(self, c, "Parting " + m)
    self.irc.send("PART " + m + " :\r\n")
    
def join(self, m, c, n):
    if n != self.owner:
        sendMsg(self, c, "I\'m sorry, but only authorized users may do that.")
        return
    if not m.startswith("#"):
        sendMsg(self, c, "Incorrect syntax, use " + self.comKey + "join #chan")
        return
    sendMsg(self, c, "Joining " + m)
    self.irc.send("JOIN " + m + " :\r\n")
    
def removechannel(self, m, c, n):
    if n != self.owner:
        sendMsg(self, c, "I\'m sorry, but only authorized users may do that.")
        return
    if not m.startswith("#"):
        sendMsg(self, c, "Incorrect syntax, use " + self.comKey + "join #chan")
        return
    sendMsg(self, c, "Removing channel " + m)
    with open('servers.dat', 'rb') as f:
        servers = pickle.load(f)
    servers[self.server][2].remove(m)
    with open('servers.dat', 'wb') as f:
        pickle.dump(servers, f)
    part(self, m, c, n)
    
def addchannel(self, m, c, n):
    if n != self.owner:
        sendMsg(self, c, "I\'m sorry, but only authorized users may do that.")
        return
    if not m.startswith("#"):
        sendMsg(self, c, "Incorrect syntax, use " + self.comKey + "join #chan")
        return
    sendMsg(self, c, "Adding channel " + m)
    with open('servers.dat', 'rb') as f:
        servers = pickle.load(f)
    servers[self.server][2].append(m)
    with open('servers.dat', 'wb') as f:
        pickle.dump(servers, f)
    join(self, m, c, n)
    
def addserver(self, m, c, n):
    if n != self.owner:
        sendMsg(self, c, "I\'m sorry, but only authorized users may do that.")
        return
    try:
        with open('servers.dat', 'rb') as f:
            servers = pickle.load(f)
        sendMsg(self, c, "Adding " + m.split()[0] + " to the server list using the nick/pass combo \'" + m.split()[1] + " " + m.split()[2] + "\' and an empty channel list")
        servers[m.split()[0]] = [m.split()[1], m.split()[2], []]
        with open('servers.dat', 'wb') as f:
            pickle.dump(servers, f)
    except:
        sendMsg(self, c, "Incorrect syntax, use " + self.comKey + "addserver irc.example.net nick pass")
        
def removeserver(self, m, c, n):
    if n != self.owner:
        sendMsg(self, c, "I\'m sorry, but only authorized users may do that.")
        return
    with open('servers.dat', 'rb') as f:
        servers = pickle.load(f)
    sendMsg(self, c, "Removing " + self.server + " from serverlist")
    del servers[self.server]
    with open('servers.dat', 'wb') as f:
        pickle.dump(servers, f)
    quit(self, m, c, n)
    
def quit(self, m, c, n):
    if n != self.owner:
        sendMsg(self, c, "I\'m sorry, but only authorized users may do that.")
        return
    sendMsg(self, c, "Quitting " + self.server)
    goAway(self, "Bye")

#Boot 'er up
serverlist = {}
threads = {}
for s, d in servers.iteritems():
    serverlist[s] = Server(s, 6667, d[0], d[1], d[2])
    threads[s] = threading.Thread(None, serverlist[s].connect)
    threads[s].start()

 