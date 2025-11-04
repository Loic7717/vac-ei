#########################################################################
# CENTRALESUPELEC : ST5 VAC Integration teaching
#
# This script works with the Arduino programmed wih serial_link.ino
# Integrated with line detection and autonomous correction
#
#########################################################################

import serial 
import time
import numpy as np
import cv2
import struct
import sys
import os

# Import de la caméra
try:
    from picamera import PiCamera
    from picamera.array import PiRGBArray
    PICAMERA_AVAILABLE = True
except ImportError:
    print("PiCamera non disponible, mode simulation")
    PICAMERA_AVAILABLE = False



def read_i16(f):
    return struct.unpack('<h', bytearray(f.read(2)))[0]


def read_i32(f):
    return struct.unpack('<l', bytearray(f.read(4)))[0]


def write_i16(f, value):
    f.write(struct.pack('<h', value))


def write_i32(f, value):
    f.write(struct.pack('<l', value))

############################################
# Fonctions de vision et traitement d'image
############################################

# Configuration de la caméra
resolution_target = (160, 128)

def init_camera():
    """Initialise la caméra PiCamera"""
    if not PICAMERA_AVAILABLE:
        return None, None, None
    
    camera = PiCamera(sensor_mode=2)
    camera.resolution = resolution_target
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, size=camera.resolution)
    frame_source = camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)
    
    return camera, rawCapture, frame_source

def capture_image(frame_source, rawCapture):
    """Capture une image depuis la caméra"""
    if frame_source is None:
        return None
    
    image = next(frame_source).array
    rawCapture.truncate(0)
    return image

def detect_line(image, feedback=False):
    """
    Détecte la ligne blanche dans l'image et retourne les coordonnées du centroïde
    Returns: (cx, cy) ou (None, None) si aucune ligne détectée
    """
    if image is None:
        return None, None
    
    h, w = image.shape[:2]
    
    # Prétraitement: flou pour réduire le bruit
    blur = cv2.blur(image, (5, 5))
    
    # Seuillage pour isoler les zones blanches
    ret, thresh1 = cv2.threshold(blur, 168, 255, cv2.THRESH_BINARY)
    
    # Conversion en HSV
    hsv = cv2.cvtColor(thresh1, cv2.COLOR_RGB2HSV)
    
    # Définition de la plage de blanc en HSV
    lower_white = np.array([0, 0, 168])
    upper_white = np.array([172, 111, 255])
    
    # Création du masque
    mask = cv2.inRange(hsv, lower_white, upper_white)
    
    # Suppression du bruit avec morphologie
    kernel_erode = np.ones((6, 6), np.uint8)
    eroded_mask = cv2.erode(mask, kernel_erode, iterations=1)
    kernel_dilate = np.ones((4, 4), np.uint8)
    dilated_mask = cv2.dilate(eroded_mask, kernel_dilate, iterations=1)
    
    # Détection des contours
    contours, hierarchy = cv2.findContours(dilated_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if feedback:
        im_debug = cv2.drawContours(image.copy(), contours, -1, (0, 255, 0), 2)
        cv2.imshow("Contours détectés", im_debug)
        cv2.waitKey(1)
    
    # Tri par aire (garder seulement le plus grand)
    if len(contours) > 0:
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]
        M = cv2.moments(contours[0])
        
        if M['m00'] != 0:
            # Calcul du centroïde
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            
            if feedback:
                print(f"Centroïde détecté à: ({cx}, {cy})")
            
            return cx, cy
    
    if feedback:
        print("Aucune ligne détectée")
    
    return None, None

def compute_steering_command(cx, cy, image_width):
    """
    Calcule la commande de direction basée sur la position du centroïde
    Returns: (left_speed, right_speed) - vitesses relatives entre -255 et 255
    """
    if cx is None:
        # Aucune ligne détectée, arrêt
        return 0, 0
    
    # Centre de l'image
    center_x = image_width / 2
    
    # Erreur de position (négatif = ligne à gauche, positif = ligne à droite)
    error = cx - center_x
    
    # Zone morte pour éviter les oscillations
    dead_zone = 10
    
    if abs(error) < dead_zone:
        # Ligne centrée, avancer tout droit
        left_speed = 100
        right_speed = 100
        print("✓ Ligne centrée - Avance tout droit")
    elif error < 0:
        # Ligne à gauche, tourner à gauche
        correction = min(abs(error) / center_x, 1.0)  # Normaliser entre 0 et 1
        left_speed = int(100 * (1 - correction * 0.5))
        right_speed = 100
        print(f"← Ligne à gauche (erreur: {error:.1f}) - Tourne à gauche")
    else:
        # Ligne à droite, tourner à droite
        correction = min(error / center_x, 1.0)
        left_speed = 100
        right_speed = int(100 * (1 - correction * 0.5))
        print(f"→ Ligne à droite (erreur: {error:.1f}) - Tourne à droite")
    
    return left_speed, right_speed

