# Système de Suivi de Ligne Autonome

## Description

Ce système intègre la détection de ligne avec le contrôle des moteurs pour permettre au robot de suivre automatiquement une ligne blanche sur le sol.

## Fichiers

- **`dialogue.py`** : Script principal avec connexion Arduino et mode autonome
- **`test_line_tracking.py`** : Script de test pour la vision sans Arduino
- **`perception_students.py`** : Capture d'image depuis la PiCamera
- **`line_detection.py`** : Algorithme de détection de ligne

## Fonctionnement

### 1. Détection de Ligne

L'algorithme de détection :
1. Capture une image depuis la PiCamera
2. Applique un flou pour réduire le bruit
3. Effectue un seuillage pour isoler les zones blanches
4. Convertit en espace HSV
5. Crée un masque pour détecter la ligne blanche
6. Applique des opérations morphologiques (érosion/dilatation)
7. Détecte les contours et garde le plus grand
8. Calcule le centroïde de la ligne détectée

### 2. Calcul de la Commande

Basé sur la position du centroïde :
- **Ligne centrée** (erreur < 10 pixels) : Avance tout droit (L=100, R=100)
- **Ligne à gauche** : Réduit la vitesse de la roue gauche pour tourner à gauche
- **Ligne à droite** : Réduit la vitesse de la roue droite pour tourner à droite

La correction est proportionnelle à l'erreur de position.

### 3. Envoi des Commandes

Les commandes sont envoyées à l'Arduino via le port série :
```
M L<vitesse_gauche> R<vitesse_droite>
```

Vitesses entre -255 et 255.

## Utilisation

### Option 1 : Test sans Arduino (Vision seule)

Pour tester uniquement la détection de ligne :

```bash
python3 test_line_tracking.py
```

Ce script affiche :
- L'image avec les contours détectés
- Le centroïde de la ligne
- La ligne centrale de référence
- Les commandes calculées (sans les envoyer)
- Les statistiques (FPS, etc.)

Appuyez sur **'q'** pour quitter.

### Option 2 : Mode Complet avec Arduino

Pour utiliser le système complet avec le robot :

```bash
python3 dialogue.py
```

Menu principal :
1. **Dialogue direct avec Arduino** : Mode manuel pour tester les commandes
2. **Mode suivi de ligne autonome** : Lance le suivi automatique
3. **Q** : Quitter

En mode autonome :
- Le robot capture des images continuellement
- Détecte la ligne blanche
- Calcule et envoie les commandes de correction
- Affiche les statistiques en temps réel

Appuyez sur **Ctrl+C** pour arrêter le suivi autonome.

## Configuration

### Paramètres de la Caméra

Dans le script (résolution par défaut) :
```python
resolution_target = (160, 128)
```

### Paramètres de Détection

- **Seuil de blanc** : 168-255
- **Zone morte** : ±10 pixels (évite les oscillations)
- **Vitesse de base** : 100 (sur 255)
- **Correction maximale** : 50% de la vitesse

### Format des Commandes Arduino

Assurez-vous que votre code Arduino (`serial_link.ino`) accepte les commandes au format :
```
M L<left_speed> R<right_speed>
```

Exemple : `M L100 R80` (avance en tournant légèrement à droite)

## Dépendances

```bash
pip3 install numpy opencv-python pyserial picamera
```

Sur Raspberry Pi :
```bash
sudo apt-get install python3-picamera
pip3 install "picamera[array]"
```

## Dépannage

### La caméra ne fonctionne pas
- Vérifiez que la PiCamera est bien connectée
- Activez l'interface caméra : `sudo raspi-config` → Interface Options → Camera
- Redémarrez le Raspberry Pi

### Aucune ligne détectée
- Vérifiez l'éclairage (ligne blanche sur fond sombre)
- Ajustez les seuils de détection dans `detect_line()`
- Utilisez `test_line_tracking.py` pour déboguer visuellement

### L'Arduino ne répond pas
- Vérifiez le port série : `/dev/ttyACM0` (peut être `/dev/ttyUSB0`)
- Vérifiez le baudrate : 115200
- Testez avec le mode "Dialogue direct"

### Le robot oscille trop
- Augmentez la zone morte (dead_zone)
- Réduisez la correction maximale
- Diminuez la vitesse de base

## Améliorations Possibles

1. **Filtre de Kalman** : Pour lisser les commandes et éviter les oscillations
2. **Anticipation** : Regarder plus loin sur la ligne pour anticiper les virages
3. **Vitesse adaptative** : Ralentir dans les virages serrés
4. **Détection multi-lignes** : Gérer les intersections
5. **Logging** : Enregistrer les données pour analyse
6. **PID Controller** : Remplacer la correction proportionnelle simple par un PID

## Architecture du Code

```
dialogue.py
├── init_camera()                    # Initialisation PiCamera
├── capture_image()                  # Capture d'image
├── detect_line()                    # Détection de ligne
├── compute_steering_command()       # Calcul de la commande
├── send_motor_command()             # Envoi à Arduino
└── autonomous_line_following()      # Boucle principale

test_line_tracking.py
└── main()                           # Test sans Arduino
```

## Exemple de Session

```
Connection à l'arduino
OK-A20

==================================================
MENU PRINCIPAL
==================================================
1. Dialogue direct avec Arduino
2. Mode suivi de ligne autonome
Q. Quitter
==================================================
Votre choix: 2
Durée du suivi (en secondes, 0 pour infini): 30

==================================================
DÉMARRAGE DU MODE SUIVI DE LIGNE AUTONOME
==================================================
Appuyez sur Ctrl+C pour arrêter

✓ Caméra initialisée
Centroïde détecté à: (85, 64)
→ Ligne à droite (erreur: 5.0) - Tourne à droite
Arduino: OK
[Stats] Frames: 10 | FPS: 19.2
Centroïde détecté à: (80, 64)
✓ Ligne centrée - Avance tout droit
Arduino: OK
...
```

## Contact

Pour toute question sur l'implémentation, consultez la documentation ou contactez l'équipe pédagogique.
