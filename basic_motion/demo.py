#!/usr/bin/env python3
"""
Script de démonstration et test du système de suivi de ligne
Permet de tester différentes configurations et profils
"""

import sys
import os
import time

# Import du fichier de configuration
try:
    import config
except ImportError:
    print("Erreur: Impossible d'importer config.py")
    print("Assurez-vous que config.py est dans le même dossier")
    sys.exit(1)

def print_banner():
    """Affiche une bannière d'accueil"""
    print("\n" + "="*70)
    print(" " * 15 + "SYSTÈME DE SUIVI DE LIGNE AUTONOME")
    print(" " * 20 + "CentraleSupélec - ST5 VAC")
    print("="*70)

def print_menu():
    """Affiche le menu principal"""
    print("\n" + "-"*70)
    print("MENU DE DÉMONSTRATION ET TEST")
    print("-"*70)
    print("1. Afficher la configuration actuelle")
    print("2. Charger un profil de configuration")
    print("3. Tester la détection de ligne (sans Arduino)")
    print("4. Tester la communication Arduino")
    print("5. Lancer le mode autonome complet")
    print("6. Simuler le calcul des commandes")
    print("7. Visualiser le système (diagramme)")
    print("Q. Quitter")
    print("-"*70)

def show_current_config():
    """Affiche la configuration actuelle"""
    print("\n" + "="*70)
    print("CONFIGURATION ACTUELLE")
    print("="*70)
    
    print("\n📷 CAMÉRA:")
    print(f"   Résolution: {config.CAMERA_RESOLUTION[0]}x{config.CAMERA_RESOLUTION[1]}")
    print(f"   Mode capteur: {config.CAMERA_SENSOR_MODE}")
    print(f"   Framerate: {config.CAMERA_FRAMERATE} FPS")
    
    print("\n🔍 DÉTECTION:")
    print(f"   Seuil de binarisation: {config.THRESHOLD_VALUE}")
    print(f"   Taille flou: {config.BLUR_KERNEL_SIZE}")
    print(f"   HSV blanc (min): {config.HSV_LOWER_WHITE}")
    print(f"   HSV blanc (max): {config.HSV_UPPER_WHITE}")
    
    print("\n🎮 CONTRÔLE:")
    print(f"   Vitesse de base: {config.BASE_SPEED} / 255")
    print(f"   Zone morte: ±{config.DEAD_ZONE} pixels")
    print(f"   Facteur correction: {config.CORRECTION_FACTOR}")
    print(f"   Vitesse minimale: {config.MIN_SPEED} / 255")
    
    print("\n🔌 COMMUNICATION:")
    print(f"   Port Arduino: {config.ARDUINO_PORT}")
    print(f"   Baudrate: {config.ARDUINO_BAUDRATE}")
    print(f"   Timeout: {config.ARDUINO_TIMEOUT}s")
    
    print("\n⚡ PERFORMANCE:")
    print(f"   Fréquence contrôle: {config.CONTROL_LOOP_FREQUENCY} Hz")
    print(f"   Délai frame: {config.FRAME_DELAY*1000:.1f} ms")
    
    print("="*70)

def load_profile_interactive():
    """Charge un profil de configuration de manière interactive"""
    print("\n" + "="*70)
    print("PROFILS DE CONFIGURATION DISPONIBLES")
    print("="*70)
    
    profiles = {
        '1': ('default', 'Configuration par défaut, équilibrée'),
        '2': ('aggressive', 'Virages rapides, pour circuit avec virages serrés'),
        '3': ('smooth', 'Virages doux, idéal pour débutants'),
        '4': ('fast', 'Vitesse élevée, pour circuit simple'),
        '5': ('precise', 'Très précis mais lent')
    }
    
    for key, (name, desc) in profiles.items():
        print(f"{key}. {name:12} - {desc}")
    
    print("-"*70)
    choice = input("Choisissez un profil (1-5, ou Q pour annuler): ").strip().upper()
    
    if choice in profiles:
        profile_name = profiles[choice][0]
        print(f"\nChargement du profil '{profile_name}'...")
        config.load_profile(profile_name)
        print("✓ Profil chargé avec succès!")
        return True
    elif choice == 'Q':
        print("Annulé")
        return False
    else:
        print("✗ Choix invalide")
        return False

def test_line_detection():
    """Lance le test de détection de ligne sans Arduino"""
    print("\n" + "="*70)
    print("TEST DE DÉTECTION DE LIGNE")
    print("="*70)
    print("\nCe test lance la détection visuelle sans connexion Arduino.")
    print("Appuyez sur 'q' dans la fenêtre vidéo pour quitter.\n")
    
    confirm = input("Lancer le test ? (o/N): ").strip().lower()
    if confirm == 'o':
        print("\nLancement du test...")
        try:
            import subprocess
            result = subprocess.run([sys.executable, "test_line_tracking.py"])
            return result.returncode == 0
        except Exception as e:
            print(f"✗ Erreur lors du lancement: {e}")
            return False
    else:
        print("Test annulé")
        return False

