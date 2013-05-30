#!/usr/bin/env python3

from aspell import Speller
from irc.bot import SingleServerIRCBot, ServerSpec
from random import choice
import re
import logging


insult_messages = [
    "Non, '{0}' n'existe pas dans la langue de Molière, désolé.",
    "Va t'acheter un dictionnaire, '{0}' n'est pas français.",
    "Apprends à écrire, tête de noeud, on ne dit pas '{0}'.",
    "'{0}', lol.",
    "Toi y-en-a bien parler la France, dis-donc. '{0}', VRAIMENT ?",
    "On ne dit PAS '{0}', bordel.",
    "'{0}'... mais qu'il est con celui-là.",
    "Je suis un Ortograph Nazi et je vous emmerde, mais on ne dit pas '{0}'"]

word_re = re.compile('[^\W\d_]+', re.UNICODE)

class OrthoNazi(SingleServerIRCBot):
    def __init__(self, server_list, nick="OrthoNazi", lang="fr_FR", channel="#test", **params):
        super().__init__(server_list, nick, "OrthoNazi", **params)
        self.channel = channel
        self.speller = Speller("lang", lang)

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_pubmsg(self, c, e):
        message = e.arguments[0]
        target = e.target
        for word in re.findall(word_re, message):
            if not self.speller.check(word):
                reply = choice(insult_messages).format(word)
                c.privmsg(target, reply)
                break

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    servers = [ServerSpec('some.irc-server.example.com', 6667)]
    bot = OrthoNazi(servers)
    bot.start()
