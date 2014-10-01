#!/usr/bin/python
# -*-coding:Utf-8 -*

"""
 "THE BEER-WARE LICENSE" (Revision 42):
  <showok@showok.info> wrote this file from the original work of
  <anthony.perard@gmail.com> : https://github.com/sheep/Chronos.
  As long as you retain this notice you  can do whatever you want with this stuff.
  If we meet some day, and you think this stuff is worth it, you can buy me a beer in return.
  Théo Segonds


  Il faut installer les dépendances requests et iCalendar avec pip

"""

import os
import sys
import re
import unicodedata
from HTMLParser import HTMLParser
import string
from datetime import datetime, timedelta
import getopt
import requests
from icalendar import Calendar, Event, Timezone, TimezoneStandard, TimezoneDaylight
import pytz

login = ""


class branchParser(HTMLParser):
	"""
	Parseur du résultat de tree.jsp pour récupérer le nom des items et leur identifiant dans les branches ouvertes
	"""
	def __init__(self):
		self.itemsID = []
		self.itemsNames = []
		self.itemsCategory = []
		self.treeitem = False
		self.ina = False
		self.category = []
		self.current_data = []
		HTMLParser.__init__(self)

	def handle_starttag(self, tag, attrs):
		if tag == "span" and len(attrs) > 0 and attrs[0][1] == "treeitem":
			self.treeitem=True
		if tag == "a" and self.treeitem==True:
			self.current_data = []
			self.current_data = int(re.sub("[\D]","",attrs[0][1]))
			self.itemsID.append(self.current_data)
			self.itemsCategory.append(self.category)
			self.ina = True
		if tag == "a" and attrs[0][1].find("openCategory(")>=0:
			self.category = re.sub("\'\)","",re.sub(r'javascript:openCategory\(\'',"",attrs[0][1]))
	def handle_endtag(self, tag):
		if tag == "span" and self.treeitem==True:
			self.treeitem=False
		if tag == "a" and self.treeitem==True:
			self.ina = False

	def handle_data(self, data):
		if self.ina:
			self.itemsNames.append(data)


class categoryParser(HTMLParser):
	"""
	Parseur du résultat de tree.jsp pour récupérer le nom et l'identifiant des branches
	"""
	def __init__(self):
		self.branches = []
		self.branchesNames = []
		self.treebranch = False
		self.ina = False
		HTMLParser.__init__(self)

	def handle_starttag(self, tag, attrs):
		if tag == "span" and len(attrs) > 0 and attrs[0][1] == "treebranch":
			self.treebranch=True
		if tag == "a" and self.treebranch==True:
			self.branches.append(int(re.sub("[\D]","",attrs[0][1])))
			self.ina = True

	def handle_endtag(self, tag):
		if tag == "span" and self.treebranch==True:
			self.treebranch=False
		if tag == "a" and self.treebranch==True:
			self.ina = False

	def handle_data(self, data):
		if self.ina :
			self.branchesNames.append(data)

class eventsParser(HTMLParser):
	"""
	Parseur du résultat de eventInfo.jsp pour récupérer l'information des évènements en vue de déterminer s'il s'agit de TD, TP, Projets, contrôles, ...
	"""
	def __init__(self):
		self.result = []
		self.inp = False
		self.s = requests.Session()
		HTMLParser.__init__(self)

	def handle_starttag(self, tag, attrs):
		if tag == "p":
			self.inp = True

	def handle_endtag(self, tag):
		if tag == "p":
			self.inp = False

	def handle_data(self, data):
		if self.inp:
			if not data=="&nbsp;" :
				self.result = data

