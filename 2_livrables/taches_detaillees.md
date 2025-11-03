## Phase 0 - Organisation generale
- [] Valider la composition de l'equipe et les roles Et.1 a Et.5.
- [+] Partager les coordonnees et mettre en place un canal de communication (Slack/Teams).
- [] Planifier les revues quotidiennes (stand-up) et les jalons (mi-parcours, demo finale).
- [] Configurer le depot Git commun et definir les regles de branche/merge.

## Phase 1 - Preparation materielle
- [] Inventorier le contenu du kit robot et verifier l'etat du chariot.
- [] Charger les batteries Varta 5V et Ansmann NiMH (>=3h / >=5h).
- [] Monter les roues, serrer les vis (cle 2 mm) et controler le jeu mecanique.
- [] Cabler le Raspberry Pi (camera CSI, alimentation) et l'Arduino Romeo (USB).
- [] Verifier le branchement des moteurs sur le PCB (pins Enable/PWM).

## Phase 2 - Mise en service du robot
- [] Alimenter la logique (batterie 5V) et demarrer le Raspberry (attendre boot complet).
- [] Alimenter la puissance moteurs via le DC jack et placer l'interrupteur PCB sur "1".
- [] Connecter le Raspberry au PC via Ethernet direct et etablir la session VNC initiale.
- [] Enregistrer le reseau WiFi de reference et noter l'adresse IP fixe (ifconfig wlan0).
- [] Tester le redemarrage complet batterie + WiFi et la reconnection VNC.

## Phase 3 - Outils logiciels et environnement
- [] Mettre a jour le Raspberry (apt, pip) et installer les dependances Python requises.
- [] Cloner le depot EI dans /home/pi et verifier les droits d'execution.
- [] Configurer l'IDE Arduino avec les cartes Romeo et importer serial_link.ino.
- [] Installer les bibliotheques Python (opencv, numpy, picamera, pyzmq, pyserial).
- [] Configurer un dossier /var/log/vac pour les journaux et limiter la taille (logrotate).

## Phase 4 - Tests unitaires materiels
- [] Televerser `test_servos/test_servos.ino` et verifier le balayage manuel (f40, etc.).
- [] Televerser `test_ultrasonic/test_ultrasonic.ino` et confirmer la mesure distance + servo.
- [] Televerser `test_infrared/test_infrared.ino` pour calibrer le seuil d'obstacle.
- [] Televerser `test_motors/test_motors.ino` pour valider le sens et la vitesse des roues.
- [] Televerser `test_encoders/test_encoders.ino` et relever les impulsions par tour.

## Phase 5 - Perception vision
- [] Capturer un flux camera de reference avec `perception_students.py` et sauvegarder echantillons.
- [] Ajuster la resolution/cadrage (CAMERA_MODE, exposition) et valider la cadence (>25 fps).
- [] Iterer sur `basic_image_processing/line_detection.py` pour filtrer la ligne blanche.
- [] Implementer la detection de carrefour (segmentation + heuristique de branche).
- [] Ajouter un module de suivi (calcul d'offset lateral + angle) et logger les mesures.

## Phase 6 - Commande mouvement
- [] Etendre `serial_link.ino` pour calculer vitesse1/vitesse2 dans task2 (encodeurs -> rad/s).
- [] Mettre en place l'acceleration progressive (task3) et definir profils vitesse cible.
- [] Implementer la fermeture de boucle dans `dialogue.py` (PI sur offset ligne -> commande moteurs).
- [] Verifier la gestion des acquittements (A20, OK/OB/ER) et gerer les erreurs.
- [] Integrer une commande de freinage d'urgence (set moteurs a 0 si timeout >500 ms).

## Phase 7 - Gestion obstacles
- [] Programmer le balayage servo + URM37 et fusionner les mesures en matrice polar.
- [] Definir des zones de securite (distance min frontale / laterale) et tester en laboratoire.
- [] Relier la protection infrarouge (I1/I0) a l'etat global de commande.
- [] Implementer le contournement: ralentir, arret, manoeuvre alternative puis reprise ligne.
- [] Logger chaque detection d'obstacle (timestamp, type capteur, decision prise).

## Phase 8 - Supervision et teleoperation
- [] Deployer `basic_infrastructure/server.py` sur un PC maitre et ouvrir le port 5005.
- [] Tester `control.py` pour l'envoi de touches et `robot.py` pour la reception.
- [] Ajouter une remontee d'etat (cle `key`, telemetrie) dans le message retour.
- [] Configurer un dashboard (terminal ou notebook) pour visualiser vitesse, erreur, tension.
- [] Documenter la procedure de bascule teleop -> autonome avec criteres clairs.

## Phase 9 - Validation terrain
- [] Definir le plan d'essais (scenario ligne simple, carrefour, obstacle mobile).
- [] Mesurer les performances (temps au tour, deviation max, taux faux positifs obstacle).
- [] Capturer video + logs pour chaque run et archiver dans /var/log/vac/YYYYMMDD.
- [] Realiser une revue de securite (checklist pre-run, coupe circuit, zone libre).
- [] Consolider les actions correctives et replanifier les essais si besoin.

## Phase 10 - Documentation et livrables
- [] Mettre a jour `Strategie-Systeme.md` avec les decisions et changements majeurs.
- [] Exporter le schema Mermaid (`schema_systeme_mermaid.md`) en image pour les slides.
- [] Rediger la notice d'exploitation (demarrage, teleop, sequence arret d'urgence).
- [] Compiler le rapport final (objectif, architecture, resultats, axes d'amelioration).
- [] Nettoyer le depot (branche principale a jour, tags version, suppr fichiers temporaires).
