#!/usr/bin/python
# -*-coding:Utf-8 -*
import os
import sys 
import random
import time
import re
import unicodedata
from HTMLParser import HTMLParser
import string
from datetime import datetime, timedelta
import logging
from HTMLParser import HTMLParser
import urllib2
import getopt
import requests
from icalendar import Calendar, Event
import chardet
# import caligula_config


class infoParser(HTMLParser):
	def __init__(self):
		self.result = []
		self.nbrow = 0
		self.active = 0
		self.finished = 0
		self.skipping=0
		self.current_row = []
		self.current_data = []
		HTMLParser.__init__(self)

	def start_table(self, attributes):
		# print "begin table"
		if not self.finished:
			self.active=1
	def end_table(self):
		# print "end table"
		self.active=0
		self.finished=1

	def start_tr(self,attributes):
		# print " begin tr"
		if self.active and not self.skipping:
			self.current_row = []
			
	def end_tr(self):
		# print " end tr"
		if self.active and not self.skipping:
			self.result.append(self.current_row)
			
	def start_td(self,attributes):
		# print " begin td"
		if self.active and not self.skipping:
			self.current_data = []
			
	def end_td(self):
		# print " end td"
		if self.active and not self.skipping:
			# print self.current_data
			self.current_row.append(
			string.join(self.current_data))
		
	def handle_data(self, data):
		if self.active and not self.skipping:
			# print " datafound:"
			# print data
			# print " end of data"
			self.current_data.append(data)

	def handle_starttag(self, tag, attrs):
		# print "Encountered the beginning of a %s tag" % tag
		if tag == "table":
			self.start_table(attrs)
		elif tag == "tr":
			self.start_tr(attrs)
		elif tag == "td":
			self.start_td(attrs)

	def handle_endtag(self, tag):
		# print "Encountered the end of a %s tag" % tag
		if tag == "table":
			self.end_table()
		elif tag == "tr":
			self.end_tr()
		elif tag == "td":
			self.end_td()



def dateICal(date):
	return date.strftime("%Y%m%dT%H%M%S")


def make_cal_event(parsed):
	cal = Calendar()
	cal.add('prodid', '-//My calendar product//mxm.dk//')
	cal.add('version', '2.0')
	cal['summary'] = 'Emploi du temps de ENSEA'

	for i in parsed:

		event = Event()

		if len(i) < 7:
			continue
		start = datetime.strptime("%s %s" % (i[0], i[1]), "%d/%m/%Y %H:%M")
		if re.match("^\d{1,2}h$", i[2]):
			delta = datetime.strptime(i[2], "%Hh")
		else: # /2h30min/
			delta = datetime.strptime(i[2], "%Mmin")
		end = start + timedelta(hours = delta.hour, minutes = delta.minute)

		
		groups = unicodedata.normalize('NFKD', i[4]).encode('ascii','ignore')
		prof = unicodedata.normalize('NFKD', i[5]).encode('ascii','ignore')[:40]
		
		prof_lst = prof.split(" ")
		if len(prof_lst) < 3 : prof = prof_lst[-1]+" "+" ".join(prof_lst[0:-1])
	


		room = i[6][:5]
		name = unicodedata.normalize('NFKD', i[3]).encode('ascii','ignore')

		
		# if len(groups) == len('2G1 TD1 2G1 TD2 2G1 TD3'):
		# 	# groups = groups[:3]
		# 	continue
		# if groups == '2me ENSEA 1re A ENSEA 1re B ENSEA 3me ENSEA':
		# 	groups = "toute l'école"
		

		# start_ical = dateICal(start)
		# end_ical = dateICal(end)
		summary = "%s avec %s en %s" %(name,prof,room)

		event_condensed_name = re.sub('[^\w]','_', "%s-%s" % (name, prof))
		uid =  "%s-%s@%s" % (dateICal(start),dateICal(end), event_condensed_name[:10])


		event = Event()
		event.add('summary',summary)
		event.add('location',room)
		event.add('categories','Cours')
		event['dtstart'] = dateICal(start)
		event['dtend'] = dateICal(end)
		event["uid"] = uid
		event.add('priority', 0)
		

		cal.add_component(event)

	return cal.to_ical()




## Parser to get the number of the current week
class weekParser(HTMLParser):
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




