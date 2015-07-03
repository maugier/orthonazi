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
    "« {0} »… c'est dur d'être aussi con, vraiment.",
    "Je suis un Ortograph Nazi et j'emmerde {1}, on ne dit pas « {0} ».",
    "{1}, t'es débile ou tu le fais exprès ? « {0} », franchement…",
    "Cotisons-nous pour offrir un Bescherelle à {1}, parce que dire des trucs comme « {0} »…",
    "« {0} »… tes profs de français se retournent dans leurs tombes à l'heure qu'il est, {1}.",
    "Et le trophée de l'illettré de la semaine revient à {1} et son magnifique « {0} »",
    "{1}, on ne dit pas « {0} », espèce de porc-épic mal embouché",
    "« {0} »… mais tais-toi un peu, {1}, bougre d'extrait de crétin des Alpes.",
    "Assez, {1}, pauvre Polichinelle analphabète, avec tes « {0} »",
    "Infâme patte de poulet prussienne en crinoline, {1} n'écrivez plus jamais {0} sous mes yeux !",
    "{1}, vil personnage… « {0} » , vraiment ?!",
    "Le fouet, le fouet, qu'on m'apporte un fouet pour {1}, l'impie qui écrivit « {0} » !",
    "{1}… La majeure en est inepte, la mineure impertinente, et la conclusion ridicule ! On ne peut dire « {0} », non, vraiment.",
    "Plutôt que d'accorder, {1}, qu'il faille dire « {0} » j'accorderais que datur vacuum in rerum natura, et que je suis en java !",
    "Décidément, mon chat est plus doué que {1} en français, parce que « {0} »…",
    "{1} n'est pas loin de mériter une médaille pour son ineptie. « {0} » ?",
    "{1}: Maraud, faquin, butor de pied plat ridicule ! « {0} »…",
    "Tiens, on dirait {2} quand {1} parle… « {0} »",
    "ERREUR: {1}: Cerveau non trouvé. Pas étonnant, à le lire (« {0} »…).",
    "« {0} »… je me sens sale, rien que de lire {1}.",
    "Pitié, quelqu'un, faites taire {1}… qui pourrait sinon continuer à dire des aberrations comme « {0} »",
    "En l'occurrence, l'imbécillité de {1} n'est pas un dilemme étymologique, avec ses superbes « {0} »",
    "{1}, si les analphabètes volaient, tu serais chef d'escadrille. « {0} ».",
    "{1}, ta connerie n'a d'égale que ma lassitude à lire tes ridicules  « {0} ».",
    "Fais gaffe, {1}, si un jour tu visites une école primaire, ils risquent de ne pas te laisser repartir. En tout cas jusqu'a ce que tu arrêtes de dire des choses comme « {0} ».",
    "« {0} ». Pauvre {1}, tu as si peu de neurones que même Frankenstein ne pourrait rien faire de ton cerveau.",
    "« {0} ». En fait, {1} c'est le produit d'un accouplement entre {2} et un manchot attardé.",
    "« {0} »… {1} dit tellement de merde qu'on n'arrive plus a savoir de quel coté est sa bouche ou son cul.",
    "« {0} »… faut croire que le jour de la distribution des cerveaux, {1} était aux chiottes.",
    "« {0} »… {1}, on t'a déja félicité pour ta culture ? Eh ben on t'a menti.",
    "« {0} »… je parie que pour halloween, {1} se déguise en dictionnaire.",
    "« {0} »… quand on lit {1}, on se dit qu'il doit forcément lui manquer quelques doigts. Au moins 10, en fait.",
    "« {0} »… Vous savez comment les écoliers arrivent à passer le bac ? En ne s'appelant pas {1}.",
    "« {0} »… il y a moins de confiture dans les placards de ma grand-mère que dans la boîte cranienne de {1}",
    "« {0} »… {1}, tu écris tellement mal qu'on pourrait croire que tu te sers d'une manette de XBox à la place d'un clavier",
    "« {0} »… au moins, quand on voit à quel point {1} est stupide, on en oublie sa laideur",
    "« {0} »… {1} c'est une sorte d'Ent en fait. Mi-humain, mi-gland.",
    "« {0} »… J'imagine que le contenu de la cervelle de {1} doit ressembler à une cuvette de chiottes après un régime de tarte aux pruneaux.",
    "« {0} »… si on installait dix mille babouins devant des machines à écrire, ils arriveraient encore a produire moins de fautes que {1}.",
    "« {0} »… Allez, courage, {1}, d'ici quelques années peut-être que la médecine moderne sera capable de réparer tes dommages cérébraux.",
    "« {0} »… {1} écrit encore plus merdiquement qu'une fosse septique défectueuse",
    "« {0} »… Et le huitième jour, Dieu créa {1}. Pour déconner.",
    "Bon sang {1}, la prochaine fois, préviens les gens quand tu prévois d'écrire aussi mal, j'ai failli m'étouffer.",
    "Il paraît qu'il existe un monde parallèle où le mot « {0} » existe, et un autre où {1} n'est pas complètement stupide.",
    "Allez, un peu de pédagogie. Laissons {1} se relire et se corriger",
    "« {0} »… Qui a encore une fois laissé rentrer {1} sur le chan ?",
    "« {0} »… Salut {1}, je suis ton futur employeur, et je ne t'embaucherai jamais",
    "{1}… Je ne sais pas si « {0} » existe dans ton monde imaginaire, mais dans le monde réel ce n'est pas le cas",
    "« {0} »… Regardez ! {1} tente de communiquer avec nous, c'est mignon !",
    "« {0} »… D'aucuns bougent comme Jagger, {1} préfère écrire comme Ducobu",
    "« {0} »… Ton truc c'était la gym {1}, avoue.",
    "« {0} »… J'ai l'impression de corriger {1} sans arrêt, et pourtant j'ai un cooldown.",
    "Non, {1}, « {0} » n'existe pas. Et non, je ne la fermerai pas.",
    "« {0} »… {1}, je me lève, et je te bouscule, et tu écris super mal, comme d'habitude.",
    "« {0} »… On dirait que {1} a pris ses cours de français sur Langochat.",
    "« {0} »… Tu sais, {1}, si le français n'est pas ta langue maternelle, il fallait nous le dire.",
    "Il y a les gens normaux qui écrivent correctement, et puis il y a {1} qui nous sort « {0} ». Comme quoi on tolère n'importe qui ici.", 
    ]

