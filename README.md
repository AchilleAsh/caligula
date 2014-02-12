Ce programme permet de récupérer l'emploi du temps de [caligula](http://caligula.ensea.fr) au format standard [iCalendar](http://fr.wikipedia.org/wiki/ICalendar) (abrévié en iCal). Vous pouvez utiliser ce type de fichier sur n'importe quel logiciel d'agenda et ainsi intégrer les cours de l'ENSEA quelque soit votre système d'exploitation ou application préférée, sans utiliser un nouveau programme. 
C'est un logiciel libre, vous pouvez utilisez ce script pour générer vous même les fichiers de calendrier (et modifier et redistribuer le script selon les termes de la licence) ou simplement utiliser les fichiers iCal fournis.

##Exploitation des fichiers iCal

Les fichiers [iCal](http://en.wikipedia.org/wiki/ICalendar) (extension .ics) correspondent à la norme des calendriers. Vous pouvez soit :
* Télécharger le fichier .ics sur votre ordinateur et l'importer dans votre logiciel d'agenda
* Synchroniser votre agenda avec l'url complete du fichier .ics

Vous pouvez générer les fichiers iCal avec le script ou simplement récupérer ceux que j'ai déja généré récupérer sur http://showok.info/caligula/ics. Les noms des fichiers correspondent aux nom complet du TP : si vous êtes dans le 1G3TD2TP3 le fichier d'emploi du temps sera *1G3TD2TP3.ics* et sera téléchargeable (et synchronisable) sur http://showok.info/caligula/ics/1G3TD2TP3.ics

Une mise à jour tous les jours à minuit est faite sur ces fichiers à partir de caligula.ensea.fr .

### Sur android

Vous pouvez visualiser votre emploi du temps avec l'application native d'agenda, mais il faut d'abord pouvoir lui faire lire le fichier iCal.

#### Avec un compte Google

Vous pouvez utiliser un compte google pour synchroniser ses contacts ; suivre la rubrique 'Avec Google Calendar'.

#### Sans compte google

L'application d'agenda ne gère pas l'import de fichiers iCal ou de synchronisation [CalDav](http://fr.wikipedia.org/wiki/CalDAV) ; il faut donc installer une [application tierce](https://play.google.com/store/apps/details?id=org.kc.and.ical&hl=fr) qui permet de faire la synchronisation. C'est tout aussi simple que de passer par Google Calendar, et ça fera une chose de moins que google aura de vous.

### Sur iOS

TODO

### Avec Sunbird (intégré dans Thunderbird)

* Importer (ne sera pas actualisé) : Evenements et tâches > Importer > votre fichier .ics 
* Synchroniser : Agenda > Nouvel agenda > Sur le réseau > format iCalendar > url correspondant à votre emploi du temps ; exemple : http://showok.info/caligula/ics/2G1TD2TP4.ics

### Avec Google Calendar

* Importer le fichier (ne sera pas actualisé) :  https://www.google.com/calendar/render > Mes agendas > parametres > importer l'agenda > votre fichier .ics 

* Synchroniser : https://www.google.com/calendar/render > Autres agenda > ajouter par url > url correspondant à votre emploi du temps ; eexemple : http://showok.info/caligula/ics/2G1TD2TP4.ics

### Avec Apple Calendar

TODO




##Usage
Pour générer les fichier iCal

`python caligula.py -g <Groupe de la forme _G_TD_TP_ > `

exemple, pour créer l'agenda du groupe 1G3TD2TP3 : `python caligula.py -g 1G3TD2TP3`

exemple, pour créer l'agenda du groupe ESATP3 : `python caligula.py -g ESATP3`

exemple pour créer tous les agendas possibles : `python caligula.py -g all`


##Dépendances
Il faut d'abord installer python (natif sous les systèmes Unix comme MacOSX et GNU/Linux).

Les deux librairies python ci-dessous ne sont pas dans le package par défault. 
* Requests 
* iCalendar

Pour installer les dépendances, avec pip :

* installer pip : `sudo apt-get install python-pip`

* `pip install requests`

* `pip install iCalendar`


##TODO

* gestion *automatique* des id correspondants à l'emploi du temps
* gestion des alternants, 3A, masters et enseignants
* améliorer la gestion des parametres d'entrée pour pouvoir avoir le choix du fichier à récupérer

 
## Contact 

Pour toute question, bug, ou autre, vous pouvez m'envoyer un mail à showok chez showok.info

## Licence
Voir licence