def test_arduino_communication():
    """Teste la communication avec l'Arduino"""
    print("\n" + "="*70)
    print("TEST DE COMMUNICATION ARDUINO")
    print("="*70)
    
    try:
        import serial
        print(f"\nTentative de connexion à {config.ARDUINO_PORT}...")
        arduino = serial.Serial(
            port=config.ARDUINO_PORT,
            baudrate=config.ARDUINO_BAUDRATE,
            timeout=config.ARDUINO_TIMEOUT
        )
        print("✓ Connexion établie")
        time.sleep(2)
        
        # Test de communication
        print("\nEnvoi de la commande de connexion...")
        arduino.write(b'A20')
        time.sleep(0.1)
        
        rep = arduino.readline()
        if rep:
            print(f"✓ Réponse reçue: {rep.decode().strip()}")
            
            # Test d'une commande moteur
            print("\nTest d'une commande moteur (vitesse 0)...")
            arduino.write(b'M L0 R0\n')
            time.sleep(0.1)
            rep = arduino.readline()
            if rep:
                print(f"✓ Réponse: {rep.decode().strip()}")
            
            print("\n✓ Test de communication réussi!")
        else:
            print("✗ Aucune réponse de l'Arduino")
        
        # Déconnexion
        arduino.write(b'a')
        arduino.close()
        print("✓ Déconnexion réussie")
        return True
        
    except serial.SerialException as e:
        print(f"✗ Erreur de connexion: {e}")
        print("\nVérifiez:")
        print(f"  - L'Arduino est connecté au port {config.ARDUINO_PORT}")
        print("  - L'Arduino est programmé avec serial_link.ino")
        print("  - Vous avez les permissions d'accès au port série")
        return False
    except Exception as e:
        print(f"✗ Erreur inattendue: {e}")
        return False

def launch_autonomous_mode():
    """Lance le mode autonome complet"""
    print("\n" + "="*70)
    print("LANCEMENT DU MODE AUTONOME")
    print("="*70)
    print("\nCe mode lance le suivi de ligne complet avec Arduino.")
    print("Le robot suivra automatiquement la ligne blanche.\n")
    
    show_current_config()
    
    print("\n" + "-"*70)
    confirm = input("Lancer le mode autonome ? (o/N): ").strip().lower()
    
    if confirm == 'o':
        duration = input("Durée du suivi (en secondes, 0 pour infini) [30]: ").strip()
        try:
            duration = int(duration) if duration else 30
        except:
            duration = 30
        
        print(f"\nLancement pour {duration}s (Ctrl+C pour arrêter)...")
        print("="*70)
        
        try:
            # Import et lancement du script principal
            import dialogue
            # Cette partie nécessiterait d'adapter dialogue.py
            print("Note: Lancez dialogue.py directement pour le mode autonome complet")
            return True
        except Exception as e:
            print(f"✗ Erreur: {e}")
            return False
    else:
        print("Lancé annulé")
        return False

def simulate_steering_commands():
    """Simule le calcul des commandes de direction"""
    print("\n" + "="*70)
    print("SIMULATION DU CALCUL DES COMMANDES")
    print("="*70)
    
    image_width = config.CAMERA_RESOLUTION[0]
    center_x = image_width / 2
    
    print(f"\nLargeur d'image: {image_width} pixels")
    print(f"Centre: {center_x} pixels")
    print(f"Zone morte: ±{config.DEAD_ZONE} pixels")
    print(f"Vitesse de base: {config.BASE_SPEED}")
    print("\n" + "-"*70)
    
    # Différentes positions du centroïde
    test_positions = [
        (center_x, "Centre"),
        (center_x - 5, "Légèrement à gauche"),
        (center_x + 5, "Légèrement à droite"),
        (center_x - 20, "À gauche"),
        (center_x + 20, "À droite"),
        (center_x - 40, "Très à gauche"),
        (center_x + 40, "Très à droite"),
        (20, "Extrême gauche"),
        (image_width - 20, "Extrême droite"),
    ]
    
    print(f"{'Position':20} | {'Erreur':>8} | {'Gauche':>7} | {'Droite':>7} | {'Action':15}")
    print("-"*70)
    
    for cx, description in test_positions:
        error = cx - center_x
        
        # Calcul des vitesses
        if abs(error) < config.DEAD_ZONE:
            left_speed = config.BASE_SPEED
            right_speed = config.BASE_SPEED
            action = "Tout droit"
        elif error < 0:
            correction = min(abs(error) / center_x, 1.0)
            left_speed = int(config.BASE_SPEED * (1 - correction * config.CORRECTION_FACTOR))
            left_speed = max(left_speed, config.MIN_SPEED)
            right_speed = config.BASE_SPEED
            action = "Tourne gauche"
        else:
            correction = min(error / center_x, 1.0)
            left_speed = config.BASE_SPEED
            right_speed = int(config.BASE_SPEED * (1 - correction * config.CORRECTION_FACTOR))
            right_speed = max(right_speed, config.MIN_SPEED)
            action = "Tourne droite"
        
        print(f"{description:20} | {error:>8.1f} | {left_speed:>7} | {right_speed:>7} | {action:15}")
    
    print("="*70)

def visualize_system():
    """Lance la visualisation du système"""
    print("\n" + "="*70)
    print("VISUALISATION DU SYSTÈME")
    print("="*70)
    print("\nGénération d'un diagramme expliquant le système...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, "visualize_system.py"])
        return result.returncode == 0
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False

def main():
    """Fonction principale"""
    print_banner()
    
    while True:
        print_menu()
        choice = input("\nVotre choix: ").strip().upper()
        
        if choice == '1':
            show_current_config()
        elif choice == '2':
            load_profile_interactive()
        elif choice == '3':
            test_line_detection()
        elif choice == '4':
            test_arduino_communication()
        elif choice == '5':
            launch_autonomous_mode()
        elif choice == '6':
            simulate_steering_commands()
        elif choice == '7':
            visualize_system()
        elif choice == 'Q':
            print("\n👋 Au revoir!")
            break
        else:
            print("❌ Choix invalide!")
        
        input("\nAppuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interruption par l'utilisateur. Au revoir!")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