class infoParser(HTMLParser):
	"""
	Parseur du résultat de info.jsp (une fois qu'on l'a configuré comme voulu: sélection Id et weeks) pour extraire les données du tableau nécessaires à la création du calendrier
	"""
	global login
	def __init__(self):
		self.result = []
		self.nbrow = 0
		self.active = 0
		self.finished = 0
		self.skipping=0
		self.current_row = []
		self.current_data = []
		self.URL0 = 'http://caligula.ensea.fr/ade/standard/gui/interface.jsp?projectId=1&login=%s&password=%s' %(login,login)
		self.s = requests.Session()
		self.html = self.s.get(self.URL0)
		self.parser = eventsParser()
		HTMLParser.__init__(self)

	def start_table(self, attributes):
		if not self.finished:
			self.active=1
	def end_table(self):
		self.active=0
		self.finished=1

	def start_tr(self,attributes):
		if self.active and not self.skipping:
			self.current_row = []

	def end_tr(self):
		if self.active and not self.skipping:
			self.result.append(self.current_row)

	def start_td(self,attributes):
		if self.active and not self.skipping:
			self.current_data = []

	def end_td(self):
		if self.active and not self.skipping:
			self.current_row.append(
			string.join(self.current_data))

	def handle_data(self, data):
		if self.active and not self.skipping:
			self.current_data.append(data)

	def handle_starttag(self, tag, attrs):
		if tag == "table":
			self.start_table(attrs)
		elif tag == "tr":
			self.start_tr(attrs)
		elif tag == "td":
			self.start_td(attrs)
		elif tag == "a": #get the ID of the event and gather info with eventsParser
			lst = re.findall(r'\d{3,6}', attrs[0][1])
			if len(lst)>0 and self.active and not self.skipping:
				URL1 = 'http://caligula.ensea.fr/ade/custom/modules/plannings/eventInfo.jsp?eventId=%i' % int(lst[0])
				self.parser.result = []
				self.parser.feed(self.s.get(URL1).content)
				self.parser.close()
				if not(self.parser.result == []):
					if self.parser.result.lower().find("cours")>=0:
						self.current_row.append("Cours")
					elif self.parser.result.lower().find("td")>=0:
						self.current_row.append("TD")
					elif self.parser.result.lower().find("tp")>=0:
						self.current_row.append("TP")
					elif self.parser.result.lower().find("contrôle")>=0:
						self.current_row.append("Contrôle")
					elif self.parser.result.lower().find("SIC")>=0:
						self.current_row.append("SIC")
					elif self.parser.result.lower().find("ESA")>=0:
						self.current_row.append("ESA")

	def handle_endtag(self, tag):
		if tag == "table":
			self.end_table()
		elif tag == "tr":
			self.end_tr()
		elif tag == "td":
			self.end_td()

def dateICal(date):
	"""format de date pour iCal"""
	return date.strftime("%Y%m%dT%H%M%S")

