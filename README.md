Ce script permet de récupérer l'emploi du temps de [l'école](http://caligula.ensea.fr) au format standard [iCalendar](http://fr.wikipedia.org/wiki/ICalendar) (abrévié en iCal)

##Usage


`caligula.py -g <groupe de TD TP> `

exemple : `caligula.py -g 2G1TD1TP1`

##Exploitation des fichiers iCal

Les fichiers [iCal](http://en.wikipedia.org/wiki/ICalendar) (extension .ics) correspondent à la norme des calendriers. Vous pouvez soit :
* Télécharger le fichier .ics sur votre ordinateur et l'importer dans votre logiciel d'agenda
* Synchroniser votre agenda avec l'url complete du fichier .ics

Les fichiers iCal des cours sont disponibles sur http://showok.info/caligula/ics. Les noms des fichiers correspondent aux nom complet du TP : si vous êtes dans le 2G1TD1TP1 le fichier d'emploi du temps sera **2G1TD1TP1.ics** et sera téléchargeable (et synchronisable) sur http://showok.info/caligula/ics/2G1TD1TP1.ics

Une mise à jour tous les jours à minuit est faite sur ces fichiers à partir de caligula.ensea.fr .

### Sur android

Vous pouvez visualiser votre emploi du temps avec l'application native d'agenda, mais il faut d'abord pouvoir lui faire lire le fichier iCal.

#### Avec un compte Google

Le plus simple est d'utiliser un compte google pour synchroniser ses contacts ; suivre la rubrique 'Avec Google Calendar'.

#### Sans compte google

L'application d'agenda ne gère pas l'import de fichiers iCal ou de synchronisation [CalDav](http://fr.wikipedia.org/wiki/CalDAV) ; il faut donc installer une [application tierce](https://play.google.com/store/apps/details?id=org.kc.and.ical&hl=fr) qui permet de faire la synchronisation.

### Sur iOS

TODO

### Avec Sunbird (intégré dans Thunderbird)

* Importer (ne sera pas actualisé) : Evenements et tâches > Importer > votre fichier .ics 
* Synchroniser : Agenda > Nouvel agenda > Sur le réseau > format iCalendar > url correspondant à votre emploi du temps

### Avec Google Calendar

* Importer (ne sera pas actualisé) :  https://www.google.com/calendar/render > Mes agendas > parametres > importer l'agenda > votre fichier .ics 

* Synchroniser : https://www.google.com/calendar/render > Autres agenda > ajouter par url > url correspondant à votre emploi du temps

### Avec Apple Calendar

TODO

##TODO

* Configurer la timezone avec VTIMEZONE 
* gestion des alternants, 3A, masters et enseignants
* Interfacer avec [radicale](http://radicale.org/) pour gérer le protocle CalDav plus approprié.
* Ajouter une interface web



##Dépendances

* Requests 
* iCalendar

Pour installer les dépendances, avec pip :

* installer pip : `sudo apt-get install python-pip`

* `pip install requests`

* `pip install iCalendar`

## Contact 

Vous pouvez m'envoyer un mail à showok chez showok.info

##Crédits
Sheep : [https://github.com/sheep/Chronos](Chronos)
