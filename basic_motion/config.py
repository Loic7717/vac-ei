"""
Fichier de configuration pour le système de suivi de ligne
Modifiez ces paramètres pour adapter le comportement du robot
"""

# ============================================
# PARAMÈTRES CAMÉRA
# ============================================

# Résolution de la caméra (largeur, hauteur)
CAMERA_RESOLUTION = (160, 128)

# Mode du capteur PiCamera (1-7)
# Mode 2 = 3280x2464, Mode 4 = 1640x1232 (plus grand FoV)
CAMERA_SENSOR_MODE = 2

# Fréquence d'images (FPS)
CAMERA_FRAMERATE = 32


# ============================================
# PARAMÈTRES DE DÉTECTION DE LIGNE
# ============================================

# Taille du noyau de flou (réduction du bruit)
# Plus grand = plus de flou, moins sensible au bruit
BLUR_KERNEL_SIZE = (5, 5)

# Seuil de binarisation (0-255)
# Plus élevé = détecte seulement les zones très blanches
THRESHOLD_VALUE = 168

# Plage HSV pour détecter le blanc
# Format: [Hue, Saturation, Value]
HSV_LOWER_WHITE = [0, 0, 168]
HSV_UPPER_WHITE = [172, 111, 255]

# Taille des noyaux pour opérations morphologiques
# Érosion : supprime les petits objets blancs (bruit)
ERODE_KERNEL_SIZE = (6, 6)
ERODE_ITERATIONS = 1

# Dilatation : agrandit les objets blancs
DILATE_KERNEL_SIZE = (4, 4)
DILATE_ITERATIONS = 1


# ============================================
# PARAMÈTRES DE CONTRÔLE
# ============================================

# Zone morte (en pixels)
# Si l'erreur est inférieure, le robot va tout droit
# Plus grand = moins d'oscillations, mais moins précis
DEAD_ZONE = 10

# Vitesse de base des moteurs (0-255)
# Vitesse nominale quand le robot va tout droit
BASE_SPEED = 100

# Facteur de correction (0.0 - 1.0)
# Définit l'intensité de la correction dans les virages
# 0.5 = réduction max de 50% de la vitesse du moteur intérieur
CORRECTION_FACTOR = 0.5

# Vitesse minimale des moteurs (0-255)
# Empêche les moteurs de s'arrêter complètement dans les virages
MIN_SPEED = 50


# ============================================
# PARAMÈTRES DE COMMUNICATION
# ============================================

# Port série de l'Arduino
# Valeurs possibles: '/dev/ttyACM0', '/dev/ttyUSB0', '/dev/ttyAMA0'
ARDUINO_PORT = '/dev/ttyACM0'

# Baudrate (vitesse de communication)
ARDUINO_BAUDRATE = 115200

# Timeout de lecture (secondes)
ARDUINO_TIMEOUT = 0.1


# ============================================
# PARAMÈTRES DE PERFORMANCE
# ============================================

# Fréquence de la boucle de contrôle (Hz)
# 20 Hz = 50ms entre chaque itération
CONTROL_LOOP_FREQUENCY = 20

# Délai entre les frames (secondes)
FRAME_DELAY = 1.0 / CONTROL_LOOP_FREQUENCY

# Afficher les statistiques tous les X frames
STATS_DISPLAY_INTERVAL = 10


# ============================================
# PARAMÈTRES DE DEBUG
# ============================================

# Afficher l'image avec les contours détectés
DEBUG_SHOW_CONTOURS = False

# Afficher les informations de détection
DEBUG_PRINT_DETECTION = True

# Afficher les commandes envoyées
DEBUG_PRINT_COMMANDS = True

# Sauvegarder les images pour analyse
DEBUG_SAVE_IMAGES = False
DEBUG_SAVE_PATH = "/tmp/line_tracking/"


# ============================================
# PROFILS PRÉDÉFINIS
# ============================================

