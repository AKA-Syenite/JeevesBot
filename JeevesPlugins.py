import subprocess, pickle
from JeevesCore import *
from random import choice

def check(self, m, c, n):
    if not m:
        sendMsg(self, c, "Invalid syntax, use " + self.comkey + "check address")
        return
    sendMsg(self, c, choice(self.work))
    if subprocess.call(['ping', m]) == 0:
        sendMsg(self, c, "It looks like " + m + " is up on my end.")
    else:
        sendMsg(self, c, "My condolences, " + m + " appears to be down.")

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
    
def quiet(self, m, c, n):
    if n != self.owner:
        sendMsg(self, c, "I\'m sorry, but only authorized users may do that.")
        return
    data = []
    try:
        with open('quiet.dat', 'rb') as f:
            data = pickle.load(f)
        if c in data:
            sendMsg(self, c, "Certainly. I\'ll resume responding to commands now.")
            data.remove(c)
        else:
            sendMsg(self, c, "I\'ll refrain from responding to commands from now on.")
            data.append(c)
        with open('quiet.dat', 'wb') as f:
            pickle.dump(data, f)
    except:
        sendMsg(self, c, "I\'ll refrain from responding to commands from now on.")
        data.append(c)
        with open('quiet.dat', 'wb') as f:
            pickle.dump(data, f)
        
def shutup(self, m, c, n):
    if n != self.owner:
        sendMsg(self, c, "I\'m sorry, but only authorized users may do that.")
        return
    data = []
    try:
        with open('shutup.dat', 'rb') as f:
            data = pickle.load(f)
        if c in data:
            sendMsg(self, c, "As you wish. I\'ll resume my usual functions.")
            data.remove(c)
        else:
            sendMsg(self, c, "I\'ll refrain from speaking from now on.")
            data.append(c)
        with open('shutup.dat', 'wb') as f:
            pickle.dump(data, f)
    except:
        sendMsg(self, c, "I\'ll refrain from speaking from now on.")
        data.append(c)
        with open('shutup.dat', 'wb') as f:
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
            sendMsg(self, c, "As you wish. I\'ll respond to " + m + " again.")
            data.remove(m)
        else:
            sendMsg(self, c, "I\'ll refrain from speaking to " + m + " from now on.")
            data.append(m)
        with open('ignore.dat', 'wb') as f:
            pickle.dump(data, f)
    except:
        sendMsg(self, c, "I\'ll refrain from speaking to " + m + " from now on.")
        data.append(c)
        with open('shutup.dat', 'wb') as f:
            pickle.dump(data, f)
        
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
        sendMsg(self, c, "Incorrect syntax, use " + self.comKey + "addserver irc.example.net")
        
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