Ce script permet de récupérer l'emploi du temps de [l'école](http://caligula.ensea.fr) au format standard iCal

##Usage


`caligula.py -g <groupe de TD TP> `

exemple : `caligula.py -g 2G1TD1TP1`

##Exploitation des fichiers iCal

Les fichiers iCal (extension .ics) correspondent à la norme des calendriers. Ils peuvent donc être importés sur la plupart des logiciels d'agenda.


##TODO

* Ajouter une VTIMEZONE 
* gestion des alternants et 3A
* gestion des profs
* Ajouter une interface web


##Dépendances

* Requests 
* iCalendar

Pour installer les dépendances, avec pip :

* installer pip : `sudo apt-get install python-pip`

* `pip install requests`

* `pip install iCalendar`


##Crédits
Sheep : [https://github.com/sheep/Chronos](Chronos)