def make_calendar(parsed,pourProf=False):
	"""
	création du calendrier a partir du parseur
	"""
	# Création de l'agenda
	cal = Calendar()

	# Etablissement du nom du Timezone
	cal.add('x-wr-calname', u"caligula.ensea.fr parser by showok")
	cal.add('x-wr-caldesc', u"send problems to <contact at showok.info>")
	cal.add('x-wr-relcalid', u"12345")
	cal.add('x-wr-timezone', u"Europe/Paris")

	tzc = Timezone()
	tzc.add('tzid', 'Europe/Paris')
	tzc.add('x-lic-location', 'Europe/Paris')

	tzs = TimezoneStandard()
	tzs.add('tzname', 'CET')
	tzs.add('dtstart', datetime(1970, 10, 25, 3, 0, 0))
	tzs.add('rrule', {'freq': 'yearly', 'bymonth': 10, 'byday': '-1su'})
	tzs.add('TZOFFSETFROM', timedelta(hours=2))
	tzs.add('TZOFFSETTO', timedelta(hours=1))

	tzd = TimezoneDaylight()
	tzd.add('tzname', 'CEST')
	tzd.add('dtstart', datetime(1970, 3, 29, 2, 0, 0))
	tzs.add('rrule', {'freq': 'yearly', 'bymonth': 3, 'byday': '-1su'})
	tzd.add('TZOFFSETFROM', timedelta(hours=1))
	tzd.add('TZOFFSETTO', timedelta(hours=2))

	tzc.add_component(tzs)
	tzc.add_component(tzd)
	cal.add_component(tzc)

	for i in parsed:
		event = Event()

		if len(i) < 7:
			continue
		start = datetime.strptime("%s %s" % (i[0], i[1]), "%d/%m/%Y %H:%M")

		if start.hour == 10:
			start = start + timedelta(minutes = 10)
		elif start.hour == 13:
			start = start + timedelta(minutes = 15)
		elif start.hour == 15:
			start = start + timedelta(minutes = 25)

		if re.match("^\d{1,2}h$", i[2]):
			delta = datetime.strptime(i[2], "%Hh")

		elif re.match("^\d{1,2}min$", i[2]): # /30min/
			delta = datetime.strptime(i[2], "%Mmin")
		else:
			delta = datetime.strptime(i[2], "%Hh%Mmin")

		if delta.hour == 2: # prise en compte des pauses pour les séquences de deux heures
			delta = delta - timedelta(minutes = 10)

		end = start + timedelta(hours = delta.hour, minutes = delta.minute)

		groups = unicodedata.normalize('NFKD', i[5]).encode('ascii','ignore').replace(" ",'')

		prof = unicodedata.normalize('NFKD', i[6]).encode('ascii','ignore')
		# On inverse nom et prénom pour avoir {prenom nom}
		prof_lst = prof.split(" ")
		if len(prof_lst) < 3 : prof = prof_lst[-1]+" "+" ".join(prof_lst[0:-1])

		# Si le nom est trop long (comme pour les cours de langues), on le coupe et ajoute [...]
		if len(prof) > 40 : prof = prof[:40]+'[...]'

		room = i[7][:5]

		name = unicodedata.normalize('NFKD', i[4]).encode('ascii','ignore')
		name = re.sub(u'ŕ',u"a",name)

		typeevent = re.sub(u'ŕ',u"à",i[3])
		# typeevent =  unicodedata.normalize('NFKD', i[3]).encode('Utf-8','ignore')
		if typeevent == "TP" and name.lower().find("projet")>=0:
			typeevent = ""

		start_ical = dateICal(start)
		end_ical = dateICal(end)
		if pourProf:
			if len(typeevent)>0:
				summary = "%s de %s avec %s en %s" %(typeevent,name,groups,room)
			else:
				summary = "%s avec %s en %s" %(name,groups,room)
		else:
			if len(typeevent)>0:
				if len(typeevent)>6:
					summary = "%s avec %s en %s" %(typeevent,prof,room)
				else :
					summary = "%s de %s avec %s en %s" %(typeevent, name,prof,room)
			else :
				summary = "%s avec %s en %s" %(name,prof,room)


		uid =  "%s-%s@%s" % (dateICal(start),dateICal(end), room) #event_condensed_name[:10])

		# Pour ajouter le timezone proprement à chaque heure d'événements (optionel)
		hour_start = [int(h) for h in str(start).split(" ")[1].split(':')]
		hour_end = [int(h) for h in str(end).split(" ")[1].split(':')]
		date_start = [int(d) for d in str(start).split(" ")[0].split('-')]
		date_end = [int(d) for d in str(end).split(" ")[0].split('-')]

		# Le fichier de sortie ne doit pas dépasser 75 caractères par ligne
		event = Event()
		event.add('summary',summary)
		event.add('location',room+", ENSEA, Cergy")
		event.add('status', "confirmed")
		event.add('category','Event')
		event.add('dtstart', datetime(date_start[0],date_start[1],date_start[2],hour_start[0],hour_start[1],hour_start[2],tzinfo=pytz.timezone("Europe/Paris")))
		event.add('dtend',datetime(date_end[0],date_end[1],date_end[2],hour_end[0],hour_end[1],hour_end[2],tzinfo=pytz.timezone("Europe/Paris")))
		event["uid"] = uid
		event.add('priority', 0)

		cal.add_component(event)
	return cal

class weekParser(HTMLParser):
	"""
	Parser to get the number of the current week
	"""
	def __init__(self):
		self.pianoSelected = False
		self.nweek = 1
		HTMLParser.__init__(self)

	def handle_starttag(self, tag, attrs):
		if tag == "div" and len(attrs) > 0 and attrs[0][1] == "pianoselected":
			self.pianoSelected = True
		elif tag == "map" and len(attrs) > 0 and self.pianoSelected:
			self.nweek = int(re.sub("[\D]","",attrs[0][1]))

	def handle_endtag(self, tag):
		if tag == "div" and self.pianoSelected:
			self.pianoSelected = False

# Transform un fichier iCal en JSON
def ical_to_json(ics):

	cal = ics
	data = {}
	data[cal.name] = dict(cal.items())

	for component in cal.subcomponents:
		if not data[cal.name].has_key(component.name):
			data[cal.name][component.name] = []

		comp_obj = {}
		for item in component.items():
			comp_obj[item[0]] = unicode(item[1])

		data[cal.name][component.name].append(comp_obj)
	return data

