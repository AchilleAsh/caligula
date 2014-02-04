Ce script permet de récupérer l'emploi du temps de [l'école](http://caligula.ensea.fr) au format standard iCal

##Usage


`caligula.py -g <groupe de TD TP> `

exemple : `caligula.py -g 2G1TD1TP1`

##Exploitation des fichiers iCal

Les fichiers iCal (extension .ics) correspondent à la norme des calendriers. Vous pouvez soit :
* Télécharger le fichier .ics sur votre ordinateur et l'importer dans votre logiciel d'agenda
* Synchroniser votre agenda avec l'url complete du fichier .ics

Les fichiers iCal des cours sont disponibles sur (http://showok.info/caligula/ics). Les noms des fichiers correspondent aux nom complet du TP : si vous êtes dans le 2G1TD1TP1 le fichier d'emploi du temps sera [](http://showok.info/caligula/ics/2G1TD1TP1.ics)

### Avec Sunbird (intégré dans Thunderbird)

Importer (ne sera pas actualisé) : Evenements et tâches > Importer > votre fichier .ics 
Synchroniser : Agenda > Nouvel agenda > Sur le réseau > format iCalendar > url correspondant à votre emploi du temps

### Avec Google Calendar

Importer (ne sera pas actualisé) :
Synchroniser : https://www.google.com/calendar/render > Autres agenda > ajouter par url > url correspondant à votre emploi du temps

### Avec iCal

TODO

##TODO

* Configurer la timezone avec VTIMEZONE 
* gestion des alternants, 3A, masters et enseignants
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
