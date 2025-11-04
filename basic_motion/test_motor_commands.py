#!/usr/bin/env python3
"""
Script de test pour vérifier l'envoi des commandes moteur
Compatible avec le protocole binaire de serial_link.ino
"""

import serial
import time
import struct


def write_i16(f, value):
    """Écrit un entier 16 bits (int16) au format little-endian"""
    f.write(struct.pack('<h', value))


def write_i32(f, value):
    """Écrit un entier 32 bits (int32) au format little-endian"""
    f.write(struct.pack('<l', value))


def send_motor_command(arduino, left_speed, right_speed):
    """
    Envoie une commande aux moteurs
    Protocole: 'C' + vitesse_gauche (int16) + vitesse_droite (int16) + dummy (int32)
    """
    print(f"Envoi commande: Gauche={left_speed}, Droite={right_speed}")
    
    arduino.write(b'C')
    write_i16(arduino, int(left_speed))
    write_i16(arduino, int(right_speed))
    write_i32(arduino, 0)  # Paramètre dummy (int32)
    
    # Attente de l'acquittement
    rep = b''
    while rep == b'':
        rep = arduino.readline()
    
    if rep:
        print(f"  → Arduino: {rep.decode().strip()}")
    
    return True


def stop_motors(arduino):
    """Arrête les moteurs"""
    print("Arrêt des moteurs")
    return send_motor_command(arduino, 0, 0)


def test_sequence(arduino):
    """Exécute une séquence de test des moteurs"""
    print("\n" + "="*60)
    print("SÉQUENCE DE TEST DES MOTEURS")
    print("="*60)
    
    tests = [
        (0, 0, "Arrêt initial", 1),
        (100, 100, "Avance tout droit", 2),
        (0, 0, "Arrêt", 1),
        (50, 100, "Tourne à gauche (correction)", 2),
        (0, 0, "Arrêt", 1),
        (100, 50, "Tourne à droite (correction)", 2),
        (0, 0, "Arrêt", 1),
        (80, 80, "Avance lentement", 2),
        (0, 0, "Arrêt final", 1),
    ]
    
    for left, right, description, duration in tests:
        print(f"\n[TEST] {description}")
        send_motor_command(arduino, left, right)
        print(f"  Attente {duration}s...")
        time.sleep(duration)
    
    print("\n" + "="*60)
    print("✓ Séquence de test terminée")
    print("="*60)


def manual_control(arduino):
    """Contrôle manuel des moteurs"""
    print("\n" + "="*60)
    print("CONTRÔLE MANUEL DES MOTEURS")
    print("="*60)
    print("Commandes disponibles:")
    print("  z - Avancer")
    print("  s - Reculer")
    print("  q - Tourner à gauche")
    print("  d - Tourner à droite")
    print("  a - Arrêter")
    print("  x - Quitter")
    print("="*60 + "\n")
    
    speed = 100
    
    try:
        while True:
            cmd = input("Commande (z/s/q/d/a/x): ").strip().lower()
            
            if cmd == 'z':
                print("→ Avancer")
                send_motor_command(arduino, speed, speed)
            elif cmd == 's':
                print("→ Reculer")
                send_motor_command(arduino, -speed, -speed)
            elif cmd == 'q':
                print("→ Tourner à gauche")
                send_motor_command(arduino, speed//2, speed)
            elif cmd == 'd':
                print("→ Tourner à droite")
                send_motor_command(arduino, speed, speed//2)
            elif cmd == 'a':
                print("→ Arrêter")
                stop_motors(arduino)
            elif cmd == 'x':
                print("→ Quitter")
                stop_motors(arduino)
                break
            else:
                print("✗ Commande invalide")
    
    except KeyboardInterrupt:
        print("\n\nInterruption détectée")
        stop_motors(arduino)


def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print("TEST DES COMMANDES MOTEUR")
    print("Protocole binaire - serial_link.ino")
    print("="*60)
    
    # Configuration du port série
    port = '/dev/ttyACM0'
    baudrate = 115200
    
    print(f"\nConnexion à {port} ({baudrate} bauds)...")
    
    try:
        arduino = serial.Serial(port=port, baudrate=baudrate, timeout=0.1)
        print("✓ Connexion établie")
        time.sleep(2)  # Attente initialisation Arduino
        
        # Connexion au protocole
        print("\nInitialisation du protocole...")
        arduino.write(b'A20')
        time.sleep(0.1)
        rep = arduino.readline()
        
        if rep and b'OK' in rep:
            print(f"✓ {rep.decode().strip()}")
            
            # Menu
            while True:
                print("\n" + "-"*60)
                print("MENU")
                print("-"*60)
                print("1. Test simple (une commande)")
                print("2. Séquence de test automatique")
                print("3. Contrôle manuel")
                print("Q. Quitter")
                print("-"*60)
                
                choice = input("Votre choix: ").strip().upper()
                
                if choice == '1':
                    left = int(input("Vitesse gauche (-255 à 255): "))
                    right = int(input("Vitesse droite (-255 à 255): "))
                    duration = float(input("Durée (secondes): "))
                    
                    send_motor_command(arduino, left, right)
                    print(f"Attente {duration}s...")
                    time.sleep(duration)
                    stop_motors(arduino)
                    
                elif choice == '2':
                    confirm = input("Lancer la séquence de test ? (o/N): ").strip().lower()
                    if confirm == 'o':
                        test_sequence(arduino)
                    
                elif choice == '3':
                    manual_control(arduino)
                    
                elif choice == 'Q':
                    break
                else:
                    print("✗ Choix invalide")
            
            # Déconnexion
            print("\nDéconnexion...")
            stop_motors(arduino)
            arduino.write(b'a')
            arduino.close()
            print("✓ Déconnexion réussie")
            
        else:
            print(f"✗ Pas de réponse OK de l'Arduino")
            print(f"  Reçu: {rep}")
            arduino.close()
            
    except serial.SerialException as e:
        print(f"✗ Erreur de connexion: {e}")
        print("\nVérifiez:")
        print(f"  - L'Arduino est connecté sur {port}")
        print("  - L'Arduino est programmé avec serial_link.ino")
        print("  - Vous avez les permissions d'accès")
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Programme interrompu par l'utilisateur")
    
    print("\nFin du programme")
