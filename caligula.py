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

		typeevent = i[3]
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
		print category
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


def get_user_config(user_type = 'stagiaires', user = '2G1TD1TP1'):
	"""
	Fournit les identifiants en fonction des groupes de TPTD
	Attention, ce code est très moche, il faut de préférence utiliser le
	parser de la recherche
	"""
	annee = td = tp = 0
	option = ""
	if user[1].lower() == 'g'  and user_type in 'stagiaires': #1A 2A
		annee = int(user[0])
		groupe = int(user[2])
		if(len(user) > 5):
			td = int(user[5])
			if(len(user) > 8):
				tp = int(user[8])

	elif user[0] == '3':
		if user[1:3].lower() in 'aei':
			option = 'aei'
			tp = user[1:3]

	elif user[0:2].lower() in 'sic':
		td = 'sic'
		option = 'mastere'
		if len(user)> 3:
			tp = int(user[5])


	elif user[0:2].lower() in 'esa':
		td = 'esa'
		option = 'mastere'
		if len(user)> 3:
			tp = int(user[5])

	elif user[0:2].lower() in 'madocs':
		td = 'madocs'
		option = 'mastere'
		# tp = int(user[8])
		if len(user)> 6:
			tp = int(user[8])

	# user = "%sG%sTD%sTP%s" %(str(annee),str(groupe),str(td),str(tp))
	param = ['trainee',0,0,0] #defaut

	if user_type in 'stagiaires':
		param[0] = 'trainee'
		if annee == 1 :
			if groupe == 1:
				param[1] = 62
				if td == 1:
					param[2] = 72
					if tp == 1:
						param[3] = 2
					elif tp == 2:
						param[3] = 3
				elif td == 2:
					param[2] = 73
					if tp == 3:
						param[3] = 4
					elif tp == 4:
						param[3] = 5
				elif td == 3:
					param[2] = 74
					if tp == 5:
						param[3] = 6
					elif tp == 6:
						param[3] = 7
			elif groupe == 2:
				param[1] = 62
				if td == 1:
					param[2] = 75
					if tp == 1:
						param[3] = 8
					elif tp == 2:
						param[3] = 9
				elif td == 2:
					param[2] = 76
					if tp == 3:
						param[3] = 10
					elif tp == 4:
						param[3] = 12
				elif td == 3:
					param[2] = 383
					if tp == 5:
						param[3] = 384
					elif tp == 6:
						param[3] = 142
			elif groupe == 3:
				param[1] = 63
				if td == 1:
					param[2] = 77
					if tp == 1:
						param[3] = 14
					elif tp == 2:
						param[3] = 15
				elif td == 2:
					param[2] = 78
					if tp == 3:
						param[3] = 16
					elif tp == 4:
						param[3] = 17
				elif td == 3:
					param[2] = 79
					if tp == 5:
						param[3] = 18
					elif tp == 6:
						param[3] = 441

		elif annee == 2:
			param[1] = 64
			if groupe == 1:
				if td == 1:
					param[2] = 80
					if tp == 1:
						param[3] = 20
					elif tp == 2:
						param[3] = 21
				elif td == 2:
					param[2] = 81
					if tp == 3:
						param[3] = 22
					elif tp == 4:
						param[3] = 23
				elif td == 3:
					param[2] = 386
					if tp == 5:
						param[3] = 388
					elif tp == 6:
						param[3] = 267
			elif groupe == 2:
				if td == 1:
					param[2] = 82
					if tp == 1:
						param[3] = 24
					elif tp == 2:
						param[3] = 25
				elif td == 2:
					param[2] = 83
					if tp == 3:
						param[3] = 26
					elif tp == 4:
						param[3] = 27
				elif td == 3:
					param[2] = 496
					if tp == 5:
						param[3] = 497
					elif tp == 6:
						param[3] = 498
			elif groupe == 3:
				if td == 1:
					param[2] = 85
					if tp == 1:
						param[3] = 29
					elif tp == 2:
						param[3] = 30
				elif td == 2:
					param[2] = 86
					if tp == 3:
						param[3] = 31
					elif tp == 4:
						param[3] = 32
				elif td == 3:
					param[2] = 389
					if tp == 5:
						param[3] = 391
					elif tp == 6:
						param[3] = 398
		elif option in 'masteres':
			param[1] = 298
			if td == 'sic':
				param[2] = 507
				if tp == 1 : param[3] = 508
				elif tp == 2 : param[3] = 509
				elif tp == 3 : param[3] = 559
			elif td == 'esa':
				param[2] = 431
				if tp == 1 : param[3] = 433
				elif tp == 2 : param[3] = 262
				elif tp == 3 : param[3] = 422
			elif td == 'madocs':
				param[2] = 247
				if tp == 1 : param[3] = 750
				elif tp == 2 : param[3] = 748
				elif tp == 3 : param[3] = 749


		# elif annee == '3D' :
		# 	param[1] = 62
		# elif annee == '3A' :
		# 	param[1] = 62
		# else :
		# 	print 'Cette combinaison est invalide'

	if user.lower() not in '1G1TD1TP1'.lower() and (param[3] == 2) : #param[1] == 60 or param[2] == 80 or param
		sys.stderr.write("Cette option est inconnue : %s,%s,%s" %(user_type,user,param))
		sys.exit(2)

	return user,param


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

	with open(path_destination+re.sub('[^\w]','_',user)+'.ics','w') as f:
		f.write(ical_str)
	print user,param,size