def send_motor_command(arduino, left_speed, right_speed):
    """
    Envoie une commande aux moteurs
    Vitesses entre -255 et 255
    Utilise le protocole binaire: commande 'C' + 2 int16 + 1 int32
    """
    # Protocole binaire conforme à DUALMOTOR_code() dans serial_link.ino:
    # 'C' + vitesse_gauche (int16) + vitesse_droite (int16) + dummy (int32)
    arduino.write(b'C')
    write_i16(arduino, int(left_speed))   # Moteur gauche
    write_i16(arduino, int(right_speed))  # Moteur droit
    write_i32(arduino, 0)                 # Paramètre dummy (non utilisé)
    
    # Attente de l'acquittement
    rep = b''
    while rep == b'':
        rep = arduino.readline()
    
    if rep:
        print(f"Arduino: {rep.decode().strip()}")

############################################
# Fonction de suivi de ligne autonome
############################################

def autonomous_line_following(arduino, duration=60, feedback=True):
    """
    Mode de suivi de ligne autonome
    duration: durée en secondes (0 = infini)
    feedback: afficher les informations de débogage
    """
    print("\n" + "="*50)
    print("DÉMARRAGE DU MODE SUIVI DE LIGNE AUTONOME")
    print("="*50)
    print("Appuyez sur Ctrl+C pour arrêter")
    print()
    
    # Initialisation de la caméra
    camera, rawCapture, frame_source = init_camera()
    
    if camera is None:
        print("Erreur: Impossible d'initialiser la caméra")
        return
    
    print("✓ Caméra initialisée")
    time.sleep(1)
    
    start_time = time.time()
    frame_count = 0
    
    try:
        while True:
            # Vérifier la durée
            if duration > 0 and (time.time() - start_time) > duration:
                print(f"\nDurée écoulée ({duration}s)")
                break
            
            # Capture d'image
            image = capture_image(frame_source, rawCapture)
            
            if image is None:
                print("Erreur de capture d'image")
                time.sleep(0.1)
                continue
            
            frame_count += 1
            
            # Détection de la ligne
            cx, cy = detect_line(image, feedback=feedback)
            
            # Calcul de la commande de direction
            left_speed, right_speed = compute_steering_command(cx, cy, image.shape[1])
            
            # Envoi de la commande aux moteurs
            send_motor_command(arduino, left_speed, right_speed)
            
            # Affichage des statistiques
            if frame_count % 10 == 0:
                fps = frame_count / (time.time() - start_time)
                print(f"[Stats] Frames: {frame_count} | FPS: {fps:.1f}")
            
            time.sleep(0.05)  # 20 Hz
            
    except KeyboardInterrupt:
        print("\n\nArrêt demandé par l'utilisateur")
    finally:
        # Arrêt des moteurs
        print("Arrêt des moteurs...")
        send_motor_command(arduino, 0, 0)
        
        # Fermeture de la caméra
        if camera is not None:
            camera.close()
        
        print("✓ Caméra fermée")
        print("="*50)

############################################
# Fonction de dialogue direct avec l'arduino
#############################################

def DialArduino():
    while True:
        print("") 
        print("Dialogue direct avec l'arduino") 
        cma = input("Tapez votre commande arduino (Q pour finir) ")
        if cma=="Q":
            break
        if cma!='':
            arduino.write(cma.encode('utf-8'))
            time.sleep(0.01)
            rep = arduino.readline()  		# on lit le message de réponse
            while rep==b'':					# On attend d'avoir une vraie réponse
                rep = arduino.readline()  	# on lit le message de réponse   
            #print(rep)
            print(rep.decode())
            while arduino.inWaiting()>0 :	# tant qu'on a des messages dans le buffer de retour
                rep = arduino.readline()  	# on lit le message de réponse   
                print(rep.decode())

def AttAcquit():
    rep=b''
    while rep==b'':					# attend l'acquitement du B2
        rep=arduino.readline()
    #print(rep.decode())

############################################
# Programme principal
############################################








############################################################
# initialisation de la liaison série connection à l'arduino

arduino = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=0.1)
print ("Connection à l'arduino")
time.sleep(2)			# on attend 2s pour que la carte soit initialisée

arduino.write(b'A20')		# demande de connection avec acquitement complet en ascii
rep = arduino.readline()
if len(rep.split())>0:
  if rep.split()[0]==b'OK':
    print(rep.decode())
    
    # Menu principal
    while True:
        print("\n" + "="*50)
        print("MENU PRINCIPAL")
        print("="*50)
        print("1. Dialogue direct avec Arduino")
        print("2. Mode suivi de ligne autonome")
        print("Q. Quitter")
        print("="*50)
        
        choix = input("Votre choix: ").strip().upper()
        
        if choix == "1":
            DialArduino()
        elif choix == "2":
            duree = input("Durée du suivi (en secondes, 0 pour infini): ").strip()
            try:
                duree = int(duree)
            except:
                duree = 60
            autonomous_line_following(arduino, duration=duree, feedback=True)
        elif choix == "Q":
            break
        else:
            print("Choix invalide!")

    
#######################################
#   deconnection de l'arduino

arduino.write(b'a')	# deconnection de la carte
arduino.close()         # fermeture de la liaison série
print ("Fin de programme")

