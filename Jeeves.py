#!/usr/bin/python

import socket, inspect, threading, os, pickle, re, ConfigParser
import JeevesPlugins
from random import choice
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

#Phrase lists
comKey = '.'
goodbyes = ['Good-bye', 'I bid you adieu', 'Farewell']
work = ['One moment please...', 'Right away, sir.']
wrong = ['I\'m terribly sorry, but that is an invalid command.', 'My apologies, but that is wrong.', 'I\'m not sure I understand you.', 'Come again?']
commandlist = ['check', 'choose', 'google', 'help', 'tell', 'quiet', 'shutup', 'part', 'join', 'quit']
inGame = False

#Polling lists
repos = ['powercrystals/minefactoryreloaded', 'powercrystals/powercrystalscore', 'powercrystals/netherores']

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
        self.work = work
        self.commands = commandlist
        
    def connect(self):
        try:
            print("Connecting to " + self.server + ":" + str(self.port) + "...\r\n")
            self.irc.connect((self.server, self.port))
        except:
            print("Connection to " + self.server + ":" + str(self.port) + " failed.")
            exit(0)
        print("Connection to " + self.server + ":" + str(self.port) + " succeeded!")
        print(self.tag + "Sending PASS")
        self.irc.send("PASS " + self.pw + '\r\n')
        print(self.tag + "Sending NICK")
        self.irc.send("NICK " + self.nick + '\r\n')
        print(self.tag + "Sending USER")
        self.irc.send("USER " + self.nick + " 8 * :At your service\r\n")
        self.isConnected = True
        self.listen()
    
    def listen(self):
        while self.isConnected:
            msg = self.irc.recv(4096)
            m = splitMsg(msg)
            
            #Respond to PING and identify if necessary
            if m[1].find('PING') != -1:
                print(self.tag + "Ponging with: " + m[2][0].strip('\r\n'))
                self.irc.send("PONG :" + m[2][0] + '\r\n')
                if not self.identified:
                    print(self.tag + "Identifying")
                    self.irc.send("PRIVMSG nickserv :identify " + self.pw + "\r\n")
                    self.identified = True
                    for c in self.chan:
                        joinChan(self, c)
            
            if getShutup(m) and getNick(m) != owner:
                continue
                
            #Moniter for URLs
            urls = re.findall(r'(https?://\S+)', getMessage(self, m))
            for url in urls:
                if 'twitter.com' in url and '/status/' in url:
                    getTweet(self, m, url)
                if 'youtube.com' in url:
                    getYouTube(self, m, url)
            
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
                            if not inGame:
                                sendMsg(self, getNick(m), "You have " + str(len(data[key])) + " new messages.")
                            else:
                                sendMsg(self, getChannel(self, m), "You have " + str(len(data[key])) + " new messages.")
                            for e in data[key]:
                                msg = e.split(' ', 2)
                                if not inGame:
                                    sendMsg(self, getNick(m), msg[0] + ' on ' + msg[1] + ' said: \"' + msg[2] + '\"')
                                else:
                                    sendMsg(self, getChannel(self, m), msg[0] + ' on ' + msg[1] + ' said: \"' + msg[2] + '\"')
                            data[key] = []
                            with open('tells.dat', 'wb') as f:
                                pickle.dump(data, f)
            
            #Command monitering
            if getCommand(m) == 'PRIVMSG' and getMessage(self, m).startswith(self.comKey):
                if getQuiet(m) and getNick(m) != owner:
                    continue
                msg = getMessage(self, m)[1:].strip('\r\n')
                cmd = msg.split()[0]
                msg = msg[len(cmd)+1:]
                if cmd in commandlist:
                    msg = msg.replace('\'', '\\\'')
                    eval("JeevesPlugins." + cmd + "(self, \'" + msg + "\', getChannel(self, m), getNick(m))")
                else:
                    sendMsg(self, getChannel(self, m), choice(wrong))
                    sendMsg(self, getChannel(self, m), "Type " + self.comKey +  "help for a list of available commands")            

serverlist = {}
threads = {}
for s, d in servers.iteritems():
    serverlist[s] = Server(s, 6667, d[0], d[1], d[2])
    threads[s] = threading.Thread(None, serverlist[s].connect)
    threads[s].start()

 