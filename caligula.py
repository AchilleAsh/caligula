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
import requests
from icalendar import Calendar, Event
import caligula_config


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
		week = "week=%i" % (i) #nweek - i pour avoir juste les semaines restantes
		url = "%s?%s&reset=false" % (bounds, week)
		result = s.get(url)
	 
	# Retrieve the content and parse it
	url = "http://caligula.ensea.fr/ade/custom/modules/plannings/info.jsp"
	result = s.get(url)

	# with open("file.html",'w') as f:
	# 	f.write(result.content)

	parser = infoParser()
	parser.feed(unicode(result.content, "utf-8", "ignore"))
	parser.close()

	return make_cal_event(parser.result)




def fetch_ics(annee = 2 , groupe = 1,td = 1,tp = 1,path_destination = 'ics/'):
	if not os.path.exists(path_destination):
		os.mkdir(path_destination[:-1])
	user,param = caligula_config.get_user_config(eleve='oui',groupe=groupe,annee=annee,td=td,tp=tp)
	events = get_ical(param)
	with open(path_destination+user+'.ics','w') as f:
		f.write(str(events))
	print user,param	


def fetch_all_ical(path_destination = 'ics/'):

	for annee in range(1,3):
		for groupe in range(1,4) :
			i = -2
			for td in range(1,4) :
				i+=2
				for tp in range(1,3):
					fetch_ics(groupe=groupe,annee=annee,td=td,tp=tp+i,path_destination=path_destination)


def main():
	fetch_all_ical()


if __name__ == "__main__":
    main()
