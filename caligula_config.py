#!/usr/bin/python
# -*-coding:Utf-8 -*
import os
import sys 
def get_user_config(eleve = 'oui', annee = 2 , groupe = 1,td = 1,tp = 1):
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