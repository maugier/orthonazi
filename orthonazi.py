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
    "Non, {1} « {0} » n'existe pas dans la langue de Molière, désolé.",
    "Je crois qu'on achève les {1} qui écrivent « {0} »",
    "{1} vient de perdre son temps à parler.",
    "Va t'acheter un dictionnaire, {1}, « {0} » n'est pas français.",
    "Apprends à écrire, tête de noeud, on ne dit pas « {0} ».",
    "« {0} », lol. Imbécile que tu fais, {1}.",
    "Toi y-en-a bien parler la France, dis-donc, {1}. « {0} », VRAIMENT ?",
    "{1}: on ne dit PAS « {0} », bordel.",
    "« {0} »... c'est dur d'être aussi con, vraiment.",
    "Je suis un Ortograph Nazi et j'emmerde {1}, on ne dit pas « {0} ».",
    "{1}, t'es débile ou tu le fais exprès ? « {0} », franchement...",
    "Cotisons-nous pour offrir un Bescherelle à {1}, parce que dire des trucs comme « {0} »...",
    "« {0} »... tes profs de français se retournent dans leurs tombes à l'heure qu'il est, {1}.",
    "Et le trophée de l'illettré de la semaine revient à {1} et son magnifique « {0} »",
    "{1}, on ne dit pas « {0} », espèce de porc-épic mal embouché",
    "« {0} »... mais tais-toi un peu, {1}, bougre d'extrait de crétin des Alpes.",
    "Assez, {1}, pauvre Polichinelle analphabète, avec tes « {0} »",
    "Infâme patte de poulet prussienne en crinoline, {1} n'écrivez plus jamais {0} sous mes yeux !",
    "{1}, vil personnage... « {0} » , vraiment ?!",
    "Le fouet, le fouet, qu'on m'apporte un fouet pour {1}, l'impie qui écrivit « {0} » !",
    "{1}... La majeure en est inepte, la mineure impertinente, et la conclusion ridicule ! On ne peut dire « {0} », non, vraiment.",
    "Plutôt que d'accorder, {1}, qu'il faille dire « {0} » j'accorderais que datur vacuum in rerum natura, et que je suis en java !",
    "Décidément, mon chat est plus doué que {1} en français, parce que « {0} »...",
    "{1} n'est pas loin de mériter une médaille pour son ineptie. « {0} » ?",
    "{1}: Maraud, faquin, butor de pied plat ridicule ! « {0} »...",
    "Tiens, on dirait {2} quand {1} parle... « {0} »",
    "ERREUR: {1}: Cerveau non trouvé. Pas étonnant, à le lire (« {0} »...).",
    "« {0} »... je me sens sale, rien que de lire {1}.",
    "Pitié, quelqu'un, faites taire {1}... qui pourrait sinon continuer à dire des aberrations comme « {0} »",
    "En l'occurrence, l'imbécillité de {1} n'est pas un dilemme étymologique, avec ses superbes « {0} »",
    ]

nick_re = re.compile('[^\W]+', re.UNICODE)
word_re = re.compile('^[^\W\d_]+$', re.UNICODE)
space_re = re.compile(r'[][(){}\s,;!?]+', re.UNICODE)
trump_re = re.compile(r'\(.*gueule.*\)', re.UNICODE)

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
                 channels=["#test"], whitelist_path=None, delay=300, 
                 victim="un débile profond", **params):
        super().__init__(server_list, nick, "OrthoNazi", **params)
        self.nazi_channels = channels
        self.spellers = [Speller("lang", lang) for lang in langs]
        self.rl = RateLimiter(delay)
        self.whitelist_path = whitelist_path
        self.whitelist = {nick.lower(): True}
        self.victim = victim
        self.load()
            
    def load(self):
        try:
            with open(self.whitelist_path) as f:
                for line in f:
                    self.whitelist[line.rstrip()] = True
            logging.info("Whitelist loaded with {0} words".format(len(self.whitelist)))
        except Exception as e:
            logging.warning("Failed to load whitelist: {0}".format(e))

    def save(self):
        if self.whitelist_path is not None:
            with open(self.whitelist_path, "w") as f:
                for l in self.whitelist:
                    f.write(l + '\n')

    def do_whitelist(self, msg):
        for word in get_words(msg):
            self.whitelist[word.lower()] = True
            logging.info("Adding {0} to whitelist".format(word))
        self.save()

    def do_blacklist(self, msg):
        for word in get_words(msg):
            del self.whitelist[word.lower()]
            logging.info("Removing {0} from whitelist".format(word))
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

    def on_kick(self, c, e):
        nick = e.arguments[0]
        chan = e.target
        if nick == c.get_nickname():
            self.victim = NickMask(e.source).nick
            logging.info("New revenge victim: {0}".format(self.victim))
            c.join(chan)

        
    def on_nick(self, c, e):
        self.do_whitelist(e.target)

    def on_pubmsg(self, c, e):
        message = e.arguments[0]

        if message.startswith("!whitelist "):
            self.do_whitelist(message[11:])
            return

        elif message.startswith("!blacklist "):
            self.do_blacklist(message[11:])
            return

        elif trump_re.search(message):
            logging.info("{0} used trump card".format(e.source))
            return

        for word in get_words(message):
            if self.check_word(word):
                continue
            if self.rl(e.source):
                logging.info("Grace time allowed to {0}".format(e.source))
                break

            reply = choice(insult_messages).format(word, NickMask(e.source).nick, self.victim)
            c.privmsg(e.target, reply)
            break

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    servers = [ServerSpec('some.irc-server.example.com', 6667)]
    bot = OrthoNazi(servers)
    bot.start()
