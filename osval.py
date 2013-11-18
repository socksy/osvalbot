from twisted.words.protocols import irc
from twisted.internet import protocol, reactor
from counter import Counter
import random
import collections
import os, re
import train

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
        if seed:
            buf = seed.split()[:ngram]
            #message = [random.choice(self.chain[random.choice(self.chain.keys())])]
            if len (seed.split()) > ngram:
                message = buf[:]
            else:
                message = []
                for i in xrange(ngram):
                    message.append(random.choice(
                        self.chain[random.choice(self.chain.keys())]))
        else:
            buf = list(random.choice(self.chain.keys()))
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
        self.commands = { "pos":lambda x: x*3}
        

class Osvalbot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname) 

    def signedOn(self):
        print("adding babble")
        if os.path.exists("babble.txt"):
            with open('babble.txt', 'r') as f:
                for line in f:
                    #it's like it's java! #ohgod
                    self.factory.environment.markov.add(line)
        self.join(self.factory.channel)
        print("Signed on as "+self.nickname)

    def joined(self, channel):
        print ("Joined " +channel)
    def kickedFrom(self, channel, kicker, message):
        self.join(channel)
        self.say(channel, "If you don't like me, stop talking to and about me! :(")

    def privmsg(self, user, channel, msg):
        seeded = False
        if not user:
            return
        if self.nickname in msg:
            msg = re.compile(self.nickname + "[:,]* ?", re.I).sub('',msg)
            if msg[0] == '!':
                self.factory.environment.commands[msg[1:]](msg)
            elif msg[0] == '$':
                msg = msg[1:]
                seeded = True
            prefix = "%s: " % (user.split('!', 1)[0],)
        else:
            prefix =''
        
        self.factory.environment.markov.add(msg, 2, write_to_file=True)
        if prefix or random.random() <= self.factory.chattiness:
            if seeded:
                sentence = self.factory.environment.markov.generate(2, seed=msg)
            else:
                sentence = self.factory.environment.markov.generate(2)
            if sentence:
                self.msg(self.factory.channel, prefix+sentence)


class OsvalbotFactory(protocol.ClientFactory):
    protocol = Osvalbot

    def __init__(self, channel="#stacs", nickname="osvalbot", chattiness=0.01):
        self.channel = channel
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
