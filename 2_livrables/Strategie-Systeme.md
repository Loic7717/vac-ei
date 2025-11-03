**Membres :**
- Rafael Maestre López – `Et.1` – Référent perception & simulation (rafael.maestre-lopez@student-cs.fr)  
- Gabriel Sylvestre Núñez – `Et.2` – Référent logiciel embarqué & communication (gabriel.sylvestre-nunez@student-cs.fr)  
- Lûqman Proietti – `Et.3` – Référent mouvement & asservissement (luqman.proietti@student-cs.fr)  
- Matthieu Giraud-Sauveur – `Et.4` – Coordinateur intégration & qualité (matthieu.giraud-sauveur@student-cs.fr)  
- Loïc Perthuis – `Et.5` – Référent tests, documentation & support opérationnel (loic.perthuis@student-cs.fr)

**Enjeux et défis de l’EI :**
Enjeu 1 : Navigation autonome sur la ligne de course  
  Défi 1.1 : Calibrer la caméra Pi et stabiliser le flux (réglage `CAMERA_MODE`, exposition).  
  Défi 1.2 : Détecter la trajectoire (scripts `basic_image_processing/line_detection.py`, `perception_students.py`) et gérer carrefours/virages.  
  Défi 1.3 : Boucler l’asservissement vitesse/angle via le lien série (`basic_motion/serial_link/serial_link.ino`, `dialogue.py`) en maintenant la stabilité dynamique.

Enjeu 2 : Sécurité et gestion proactive des obstacles  
  Défi 2.1 : Exploiter le servo avant pour balayer l’URM37 et créer une carte d’occupation locale.  
  Défi 2.2 : Paramétrer la protection infrarouge (commandes `I0/I1`) et définir les seuils de déclenchement.  
  Défi 2.3 : Orchestrer les scénarios d’arrêt/reprise (commande `H` hold, `R` resume) et les plans de contournement.

Enjeu 3 : Infrastructure fiable et cycles d’essais rapides  
  Défi 3.1 : Industrialiser la communication Raspberry Pi <-> Arduino (protocole ASCII/binaire, gestion des acquittements `A2y`).  
  Défi 3.2 : Maintenir l’accès distant (VNC, ZMQ `basic_infrastructure/server.py`, `control.py`, `robot.py`) pour les tests et la télémétrie.  
  Défi 3.3 : Sécuriser l’alimentation (batteries NiMH / Li-Ion, double rail) et tracer l’état de charge pour chaque session d’essai.

**Tâches et livrables :**

| #   | Description                                                                              | Responsable | Équipe             | Deadline    |
| --- | ---------------------------------------------------------------------------------------- | ----------- | ------------------ | ----------- |
| T.1 | Mise en service du robot (alimentation, câblage standard, tests unitaires fournis)       | Et.3        | Et.2, Et.3         | Lundi 14h   |
| T.2 | Chaîne perception -> décision -> commande pour le suivi de ligne                           | Et.1        | Et.1, Et.2, Et.3   | Mardi 17h   |
| T.3 | Intégration obstacle (URM37 + IR) et logique de contournement                            | Et.5        | Et.3, Et.5         | Mercredi 17h|
| T.4 | Pipeline de supervision & téléop (serveur ZMQ, journalisation, scripts de diagnostic)    | Et.4        | Et.2, Et.4, Et.5   | Jeudi 12h   |
| T.5 | Validation terrain : campagne d’essais + plan de mitigation des risques                  | Et.4        | Toute l’équipe     | Vendredi 15h|
| L.1 | Présent document "Stratégie d’équipe & Schéma du système"                              | Et.4        |                    | Lundi 12h   |
| L.2 | Schéma d’architecture validé et partagé (format A3 + version numérique)                  | Et.2        | Et.1, Et.2         | Mercredi 10h|
| L.3 | Démo mi-parcours (suivi de ligne stabilisé + arrêt obstacle)                             | Et.5        | Toute l’équipe     | Jeudi 17h   |
| L.4 | Rapport de fin d’EI + dépôt du code nettoyé (Git + documentation d’exploitation)         | Et.1        | Toute l’équipe     | Vendredi 18h|

**Schéma du système (architecture organique) :**
- Niveau décision : Raspberry Pi 3B+ exécute la perception (caméra CSI), la planification trajet et le suivi d’état. Il s’appuie sur Python (`basic_image_processing`, `basic_motion/dialogue.py`) et échange les ordres via USB.
- Niveau actionnement : Arduino Romeo BLE (`serial_link.ino`) pilote moteurs DC (Joy-It COM-MOTOR06) et servomoteur avant, calcule vitesses (encodeurs) et applique rampes d’accélération.
- Capteurs :  
  - Vision : caméra Pi (160×128 @32 fps).  
  - Proximité : URM37 sur servo (balayage 180°) et IR GP2Y0A21 aligné avant.  
  - Retour mouvement : encodeurs quadrature intégrés aux moteurs.
- Communication externe : serveur ZMQ (`basic_infrastructure/server.py`) relie téléop (`control.py`) et robot (`robot.py`), utile pour monitoring et scénarios de secours.
- Alimentation : double circuit (moteurs via NiMH 6×AA ou Li-Ion 5 V, logique via Varta 5 V 2.4 A). Interrupteur PCB sur position "1" pour activer drivers moteurs.

```
[Caméra Pi] --> [Raspberry Pi : perception + décision] --USB/Serial--> [Arduino Romeo] --> [Ponts moteurs & roues]
                         ^                       ^                         |
                         |                       |                         +--> [Servomoteur + URM37]
           [Serveur ZMQ & poste de contrôle]     |                         +--> [Protection IR & encodeurs]
                         |                       |
                  [VNC / SSH / VNCviewer]        |
                         +------ Supervision & updates ------+
```

- Gestion des risques :  
  - Blocage capteur : prévoir mode dégradé sans caméra (IR + encodeurs) pour rouler lentement.  
  - Rupture liaison série : watchdog côté Arduino (commandes `a`/`A2y`), arrêt moteur si absence d’ordre >500 ms.  
  - Chute tension batterie : mesure tension (`T`), seuil d’alerte remonté au Raspberry pour basculer sur charge pleine.

- Plan d’itération hebdomadaire : tests unitaires matin, intégration après-midi, déploiement terrain fin de journée avec journalisation systématique (`/var/log/vac/`).
