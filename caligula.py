#!/usr/bin/python
# -*-coding:Utf-8 -*
import os
import sys 
import requests
import random
import threading
import Queue
import time
import re
import unicodedata
from icalendar import Calendar, Event
from HTMLParser import HTMLParser
import string
from datetime import datetime, timedelta
import logging
from HTMLParser import HTMLParser
import urllib2


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

		
		groups = i[4]
		prof = str(i[5])
		room = i[6]
		name = unicodedata.normalize('NFKD', i[3]).encode('ascii','ignore')
		# start_ical = dateICal(start)
		# end_ical = dateICal(end)
		summary = "%s avec %s en %s" %(name,prof,room)

		event_condensed_name = "%s-%s" % (name, prof)
		event_condensed_name = re.sub('[^\w]','_', event_condensed_name)
		uid =  "%s-%s-%s" % (groups, start, event_condensed_name)
		


		event = Event()
		event.add('summary',summary)
		event['dtstart'] = dateICal(start)
		event['dtend'] = dateICal(end)
		event["uid"] = uid
		event.add('priority', 1)
		

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
	URL2 = 'http://caligula.ensea.fr/ade/standard/gui/menu.jsp?on=Planning&sub=Afficher&href=/custom/modules/plannings/plannings.jsp&target=visu&tree=true'
	tree = "http://caligula.ensea.fr/ade/standard/gui/tree.jsp"
	s = requests.Session()
	s.get(URL1)
	nbw = 38
	# r = s.get(URL2)


	# f = open("file.html",'w') 
	# f.write(r.content) 


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
	# print nweek
	# Set the weeks
	bounds = "http://caligula.ensea.fr/ade/custom/modules/plannings/bounds.jsp"

	## Obtain next 8 weeks of the calendar
	week = "week=%i" % nweek
	url = "%s?%s&reset=true" % (bounds, week)
	result = s.get(url)


	for i in range(1, nbw - 1):
		week = "week=%i" % (i) #nweek - i pour avoir juste les semaines restantes
		url = "%s?%s&reset=false" % (bounds, week)
		result = s.get(url)
	 
	# Retrieve the content and parse it
	info = "http://caligula.ensea.fr/ade/custom/modules/plannings/info.jsp"
	url = info
	result = s.get(url)

	with open("file.html",'w') as f:
		f.write(result.content)



	parser = infoParser()
	parser.feed(unicode(result.content, "utf-8", "ignore"))
	parser.close()

	# print parser.result

	ics = make_cal_event(parser.result)

	return ics

def get_tp_ids(eleve = 'oui', annee = 2 , groupe = 1,td = 1,tp = 1):
	# TODO : Gerer les alternants et les profs
	user = "%sG%sTD%sTP%s" %(str(annee),str(groupe),str(td),str(tp))
	param = ['trainee',60,80,20]	
	if eleve == 'oui':
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
		# elif annee == '3D' :
		# 	param[1] = 62
		# elif annee == '3A' :
		# 	param[1] = 62	
		else :
			print 'Cette combinaison est invalde'
		return user,param


prefix = ''
for annee in range(1,3):
	for groupe in range(1,4) :
		i = -2
		for td in range(1,4) :
			i+=2
			for tp in range(1,3):
				user,param = get_tp_ids(eleve='oui',groupe=groupe,annee=annee,td=td,tp=tp+i)
				print user,param

				events = get_ical(param)
				with open(prefix+user+'.ics','w') as f:
					f.write(str(events))

# # param_lst = ['trainee',60,80,20]	
# events = get_ical(param)
# with open('list.ics','w') as f:
# 	f.write(str(events))