def get_ical(param_lst):

	URL1 = 'http://caligula.ensea.fr/ade/standard/gui/interface.jsp?projectId=4&login=ensea&password=ensea'
	tree = "http://caligula.ensea.fr/ade/standard/gui/tree.jsp"
	s = requests.Session()
	s.get(URL1)
	nbw = 38

	category = "category=%s" % param_lst[0]
	url = "%s?%s&expand=false&forceLoad=false&reload=false" % (tree, category)
	r = s.get(url)

	branch = "branchId=%i" % param_lst[1]
	url = "%s?%s&expand=false&forceLoad=false&reload=false" % (tree, branch)
	r = s.get(url)

	branch = "branchId=%i" % param_lst[2]
	url = "%s?%s&expand=false&forceLoad=false&reload=false" % (tree, branch)
	r = s.get(url)

	selectId = "selectId=%i" % param_lst[3]
	url = "%s?%s&expand=false&forceLoad=false&reload=false" % (tree, selectId)
	r = s.get(url)

	# Get the time bar
	url = "http://caligula.ensea.fr/ade/custom/modules/plannings/pianoWeeks.jsp"
	result = s.get(url)

	parser = weekParser()
	parser.feed(result.content)
	parser.close()
	nweek = parser.nweek - 1

	# Set the weeks
	bounds = "http://caligula.ensea.fr/ade/custom/modules/plannings/bounds.jsp"

	## Obtain next x weeks of the calendar
	week = "week=%i" % nweek
	url = "%s?%s&reset=true" % (bounds, week)
	result = s.get(url)


	for i in range(1, nbw - 1):
		week = "week=%i" % (nweek + i) #nweek - i pour avoir juste les semaines restantes
		url = "%s?%s&reset=false" % (bounds, week)
		result = s.get(url)
	 
	# Retrieve the content and parse it
	url = "http://caligula.ensea.fr/ade/custom/modules/plannings/info.jsp"
	result = s.get(url)

	with open("file.html",'w') as f:
		f.write(result.content)


	content = result.content
	# encoding = chardet.detect(content)['encoding']
	# print 'encoding',encoding
	parser = infoParser()
	parser.feed(result.content.decode("ISO-8859-2","ignore"))
	parser.close()

	return make_cal_event(parser.result)

def get_user_config(user_type = 'stagiaires', user = '2G1TD1TP1'):
	# TODO : Gerer les alternants et les profs
	annee = td = tp = 0
	option = ""
	if user[1].lower() == 'g' and len(user) == 9 and user_type in 'stagiaires': #1A 2A
		annee = int(user[0])
		groupe = int(user[2])
		td = int(user[5])
		tp = int(user[8])
	
	elif user[0:2].lower() in 'sic': 
		tp = int(user[5])
		annee = 'mastere'
		print 'sic'
	elif user[0:2].lower() in 'esa': 
		td = 'esa'
		tp = int(user[5])
		option = 'mastere'
	elif user[0:2].lower() in 'madocs':
		td = 'madocs'
		tp = int(user[8])
		option = 'mastere'

			 
			
	# user = "%sG%sTD%sTP%s" %(str(annee),str(groupe),str(td),str(tp))
	param = ['trainee',60,80,20] #defaut

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
				param[1] = 247
				if tp == 1 : param[3] = 750
				elif tp == 2 : param[3] = 748
				elif tp == 3 : param[3] = 749


		# elif annee == '3D' :
		# 	param[1] = 62
		# elif annee == '3A' :
		# 	param[1] = 62	
		# else :
		# 	print 'Cette combinaison est invalde'

	if user.lower() not in '2G1TD1TP1'.lower() and (param[1] == 60 or param[2] == 80 or param[3] == 20) :
		sys.stderr.write("Cette option est inconnue")
		sys.exit(2)

	return user,param


def fetch_ics(user_type = 'stagiaires',user = '2G1TD1TP1',path_destination = ' '):
	if not os.path.exists(path_destination) and len(path_destination) > 2:
		os.mkdir(path_destination[:-1])
	user,param = get_user_config(user=user)
	events = get_ical(param)
	with open(path_destination+user+'.ics','w') as f:
		f.write(str(events))
	print user,param	


def fetch_all_ical(path_destination = 'ics/'):

	# 1A et 2A
	for annee in range(1,3):
		for groupe in range(1,4) :
			i = -2
			for td in range(1,4) :
				i+=2
				for tp in range(1,3):
					fetch_ics(user= "%sG%sTD%sTP%s" %(annee,groupe,td,tp),path_destination=path_destination)

	# Mastere
	for master in """esa sic madocs""".split() :
		for tp in range (0,4):
			fetch_ics(user= "%sTP%s" %(master,tp),path_destination=path_destination)


def usage():
	print 'usage : caligula.py -g <groupe de TD TP>'
	print 'exemple : caligula.py -g 2G1TD1TP1'
	print 'le groupe all va télécharger tous les emplois du temps'
	print 'exemple : caligula.py -g all'

def main(argv):
	groupe = ''
	if len(argv) < 1 :
		usage()
	try:
		opts, args = getopt.getopt(argv,"hg:",["groupe="])
	except getopt.GetoptError,err:
		print str(err)
		usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ('-h','--help'): usage()
		elif opt in ("-g", "--groupe"): groupe = arg


	# if len(groupe) != 9  and groupe != 'all':
	# 	print "Le choix '%s' est incorrect" %(groupe)
	# 	usage()

	if groupe == 'all' :
		fetch_all_ical()
	else :
		fetch_ics(user=groupe)




if __name__ == "__main__":
	main(sys.argv[1:])