def get_html_agenda(param_lst,debug = True):
	global login
	URL1 = 'http://caligula.ensea.fr/ade/standard/gui/interface.jsp?projectId=1&login=%s&password=%s' %(login,login)
	tree = "http://caligula.ensea.fr/ade/standard/gui/tree.jsp"
	s = requests.Session()
	s.get(URL1)
	nbw = 38

	if param_lst[0] not in '' :
		category = "category=%s" % param_lst[0]
		url = "%s?%s&expand=false&forceLoad=false&reload=false" % (tree, category)
		r = s.get(url)

	for i in range(1,len(param_lst)-2) :
		if param_lst[i] != 0 :
			branch = "branchId=%i" % param_lst[i]
			print branch
			url  = "%s?select%s&reset=true&forceLoad=false&reload=false" % (tree,branch)
			r = s.get(url)

			url = "%s?%s&expand=false&forceLoad=false&reload=false" % (tree, branch)
			r = s.get(url)

	if param_lst[3] != 0 :
		selectId = "selectId=%i" % param_lst[3]
		url = "%s?%s&expand=false&forceLoad=false&reload=false" % (tree, selectId)
		r = s.get(url)

	# Get the time bar
	url = "http://caligula.ensea.fr/ade/custom/modules/plannings/pianoWeeks.jsp"
	result = s.get(url)

	parser = weekParser()
	parser.feed(result.content)
	parser.close()
	nweek = parser.nweek - 2

	# Set the weeks
	bounds = "http://caligula.ensea.fr/ade/custom/modules/plannings/bounds.jsp"

	## Obtain next x weeks of the calendar
	week = "week=%i" % nweek
	url = "%s?%s&reset=true" % (bounds, week)
	result = s.get(url)

	for i in range(nweek, nbw - 1):
		week = "week=%i" % (i) #nweek - i pour avoir juste les semaines restantes
		url = "%s?%s&reset=false" % (bounds, week)
		result = s.get(url)

	# Retrieve the content and parse it
	url = "http://caligula.ensea.fr/ade/custom/modules/plannings/info.jsp"
	result = s.get(url)

	content = result.content.decode("ISO-8859-2","ignore")

	return content



def fetch_ical(param, user, path_destination = '',debug=False):
	"""
	Récupère l'agenda lié à un élément de la base (ne convient pas pour
	les groupes de TD qui sont des branches, pas des items)
	"""
	if not os.path.exists(path_destination) and len(path_destination) > 2:
		os.mkdir(path_destination[:-1])

	html = get_html_agenda(param,debug=debug)
	parser = infoParser()
	parser.feed(html)
	parser.close()
	if param[0] == 'instructor':
		ical =  make_calendar(parser.result,pourProf=True)
	else:
		ical =  make_calendar(parser.result,pourProf=False)

	ical_str = str(ical.to_ical())
	if ical_str[0] == " ":
		ical_str = ical_str[1:]

	if debug == True:
		print 'Debug mode'

		with open(path_destination+user+'.json','w') as f:
			f.write(str(ical_to_json(ical)))

		with open(path_destination+user+'.html','w') as f:
			f.write(html.encode('ISO-8859-2'))
			# f.write(html.decode("ISO-8859-2","ignore"))

	size = str(len(ical_str))+" octets"
	# if int(size.split()[0]) < 700:
	# 	size += '... il y a peut-être une erreur'
	if param[0] == 'instructor':
		# On ne garde que les 4 premier caracteres pour "annonymiser" le nom des profs
		usr_lst = [l[:4] for l in user.split()]
		user = '_'.join(usr_lst)

	with open(path_destination+re.sub('[^\w]','_',user)+'.ics','w') as f:
		f.write(ical_str)
	print user,param,size


