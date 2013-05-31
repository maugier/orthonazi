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
    "'{0}', lol. Imbécile que tu fais, {1}.",
    "Toi y-en-a bien parler la France, dis-donc, {1}. '{0}', VRAIMENT ?",
    "{1}: on ne dit PAS '{0}', bordel.",
    "'{0}'... c'est dur d'être aussi con, vraiment.",
    "Je suis un Ortograph Nazi et j'emmerde {1}, on ne dit pas '{0}'",
    "{1}, t'es débile ou tu le fais exprès ? '{0}', franchement...",
    "Cotisons-nous pour offrir un Bescherelle à {1}, parce que dire des trucs comme '{0}'...",
    "'{0}'... tes profs de français se retournent dans leur tombe à l'heure qu'il est, {1}.",
    "Et le trophée de l'illettré de la semaine revient à {1} et son magnifique '{0}'",
    "{1}, on ne dit pas '{0}', espèce de porc-épic mal embouché",
    "'{0}'... mais tais-toi un peu, {1}, bougre d'extrait de crétin des Alpes.",
    ]

nick_re = re.compile('[^\W]+', re.UNICODE)
word_re = re.compile('^[^\W\d_]+$', re.UNICODE)
space_re = re.compile(r'[][(){}\s,;!?]+', re.UNICODE)

def RateLimiter(delay):
    cache = {}

    def recent(key):
        now = time()

        if key in cache and (now - cache[key]) < delay:
            return True
        
        cache[key] = now
        return False

    return recent
        
def get_words(message):
    return [word for word in space_re.split(message) if len(word) > 3 and word_re.match(word)]


class OrthoNazi(SingleServerIRCBot):
    def __init__(self, server_list, nick="OrthoNazi", langs=["fr_FR", "en_US"],
                 channels=["#test"], whitelist_path=None, delay=300, **params):
        super().__init__(server_list, nick, "OrthoNazi", **params)
        self.nazi_channels = channels
        self.spellers = [Speller("lang", lang) for lang in langs]
        self.rl = RateLimiter(delay)
        self.whitelist_path = whitelist_path
        try:
            with open(whitelist_path) as f:
                self.whitelist = pickle.load(f)
                logging.info("Whitelist loaded with {0} words".format(len(self.whitelist)))
        except:
            self.whitelist = {}
        self.whitelist = {nick.lower(): True}
            

    def save(self):
        if self.whitelist_path is not None:
            with open(self.whitelist_path, "wb") as f:
                pickle.dump(self.whitelist, f)

    def do_whitelist(self, msg):
        for word in get_words(msg):
            self.whitelist[word.lower()] = True
            logging.info("Adding {0} to whitelist".format(word))
            self.save()

    def check_word(self, word):
        return (word[0].isupper() 
                or word.lower() in self.whitelist 
                or any([s.check(word) for s in self.spellers]))

    def on_welcome(self, c, e):
        for chan in self.nazi_channels:
            c.join(chan)

    def on_namreply(self, c, e):
        for nick in nick_re.findall(e.arguments[2]):
            self.do_whitelist(nick)

    def on_join(self, c, e):
        self.do_whitelist(NickMask(e.source).nick)
        
    def on_nick(self, c, e):
        self.do_whitelist(e.target)

    def on_pubmsg(self, c, e):
        message = e.arguments[0]

        if message.startswith("!whitelist "):
            self.do_whitelist(message[11:])
            return

        for word in get_words(message):
            if self.check_word(word):
                continue
            if self.rl(e.source):
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