def fetch_all_ical(path_destination = 'ics/',debug = False):
	"""
	Récupère les agendas de tous les groupes d'élèves
	"""

	# 1A et 2A
	for annee in range(1,3):
		for groupe in range(1,4) :
			i = -2
			for td in range(1,4) :
				i+=2
				for tp in range(1,3):
					fetch_ical(user= "%sG%sTD%sTP%s" %(annee,groupe,td,i+tp),path_destination=path_destination,debug = debug)

	# Mastere
	for master in """esa sic madocs""".split() :
		for tp in range (1,4):
			fetch_ical(user= "%sTP%s" %(master,tp),path_destination=path_destination)


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
	parser.feed(s.content)
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

def usage():

	print 'Usage : '
	print 'caligula.py <options> -l <login pour acceder à caligula.ensea.fr>'
	print ''
	print 'Options:'
	print '-s --search 	partie du nom de prof, groupe de TD ou salle'
	print 'exemple 1 : caligula.py -s guerquin -l <login pour acceder à caligula.ensea.fr>'
	print 'exemple 2 : caligula.py -s C104 -l <login pour acceder à caligula.ensea.fr>'
	print 'exemple 3 : caligula.py -s \'1G1 TP3\' -l <login pour acceder à caligula.ensea.fr>'
	print ''
	print '-g --groupe 	groupe complet avec la syntaxe GxTDxTPx'
	print '			all extraira tous les groupes'
	print 'exemple : caligula.py -g 2G1TD1TP1 -l <login pour acceder à caligula.ensea.fr>'
	print 'exemple : caligula.py -g all -l <login pour acceder à caligula.ensea.fr>'
	print ''



def main(argv):
	global login
	groupe = ''
	search = ''
	debug = False
	if len(argv) < 1 :
		usage()
	try:
		opts, args = getopt.getopt(argv,"hg:d:s:l:",["groupe","help","debug","search","login"])
	except getopt.GetoptError,err:
		print str(err)
		usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ('-h','--help'): usage()
		elif opt in ("-g", "--groupe"): groupe = arg
		elif opt in ("-d", "--debug"): debug = True
		elif opt in ("-s", "--search"): search = arg
		elif opt in ("-l", "--login"): login = arg
		else :
			usage()
			sys.exit(2)





	# if len(groupe) != 9  and groupe != 'all':
	# 	print "Le choix '%s' est incorrect" %(groupe)
	# 	usage()
	if (login is ""):
		usage()
		sys.exit(2)
	if not(groupe is ""):
		if groupe == 'all' :
			fetch_all_ical(debug = debug)
		else :
			user,param = get_user_config(user=groupe)
			fetch_ical(param=param,user=user,debug = debug)
	if not(search is ""):
		user,param = search_item(search)
		fetch_ical(param=param,user=user,debug = debug)

	sys.exit(2)

if __name__ == "__main__":
	main(sys.argv[1:])
