import subprocess, pickle
from JeevesCore import *
from random import choice

def check(self, m, c, n):
    if not m:
        sendMsg(self, c, "Invalid syntax, use " + self.comkey + "check address")
        return
    sendMsg(self, c, choice(self.work))
    if subprocess.call(['ping', m]) == 0:
        sendMsg(self, c, "It looks like " + m + " is up on my end!")
    else:
        sendMsg(self, c, "Oh no! " + m + " is dead!")

def choose(self, m, c, n):
    try:
        m.split(" ")[1]
    except:
        sendMsg(self, c, "Incorrect syntax, use " + self.comKey + "choose a b c etc")
        return
    sendMsg(self, c, choice(self.work) + " I choose " + choice(m.split(" ")))

def google(self, m, c, n):
    if not m:
        sendMsg(self, c, "Invalid syntax, use " + self.comkey + "google word(s)")
        return
    sendMsg(self, c, choice(self.work) + " http://lmgtfy.com/?q=" + m.replace(" ", "+"))

def help(self, m, c, n):
    sendMsg(self, c, "The following commands are available: " + ', '.join(self.commands))
    
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
        message = m.split(' ')[1]
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
    
def quiet(self, m, c, n):
    if n != self.owner:
        sendMsg(self, c, "You can\'t tell me what to do! YOU\'RE NOT MY REAL DAD!")
        return
    data = []
    try:
        with open('quiet.dat', 'rb') as f:
            data = pickle.load(f)
        if c in data:
            sendMsg(self, c, "Responding to commands again!")
            data.remove(c)
        else:
            sendMsg(self, c, "Not responding to commands anymore!")
            data.append(c)
        with open('quiet.dat', 'wb') as f:
            pickle.dump(data, f)
    except:
        sendMsg(self, c, "Not responding to commands anymore!")
        data.append(c)
        with open('quiet.dat', 'wb') as f:
            pickle.dump(data, f)
        
def shutup(self, m, c, n):
    if n != self.owner:
        sendMsg(self, c, "You can\'t tell me what to do! YOU\'RE NOT MY REAL DAD!")
        return
    data = []
    try:
        with open('shutup.dat', 'rb') as f:
            data = pickle.load(f)
        if c in data:
            sendMsg(self, c, "I shall speak again!")
            data.remove(c)
        else:
            sendMsg(self, c, "You won't hear a peep out of me!")
            data.append(c)
        with open('shutup.dat', 'wb') as f:
            pickle.dump(data, f)
    except:
        sendMsg(self, c, "You won't hear a peep out of me!")
        data.append(c)
        with open('shutup.dat', 'wb') as f:
            pickle.dump(data, f)
        
def part(self, m, c, n):
    if n != self.owner:
        sendMsg(self, c, "You can\'t tell me what to do! YOU\'RE NOT MY REAL DAD!")
        return
    if not m.startswith("#"):
        sendMsg(self, c, "Incorrect syntax, use " + self.comKey + "part #chan")
        return
    sendMsg(self, c, "Parting " + m)
    self.irc.send("PART " + m + " :\r\n")
    
def join(self, m, c, n):
    if n != self.owner:
        sendMsg(self, c, "You can\'t tell me what to do! YOU\'RE NOT MY REAL DAD!")
        return
    if not m.startswith("#"):
        sendMsg(self, c, "Incorrect syntax, use " + self.comKey + "join #chan")
        return
    sendMsg(self, c, "Joining " + m)
    self.irc.send("JOIN " + m + " :\r\n")
    
def quit(self, m, c, n):
    if n != self.owner:
        sendMsg(self, c, "You can\'t tell me what to do! YOU\'RE NOT MY REAL DAD!")
        return
    sendMsg(self, c, "Quitting " + self.server)
    self.goAway("Bye")