from twisted.words.protocols import irc
from twisted.internet import protocol, reactor
from collections import Counter
import random
import collections
import os, re
import train
#from pprint import pprint

class MarkovChain(object):
    def __init__(self):
        self.chain = collections.defaultdict(list)

    def add(self, sentence, ngram, write_to_file=False):
        if write_to_file:
            with open('babbling.txt', 'a') as f:
                f.write(sentence+'\n')
        buf = ['\n']*ngram
        for word in sentence.split():
            self.chain[tuple(buf)].append(word)
            del buf[0]
            buf.append(word)
        self.chain[tuple(buf)].append('\n')

    def generate(self, ngram, seed=None):
        random.seed(os.urandom(5))
        if seed:
            buf = seed.split()[:ngram]
            #message = [random.choice(self.chain[random.choice(self.chain.keys())])]
            if len (seed.split()) > ngram:
                message = buf[:ngram]
            else:
                for i in xrange(ngram-len(seed.split())):
                    buf.append(random.choice(
                        self.chain[random.choice(self.chain.keys())]))
        else:
            buf = list(random.choice(self.chain.keys()))
        #pprint(self.chain)
        message = buf[:]

        for i in xrange(1000):
            try:
                next_word = random.choice(self.chain[tuple(buf)])
            except IndexError:
                continue #ew - it's the self.chain[tuple(buf)]
                         #which may be blank, could check if contains
            if next_word == '\n':
                break
            message.append(next_word)
            del buf[0]
            buf.append(next_word)
        return ' '.join(message)
                

class EnvironmentStuff(object):
    def __init__(self):
        self.signins = Counter()
        self.signouts = Counter()
        self.kicks = Counter()
        self.markov = MarkovChain()
        self.commands = {"train": train_it, "clas": classify, "classify": classify} 

def classify(msg):
    print(msg)
    cat = train.classify(msg)
    if not cat:
        return "I have no thoughts on the matter."
    return cat.name

def train_it(fuck_off=None):
    train.do_training()
    return "trained!"

class Osvalbot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname) 

    def signedOn(self):
        print("adding babble")
        if os.path.exists("babbling.txt"):
            with open('babbling.txt', 'r') as f:
                for line in f:
                    #it's like it's java! #ohgod
                    self.factory.environment.markov.add(line, 2)
        for channel in self.factory.channels:
            self.join(channel)
        print("Signed on as "+self.nickname)

    def joined(self, channel):
        print ("Joined " +channel)
    def kickedFrom(self, channel, kicker, message):
        self.join(channel)
        self.say(channel, "If you don't like me, stop talking to and about me! :(")

    def privmsg(self, user, channel, msg):
        seeded = False
        commanding = False
        if not user:
            return
        if self.nickname in msg:
            msg = re.compile(self.nickname + "[:,]* ?", re.I).sub('',msg)
            if msg:
                print msg
                if msg[0] == '!':
                    commanding = True
                    commandmatch = re.match("!(\w*) ", msg)
                    if commandmatch:
                        print "firstmatch type"
                        command = commandmatch.group(1)
                    else:
                        commandmatch = re.match("!(.*)", msg)
                        command = commandmatch.group(1) #too many ifs
                    commandmatch = re.match("!"+command+" (.*)", msg)
                    if commandmatch:
                        command_args = commandmatch.group(1)
                    else:
                        command_args = None
                    print("command "+command)
                    if command_args :print(", args \""+command_args+"\"")
                elif msg[0] == '$':
                    msg = msg[1:]
                    seeded = True
                prefix = "%s: " % (user.split('!', 1)[0],)
        else:
            prefix =''
        
        if prefix or random.random() <= self.factory.chattiness:
            if seeded:
                sentence = self.factory.environment.markov.generate(2, seed=msg)
            elif commanding:
                sentence = str(self.factory.environment.commands[command](command_args))
            else:
                sentence = self.factory.environment.markov.generate(2)
            if sentence:
                self.msg(channel, prefix+sentence.lstrip())
        else:
            self.factory.environment.markov.add(msg, 2, write_to_file=True)


class OsvalbotFactory(protocol.ClientFactory):
    protocol = Osvalbot

    def __init__(self, channels=["#stacs", "#stacs2"], nickname="osvalbot", chattiness=0.01):
        self.channels = channels
        self.nickname = nickname
        self.environment = EnvironmentStuff()
        self.chattiness = chattiness

    def clientConnectionLost(self, connector, reason):
        print "connection lost"
        connector.connect()

    def clientConnectionFailed(self, connector,reason):
        print ("Could not connect: "+reason)
        reactor.stop()

if __name__ == "__main__":
    reactor.connectTCP('irc.freenode.net', 6667, OsvalbotFactory())
    reactor.run()