nick_re = re.compile('[^\W]+', re.UNICODE)
word_re = re.compile('^[^\W\d_]+$', re.UNICODE)
space_re = re.compile(r'[][(){}\s,;!?]+', re.UNICODE)
trump_re = re.compile(r'\(.*(gueule|tglb).*\)', re.UNICODE)
onom_re = re.compile(r'([a-z]+)\1\1', re.UNICODE)

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
                 channels=["#test"], whitelist_path=None, delay=300, trump_delay=10,
                 victim="un débile profond", **params):
        super().__init__(server_list, nick, "OrthoNazi", **params)
        self.nazi_channels = channels
        self.spellers = [Speller("lang", lang) for lang in langs]
        self.rl = RateLimiter(delay)
        self.trump_rl = RateLimiter(trump_delay)
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
            try:
                del self.whitelist[word.lower()]
                logging.info("Removing {0} from whitelist".format(word))
            except KeyError:
                pass
        self.save()

    def check_word(self, word):
        return ((word[0].isupper() and any(x.islower() for x in word))
                or onom_re.search(word)
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

        def by_oper():
            chan = self.channels[e.target]
            nick = NickMask(e.source).nick
            allow = (chan.is_oper(nick) or 
                     chan.is_halfop(nick) or
                     chan.is_voiced(nick))

            if not allow:
                c.privmsg(e.target, "{0}: dis-donc, tête de noeud, tu crois que je suis ton larbin ?".format(nick))
                self.victim = nick

            return allow

        if message.startswith("!whitelist "):
            if by_oper():
                self.do_whitelist(message[11:])
            return

        elif message.startswith("!blacklist "):
            if by_oper():
                self.do_blacklist(message[11:])
            return

        elif trump_re.search(message):
            if self.trump_rl(e.source):
                self.victim = NickMask(e.source).nick
                logging.info("{0} abused trump card".format(e.source))
                c.privmsg(e.target, "{0}: c'est bientôt fini, de me dire ta gueule à tout va ? c'est pas comme ça que tu vas relever le niveau.".format(
                    self.victim))
            else:
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
