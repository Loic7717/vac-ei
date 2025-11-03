**Nº et nom d'équipe :** Équipe 6 – CTM (Connected Turbo Motors)

**Membres :**
- Rafael Maestre López – `Et.1` – Référent perception & simulation (rafael.maestre-lopez@student-cs.fr)  
- Gabriel Sylvestre Núñez – `Et.2` – Référent logiciel embarqué & communication (gabriel.sylvestre-nunez@student-cs.fr)  
- Lûqman Proietti – `Et.3` – Référent mouvement & asservissement (luqman.proietti@student-cs.fr)  
- Matthieu Giraud-Sauveur – `Et.4` – Coordinateur intégration & qualité (matthieu.giraud-sauveur@student-cs.fr)  
- Loïc Perthuis – `Et.5` – Référent tests, documentation & support opérationnel (loic.perthuis@student-cs.fr)

**Enjeux et défis de l’EI :**
Enjeu 1 : Sécurité proactive et gestion robuste des obstacles  
  Défi 1.1 : Qualifier la détection en combinant URM37 et IR sur toute la plage utile, y compris sous forte luminosité.  
  Défi 1.2 : Filtrer l’éblouissement solaire et les retours parasites via calibration dynamique et fusion temporelle.  
  Défi 1.3 : Orchestrer la réponse (ralentir, contournement, reprise de trajectoire) avec journalisation pour validation.

Enjeu 2 : Suivi de ligne résilient et repositionnement rapide  
  Défi 2.1 : Stabiliser la perception de la ligne (réglages caméra, pipeline vision) pour tenir une trajectoire continue.  
  Défi 2.2 : Gérer intersections, virages serrés et changements de texture sans perte de suivi.  
  Défi 2.3 : Mettre en œuvre une stratégie de recapture lorsqu’on perd la ligne (balayage vision + encodeurs).

Enjeu 3 : Trajet intelligent et performance mission  
  Défi 3.1 : Modéliser la piste dans un simulateur pour comparer les stratégies de navigation.  
  Défi 3.2 : Décider en temps réel de la meilleure option (contournement, attente, reroutage) face aux obstacles.  
  Défi 3.3 : Optimiser le temps de parcours en ajustant consignes moteurs et budget énergétique sous contraintes de sécurité.

**Tâches et livrables :**

| #    | Description                                                                                          | Responsable | Équipe                | Deadline      |
| ---- | ---------------------------------------------------------------------------------------------------- | ----------- | --------------------- | ------------- |
| T.0  | Branchements et raccordements électroniques (moteurs, capteurs, alimentation)                        | Et.3        | Et.2, Et.3            | Lundi 11h     |
| T.1  | Conception du simulateur d’itinéraires et import des tracés de référence                              | Et.1        | Et.1, Et.4            | Mardi 17h     |
| T.2  | Caractérisation des capteurs (URM37, IR) et choix des configurations physiques                        | Et.5        | Et.2, Et.5            | Lundi 16h15   |
| T.3  | Calibration anti-éblouissement et positionnement des capteurs face à la lumière directe              | Et.2        | Et.2, Et.5            | Lundi 18h     |
| T.4  | Premier algorithme embarqué de détection d’obstacle sur le robot                                     | Et.5        | Et.3, Et.5            | Mardi 16h15   |
| T.5  | Fusion URM/IR et filtrage des faux positifs (objets hors trajectoire)                                | Et.5        | Et.1, Et.5            | Mardi 18h     |
| T.6  | Détection de la ligne au sol et calibration caméra (balance des blancs, exposition)                  | Et.1        | Et.1, Et.2            | Mercredi 11h30 |
| T.7  | Gestion des intersections et stratégie de recapture de ligne                                         | Et.1        | Et.1, Et.3            | Mercredi 16h00 |
| T.8  | Calcul des consignes roues et fermeture de la boucle de rétroaction                                  | Et.3        | Et.1, Et.3            | Mercredi 17h30 |
| T.9  | Intégration perception-commande et essais piste "huit" avec logging complet                          | Et.4        | Toute l’équipe        | Jeudi 09h00   |
| T.10 | Dashboard ZMQ : journalisation temps réel et monitoring (tension, vitesse, états)                    | Et.4        | Et.2, Et.4            | Jeudi 15h     |
| T.11 | Optimisation des stratégies de trajectoire (vitesses cibles, choix de voie)                          | Et.3        | Et.1, Et.3            | Vendredi 11h  |
| T.12 | Validation finale terrain + script de redéploiement et checklist de sécurité                         | Et.4        | Toute l’équipe        | Vendredi 15h  |
| L.1  | Document "Stratégie d’équipe & Schéma du système"                                                    | Et.4        |                       | Lundi 12h     |
| L.2  | Schéma d’architecture validé (version A3 + numérique)                                                | Et.2        | Et.1, Et.2            | Mercredi 10h  |
| L.3  | Démo mi-parcours (suivi de ligne stabilisé + arrêt obstacle)                                         | Et.5        | Toute l’équipe        | Jeudi 17h     |
| L.4  | Démo piste "huit" et rapport de tests associés                                                       | Et.5        | Toute l’équipe        | Jeudi 10h     |
| L.5  | Soutenance finale et remise du rapport d’exploitation                                                | Et.1        | Toute l’équipe        | Vendredi 17h  |

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
