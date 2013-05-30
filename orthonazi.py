#!/usr/bin/env python3

from aspell import Speller
from irc.bot import SingleServerIRCBot, ServerSpec
from irc.client import NickMask
from random import choice
from time import time
import re
import logging
import pickle


insult_messages = [
    "Non, {1} '{0}' n'existe pas dans la langue de Molière, désolé.",
    "Va t'acheter un dictionnaire, {1}, '{0}' n'est pas français.",
    "Apprends à écrire, tête de noeud, on ne dit pas '{0}'.",
    "'{0}', lol. Quel idiot ce {1}.",
    "Toi y-en-a bien parler la France, dis-donc, {1}. '{0}', VRAIMENT ?",
    "{1}: on ne dit PAS '{0}', bordel.",
    "'{0}'... mais qu'il est con celui-là.",
    "Je suis un Ortograph Nazi et j'emmerde {1}, mais on ne dit pas '{0}'"]

word_re = re.compile('[^\W\d_]+', re.UNICODE)

class RateLimiter(object):
    #TODO add a deque to prune old entries to prevent unbounded growth
    def __init__(self, delay):
        self.cache = {}
        self.delay = delay

    def recent(self, key):
        now = time()

        if key in self.cache and (now - self.cache[key]) < self.delay:
            return True
        
        self.cache[key] = now
        return False
        
        


class OrthoNazi(SingleServerIRCBot):
    def __init__(self, server_list, nick="OrthoNazi", lang="fr_FR", 
                 channels=["#test"], whitelist_path=None, delay=300, **params):
        super().__init__(server_list, nick, "OrthoNazi", **params)
        self.nazi_channels = channels
        self.speller = Speller("lang", lang)
        self.rl = RateLimiter(delay)
        self.whitelist_path = whitelist_path
        try:
            with open(whitelist_path) as f:
                self.whitelist = pickle.load(f)
        except:
            self.whitelist = {}
        self.whitelist = {nick: True}
            

    def save(self):
        if self.whitelist_path is not None:
            with open(self.whitelist_path, "wb") as f:
                pickle.dump(self.whitelist, f)

    def do_whitelist(self, msg):
        for word in re.findall(word_re, msg):
            self.whitelist[word] = True
            logging.info("Adding {0} to whitelist".format(word))
            self.save()

    def on_welcome(self, c, e):
        for chan in self.nazi_channels:
            c.join(chan)

    def on_namreply(self, c, e):
        self.do_whitelist(e.arguments[2])

    def on_join(self, c, e):
        self.do_whitelist(NickMask(e.source).nick)

    def on_pubmsg(self, c, e):
        message = e.arguments[0]

        if message.startswith("!whitelist "):
            self.do_whitelist(message[11:])
            return

        for word in re.findall(word_re, message):
            if word in self.whitelist or self.speller.check(word):
                continue
            if self.rl.recent(e.source):
                logging.info("Grace time allowed to {0}".format(e.source))
                break

            reply = choice(insult_messages).format(word, NickMask(e.source).nick)
            c.privmsg(e.target, reply)
            break

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    servers = [ServerSpec('some.irc-server.example.com', 6667)]
    bot = OrthoNazi(servers)
    bot.start()
