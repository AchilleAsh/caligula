# Caligula Parser
Ce programme permet de récupérer l'emploi du temps de [caligula](http://caligula.ensea.fr) au format standard [iCalendar](http://fr.wikipedia.org/wiki/ICalendar) (abrévié en iCal). Vous pouvez utiliser ce type de fichier sur n'importe quel logiciel d'agenda et ainsi intégrer les cours de l'ENSEA quelque soit votre système d'exploitation ou application préférée, sans utiliser un nouveau programme. 

##Exploitation des fichiers iCal

Les fichiers [iCal](http://en.wikipedia.org/wiki/ICalendar) (extension .ics) correspondent à la norme des calendriers. Vous pouvez soit :

* Télécharger le fichier .ics sur votre ordinateur et l'importer dans votre logiciel d'agenda

* Synchroniser votre agenda avec l'url complete du fichier .ics

Vous pouvez générer vous même les fichiers iCal avec le script ou simplement récupérer ceux que j'ai déja généré sur http://caligula.showok.info/ics/ . 

Une mise à jour tous les jours est faite sur ces fichiers à partir de caligula.ensea.fr .

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
* Synchroniser : Agenda > Nouvel agenda > Sur le réseau > format iCalendar > url correspondant à votre emploi du temps ; exemple : http://caligula.showok.info/ics/2G1_TP4.ics

### Avec Google Calendar

* Importer le fichier (ne sera pas actualisé) :  https://www.google.com/calendar/render > Mes agendas > parametres > importer l'agenda > votre fichier .ics 

* Synchroniser : https://www.google.com/calendar/render > Autres agenda > ajouter par url > url correspondant à votre emploi du temps ; eexemple :  http://caligula.showok.info/ics/2G1_TP4.ics

### Avec Apple Calendar

TODO

## Contact 

Pour toute question, bug, ou autre, vous pouvez m'envoyer un mail à showok chez showok.info

## Licence
Voir [licence](https://github.com/show0k/caligula/blob/master/LICENCE)


