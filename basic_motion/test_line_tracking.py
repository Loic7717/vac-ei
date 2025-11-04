#!/usr/bin/env python3
"""
Script de test pour le suivi de ligne sans Arduino
Permet de tester la détection de ligne et le calcul des commandes
"""

import cv2
import numpy as np
import time

try:
    from picamera import PiCamera
    from picamera.array import PiRGBArray
    PICAMERA_AVAILABLE = True
except ImportError:
    print("PiCamera non disponible, mode simulation avec webcam")
    PICAMERA_AVAILABLE = False

resolution_target = (160, 128)

def init_camera():
    """Initialise la caméra (PiCamera ou webcam)"""
    if PICAMERA_AVAILABLE:
        camera = PiCamera(sensor_mode=2)
        camera.resolution = resolution_target
        camera.framerate = 32
        rawCapture = PiRGBArray(camera, size=camera.resolution)
        frame_source = camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)
        return camera, rawCapture, frame_source, True
    else:
        # Utiliser la webcam comme fallback
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution_target[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution_target[1])
        return cap, None, None, False

def capture_image(camera, rawCapture, frame_source, is_picamera):
    """Capture une image depuis la caméra"""
    if is_picamera:
        image = next(frame_source).array
        rawCapture.truncate(0)
        return image
    else:
        ret, image = camera.read()
        if ret:
            # Redimensionner si nécessaire
            image = cv2.resize(image, resolution_target)
            return image
        return None

def detect_line(image):
    """
    Détecte la ligne blanche dans l'image et retourne les coordonnées du centroïde
    Returns: (cx, cy, debug_image) ou (None, None, debug_image)
    """
    if image is None:
        return None, None, image
    
    h, w = image.shape[:2]
    debug_image = image.copy()
    
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
    
    # Dessiner les contours sur l'image de debug
    cv2.drawContours(debug_image, contours, -1, (0, 255, 0), 2)
    
    # Tri par aire (garder seulement le plus grand)
    if len(contours) > 0:
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]
        M = cv2.moments(contours[0])
        
        if M['m00'] != 0:
            # Calcul du centroïde
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            
            # Dessiner le centroïde
            cv2.circle(debug_image, (cx, cy), 5, (255, 0, 0), -1)
            cv2.putText(debug_image, f"({cx},{cy})", (cx+10, cy-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
            
            return cx, cy, debug_image
    
    return None, None, debug_image

def compute_steering_command(cx, cy, image_width):
    """
    Calcule la commande de direction basée sur la position du centroïde
    Returns: (left_speed, right_speed, info_text)
    """
    if cx is None:
        return 0, 0, "Aucune ligne détectée - ARRÊT"
    
    # Centre de l'image
    center_x = image_width / 2
    
    # Erreur de position (négatif = ligne à gauche, positif = ligne à droite)
    error = cx - center_x
    
    # Zone morte pour éviter les oscillations
    dead_zone = 10
    
    if abs(error) < dead_zone:
        left_speed = 100
        right_speed = 100
        info = f"Ligne centrée | L:{left_speed} R:{right_speed}"
    elif error < 0:
        correction = min(abs(error) / center_x, 1.0)
        left_speed = int(100 * (1 - correction * 0.5))
        right_speed = 100
        info = f"Tourne GAUCHE (err:{error:.1f}) | L:{left_speed} R:{right_speed}"
    else:
        correction = min(error / center_x, 1.0)
        left_speed = 100
        right_speed = int(100 * (1 - correction * 0.5))
        info = f"Tourne DROITE (err:{error:.1f}) | L:{left_speed} R:{right_speed}"
    
    return left_speed, right_speed, info

def main():
    """Fonction principale de test"""
    print("\n" + "="*60)
    print("TEST DE SUIVI DE LIGNE (sans Arduino)")
    print("="*60)
    print("Ce script teste la détection de ligne et le calcul des commandes")
    print("Appuyez sur 'q' pour quitter")
    print("="*60 + "\n")
    
    # Initialisation de la caméra
    camera, rawCapture, frame_source, is_picamera = init_camera()
    
    if camera is None:
        print("Erreur: Impossible d'initialiser la caméra")
        return
    
    print("✓ Caméra initialisée")
    time.sleep(1)
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            # Capture d'image
            image = capture_image(camera, rawCapture, frame_source, is_picamera)
            
            if image is None:
                print("Erreur de capture d'image")
                time.sleep(0.1)
                continue
            
            frame_count += 1
            
            # Détection de la ligne
            cx, cy, debug_image = detect_line(image)
            
            # Calcul de la commande de direction
            left_speed, right_speed, info_text = compute_steering_command(cx, cy, image.shape[1])
            
            # Affichage des informations sur l'image
            h, w = debug_image.shape[:2]
            
            # Ligne centrale de référence
            cv2.line(debug_image, (w//2, 0), (w//2, h), (0, 0, 255), 1)
            
            # Zone morte
            dead_zone = 10
            cv2.line(debug_image, (w//2 - dead_zone, 0), (w//2 - dead_zone, h), (128, 128, 128), 1)
            cv2.line(debug_image, (w//2 + dead_zone, 0), (w//2 + dead_zone, h), (128, 128, 128), 1)
            
            # Affichage du texte
            cv2.putText(debug_image, info_text, (5, 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
            
            # FPS
            fps = frame_count / (time.time() - start_time)
            cv2.putText(debug_image, f"FPS: {fps:.1f}", (5, h-5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
            
            # Affichage
            cv2.imshow("Test de suivi de ligne", debug_image)
            
            # Console
            if frame_count % 10 == 0:
                print(f"[Frame {frame_count}] {info_text} | FPS: {fps:.1f}")
            
            # Gestion des touches
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\nArrêt demandé par l'utilisateur")
                break
            
    except KeyboardInterrupt:
        print("\n\nArrêt demandé par l'utilisateur")
    finally:
        # Fermeture
        if is_picamera:
            camera.close()
        else:
            camera.release()
        cv2.destroyAllWindows()
        
        print("✓ Caméra fermée")
        print("="*60)

if __name__ == "__main__":
    main()