def search_item(name):
	"""
	Effectue la recherche d'un élément de la base (groupe, prof, salle) par l'intermédiaire de l'outil de recherche du site
	"""
	global login
	print "Recherche d'un élément de la base dont le nom contient \""+name+"\""
	param_lst = ['',0,0,0]
	URL1 = 'http://caligula.ensea.fr/ade/standard/gui/interface.jsp?projectId=1&login=%s&password=%s' % (login,login)

	s = requests.Session()
	s.get(URL1)
	tree = 'http://caligula.ensea.fr/ade/standard/gui/tree.jsp?projectId=1&login=%s&password=%s' % (login,login)
	search_form = {'search': name}
	s = requests.post(tree, data=search_form)

	if "<HTML>" not in s.content :
		print "%s est probablement un mauvais mot de passe ou il y a eu un changement dans le site. Si tel est le cas, contactez moi sur showok@showok.info" % login
		sys.exit(2)
	if "Veuillez vous identifier" in s.content :
		print "il semblerait qu'il y ai eu une modification dans le site"

	parser = branchParser()
	parser.itemsID = []
	parser.itemsNames = []
	parser.feed(s.content.decode("ISO-8859-2","ignore"))
	parser.close()
	if len(parser.itemsID)==0: # si aucun résultat n'est trouvé
		print "%s ne correspond à aucune donnée de la base" % name
		sys.exit(2)
	elif len(parser.itemsID)==1: # dans le cas optimal où un seul résultat est renvoyé
		user = parser.itemsNames[0]
		param_lst[0] = parser.itemsCategory[0]
		param_lst[3] = parser.itemsID[0];
	else: # si plusieurs résultats sont renvoyés
		for i in range(1, len(parser.itemsID) ):
			print "%d:\t%s\t%s" % (i,parser.itemsCategory[i-1],parser.itemsNames[i-1])
			param_lst[3] = parser.itemsID[i-1];
		input_var = int(input("Please select an item by entering the corresponding number: "))
		user = parser.itemsNames[input_var-1]
		param_lst[0] = parser.itemsCategory[input_var-1]
		param_lst[3] = parser.itemsID[input_var-1]
	print "%s %s with ID %s" % (param_lst[0],user,param_lst[3])
	return user,param_lst

def fetch_from_search(name):
	user,param = search_item(name)
	fetch_ical(param=param,user=user,debug = False)

def worker(q,name):
	q.put(fetch_from_search(name))


def search_from_file(filename):
	"""
	Implémente la recherche à partir d'un fichier afin de télécharger un grand nombre d'agendas d'un coup

	Le multithreading entrenne des erreurs....
	"""
	import Queue
	import threading
	q = Queue.Queue()
	with open(filename, "r") as f:
		for line in f:
			if line is not "\n" :
				fetch_from_search(line[:-1])
				# t = threading.Thread(target=worker, args = (q,line[:-1]))
				# t.daemon = True
				# t.start()
		# s = q.get()
		# print s


def usage():

	print 'Usage : '
	print 'python caligula.py <options> -l <login pour acceder à caligula.ensea.fr>'
	print ''
	print 'Options:'
	print '-s --search 	partie du nom de prof, groupe de TD ou salle'
	print 'exemple 1 : python caligula.py -s guerquin -l <login pour acceder à caligula.ensea.fr>'
	print 'exemple 2 : python caligula.py -s C104 -l <login pour acceder à caligula.ensea.fr>'
	print 'exemple 3 : python caligula.py -s \'1G1 TP3\' -l <login pour acceder à caligula.ensea.fr>'
	print ''
	print ''



def main(argv):
	global login
	search = ''
	file = ''
	debug = False
	if len(argv) < 1 :
		usage()
	try:
		opts, args = getopt.getopt(argv,"h:d:s:l:f:",["help","debug","search","login","file"])
	except getopt.GetoptError,err:
		print str(err)
		usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ('-h','--help'): usage()
		elif opt in ("-s", "--search"): search = arg
		elif opt in ("-l", "--login"): login = arg
		elif opt in ("-f", "--file"): file = arg
		else :
			usage()
			sys.exit(2)





	# if len(groupe) != 9  and groupe != 'all':
	# 	print "Le choix '%s' est incorrect" %(groupe)
	# 	usage()
	if (login is ""):
		usage()
		sys.exit(2)
	if not(search is ""):
		user,param = search_item(search)
		# print "user %s, param : %s" %(user,param)
		fetch_ical(param=param,user=user,debug = debug)
	if not(file is ""):
		search_from_file(file)

	sys.exit(2)

if __name__ == "__main__":
	main(sys.argv[1:])
