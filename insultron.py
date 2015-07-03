import random

def generate():
	return ' '.join(random.choice(x) for x in [prefixes, nouns, suffixes])

prefixes = [
	"grosse",
	"hideuse",
	"pauvre",
	"petite",
	"putain de",
	"sale",
	"vieille",
	"affreuse",
	"ignoble",
	"infecte",
	"horrible"]

nouns = [
	"attardée",
	"baleine",
	"batarde",
	"bouse",
	"chienne",
	"chieuse",
	"choucroute",
	"conasse",
	"conne",
	"crapule",
	"crotte",
	"daube",
	"debile",
	"diahrrée",
	"gouine",
	"greluche",
	"grognasse",
	"idiote",
	"lépreuse",
	"merde",
	"morue",
	"mongolienne",
	"poubelle",
	"peste",
	"plaie",
	"putasse",
	"pute",
	"prostituee",
	"salope",
	"sodomite",
	"suceuse",
	"truie",
	"vache" ]

suffixes = [
	"alcoolique",
	"cadaverique",
	"chauve",
	"decatie",
	"degeulasse",
	"edentee",
	"enculee",
	"en chaleur",
	"en latex",
	"infecte",
	"imbaisable",
	"mal baisee",
	"merdeuse",
	"moche",
	"moisie",
	"nymphomane",
	"pourrie",
	"puante",
	"rachitique",
	"ridee",
	"stupide",
	"suintante",
	"syphillitique",
	"tarée"]

if __name__ == '__main__':
	print(generate())