def load_profile(profile_name):
    """
    Charge un profil de configuration prédéfini
    
    Profils disponibles:
    - 'default': Configuration par défaut
    - 'aggressive': Virages rapides, idéal pour circuit avec virages serrés
    - 'smooth': Virages doux, idéal pour débutants
    - 'fast': Vitesse élevée, pour circuit simple
    - 'precise': Très précis mais lent
    """
    global BASE_SPEED, CORRECTION_FACTOR, DEAD_ZONE, MIN_SPEED
    
    profiles = {
        'default': {
            'BASE_SPEED': 100,
            'CORRECTION_FACTOR': 0.5,
            'DEAD_ZONE': 10,
            'MIN_SPEED': 50
        },
        'aggressive': {
            'BASE_SPEED': 120,
            'CORRECTION_FACTOR': 0.7,
            'DEAD_ZONE': 5,
            'MIN_SPEED': 40
        },
        'smooth': {
            'BASE_SPEED': 80,
            'CORRECTION_FACTOR': 0.3,
            'DEAD_ZONE': 15,
            'MIN_SPEED': 60
        },
        'fast': {
            'BASE_SPEED': 150,
            'CORRECTION_FACTOR': 0.4,
            'DEAD_ZONE': 8,
            'MIN_SPEED': 80
        },
        'precise': {
            'BASE_SPEED': 60,
            'CORRECTION_FACTOR': 0.6,
            'DEAD_ZONE': 5,
            'MIN_SPEED': 30
        }
    }
    
    if profile_name in profiles:
        profile = profiles[profile_name]
        BASE_SPEED = profile['BASE_SPEED']
        CORRECTION_FACTOR = profile['CORRECTION_FACTOR']
        DEAD_ZONE = profile['DEAD_ZONE']
        MIN_SPEED = profile['MIN_SPEED']
        print(f"✓ Profil '{profile_name}' chargé")
        print(f"  BASE_SPEED={BASE_SPEED}, CORRECTION_FACTOR={CORRECTION_FACTOR}")
        print(f"  DEAD_ZONE={DEAD_ZONE}, MIN_SPEED={MIN_SPEED}")
        return True
    else:
        print(f"✗ Profil '{profile_name}' inconnu")
        print(f"  Profils disponibles: {', '.join(profiles.keys())}")
        return False


# ============================================
# GUIDE D'AJUSTEMENT
# ============================================

"""
GUIDE D'AJUSTEMENT DES PARAMÈTRES:

1. Le robot oscille trop (zigzague):
   - Augmenter DEAD_ZONE (ex: 15-20)
   - Réduire CORRECTION_FACTOR (ex: 0.3-0.4)
   - Réduire BASE_SPEED

2. Le robot ne suit pas bien la ligne:
   - Réduire DEAD_ZONE (ex: 5-8)
   - Augmenter CORRECTION_FACTOR (ex: 0.6-0.8)
   - Vérifier les seuils HSV

3. Le robot perd la ligne dans les virages:
   - Augmenter CORRECTION_FACTOR
   - Réduire MIN_SPEED (permet des virages plus serrés)
   - Augmenter la fréquence (CONTROL_LOOP_FREQUENCY)

4. La détection ne fonctionne pas:
   - Ajuster THRESHOLD_VALUE selon l'éclairage
   - Modifier HSV_LOWER_WHITE et HSV_UPPER_WHITE
   - Augmenter BLUR_KERNEL_SIZE si trop de bruit

5. Le robot est trop lent:
   - Augmenter BASE_SPEED (max 255)
   - Essayer le profil 'fast'

6. Le robot rate les virages serrés:
   - Essayer le profil 'aggressive'
   - Réduire MIN_SPEED
   - Augmenter CORRECTION_FACTOR

ASTUCE: Commencez avec le profil 'smooth' et ajustez progressivement
"""

if __name__ == "__main__":
    print("Configuration du système de suivi de ligne")
    print("="*50)
    print(f"\nCAMÉRA:")
    print(f"  Résolution: {CAMERA_RESOLUTION}")
    print(f"  Framerate: {CAMERA_FRAMERATE} FPS")
    print(f"\nCONTRÔLE:")
    print(f"  Vitesse de base: {BASE_SPEED}")
    print(f"  Zone morte: ±{DEAD_ZONE} pixels")
    print(f"  Facteur de correction: {CORRECTION_FACTOR}")
    print(f"  Vitesse minimale: {MIN_SPEED}")
    print(f"\nCOMMUNICATION:")
    print(f"  Port: {ARDUINO_PORT}")
    print(f"  Baudrate: {ARDUINO_BAUDRATE}")
    print("="*50)
    
    print("\nProfils disponibles:")
    for profile in ['default', 'aggressive', 'smooth', 'fast', 'precise']:
        print(f"  - {profile}")
