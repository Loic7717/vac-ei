# 🚗 Guide de Démarrage Rapide - Suivi de Ligne

## Installation

### 1. Prérequis matériels
- Raspberry Pi avec caméra PiCamera
- Arduino programmé avec `serial_link.ino`
- Robot avec 2 moteurs DC
- Ligne blanche sur fond sombre

### 2. Installation des dépendances

```bash
# Sur Raspberry Pi
sudo apt-get update
sudo apt-get install python3-pip python3-picamera

# Packages Python
pip3 install numpy opencv-python pyserial
pip3 install "picamera[array]"

# Pour la visualisation (optionnel)
pip3 install matplotlib
```

### 3. Activation de la caméra

```bash
sudo raspi-config
# Interface Options → Camera → Enable
sudo reboot
```

## 🚀 Démarrage Rapide

### Test 1: Vision seule (RECOMMANDÉ pour commencer)

```bash
cd basic_motion
python3 test_line_tracking.py
```

✅ **Ce test permet de:**
- Vérifier que la caméra fonctionne
- Voir si la ligne est bien détectée
- Visualiser les commandes calculées
- Pas besoin de l'Arduino

Appuyez sur **'q'** pour quitter.

### Test 2: Communication Arduino

```bash
python3 demo.py
# Choisir option 4
```

✅ **Ce test vérifie:**
- La connexion série avec l'Arduino
- L'envoi et réception de commandes
- Le protocole de communication

### Test 3: Mode Autonome Complet

```bash
python3 dialogue.py
# Choisir option 2 (Mode suivi de ligne autonome)
```

✅ **Le robot va:**
- Détecter la ligne
- Calculer les corrections
- Envoyer les commandes aux moteurs
- Suivre automatiquement la ligne

Appuyez sur **Ctrl+C** pour arrêter.

## 🎛️ Configuration

### Utilisation des profils

```bash
python3 demo.py
# Option 2: Charger un profil
```

**Profils disponibles:**

| Profil | Vitesse | Virages | Usage |
|--------|---------|---------|-------|
| `default` | Moyenne | Normaux | Utilisation générale |
| `smooth` | Lente | Doux | **Recommandé pour débuter** |
| `aggressive` | Rapide | Serrés | Circuit avec virages |
| `fast` | Très rapide | Normaux | Circuit simple |
| `precise` | Lente | Précis | Test et calibration |

### Configuration manuelle

Éditez `config.py`:

```python
# Vitesse de base (0-255)
BASE_SPEED = 100

# Zone morte (pixels)
DEAD_ZONE = 10

# Facteur de correction (0.0-1.0)
CORRECTION_FACTOR = 0.5
```

## 🔧 Dépannage

### ❌ "PiCamera non disponible"

**Solution:**
```bash
# Vérifier que la caméra est activée
vcgencmd get_camera
# Devrait afficher: supported=1 detected=1

# Si non détectée, vérifier le câble et redémarrer
```

### ❌ "Erreur de connexion Arduino"

**Solutions:**
1. Vérifier le port série:
   ```bash
   ls /dev/tty*
   # Chercher ttyACM0 ou ttyUSB0
   ```

2. Modifier dans `config.py`:
   ```python
   ARDUINO_PORT = '/dev/ttyUSB0'  # Ou autre port
   ```

3. Permissions:
   ```bash
   sudo usermod -a -G dialout $USER
   # Puis déconnexion/reconnexion
   ```

### ❌ "Aucune ligne détectée"

**Solutions:**
1. Vérifier l'éclairage (ligne bien éclairée)
2. Tester avec `test_line_tracking.py` pour voir l'image
3. Ajuster le seuil dans `config.py`:
   ```python
   THRESHOLD_VALUE = 150  # Réduire si ligne grise
   ```

### ❌ "Le robot oscille trop"

**Solutions:**
1. Utiliser le profil `smooth`:
   ```bash
   python3 demo.py
   # Option 2 → Profil 3 (smooth)
   ```

2. Ou modifier manuellement:
   ```python
   DEAD_ZONE = 15          # Augmenter
   CORRECTION_FACTOR = 0.3  # Réduire
   ```

### ❌ "Le robot perd la ligne dans les virages"

**Solutions:**
1. Utiliser le profil `aggressive`
2. Ou augmenter:
   ```python
   CORRECTION_FACTOR = 0.7  # Plus de correction
   MIN_SPEED = 40           # Virages plus serrés
   ```

## 📊 Commandes du Script de Démo

```bash
python3 demo.py
```

**Options disponibles:**

1. **Afficher la configuration** - Voir tous les paramètres actuels
2. **Charger un profil** - Changer rapidement de comportement
3. **Tester la détection** - Vision seule, sans Arduino
4. **Tester Arduino** - Communication série
5. **Mode autonome** - Lancer le robot complet
6. **Simuler commandes** - Voir le calcul des vitesses
7. **Visualiser système** - Générer un diagramme

## 📝 Processus Recommandé

### Pour débutants:

```
1. Test vision (test_line_tracking.py)
   ↓ Vérifier que la ligne est détectée
2. Test Arduino (demo.py → option 4)
   ↓ Vérifier la communication
3. Profil smooth (demo.py → option 2 → profil 3)
   ↓ Configuration douce
4. Mode autonome (dialogue.py → option 2)
   ↓ Lancer avec durée courte (10s)
5. Ajuster progressivement
```

### Pour experts:

```
1. Simuler commandes (demo.py → option 6)
   ↓ Comprendre la logique
2. Créer profil personnalisé dans config.py
   ↓ Optimiser pour votre circuit
3. Tester et itérer
```

## 🎯 Exemple de Session Complète

```bash
# 1. Tester la vision
python3 test_line_tracking.py
# Vérifier: La ligne apparaît avec un point rouge au centre?
# Si OUI → continuer, si NON → ajuster THRESHOLD_VALUE

# 2. Tester Arduino
python3 demo.py
# Choisir: 4 (Test Arduino)
# Vérifier: "✓ Test de communication réussi!"

# 3. Charger profil smooth
python3 demo.py
# Choisir: 2 (Charger profil) → 3 (smooth)

# 4. Lancer mode autonome
python3 dialogue.py
# Choisir: 2 (Mode autonome)
# Durée: 30 (secondes)
# Placer le robot sur la ligne
# Observer le comportement

# 5. Ajuster si nécessaire
# Éditer config.py selon le comportement observé
```

## 📖 Documentation Complète

- **README_LINE_TRACKING.md** - Documentation détaillée
- **config.py** - Tous les paramètres avec explications
- **demo.py** - Interface de test interactive

## 🆘 Support

Si vous rencontrez des problèmes:

1. Consultez la section Dépannage ci-dessus
2. Lisez le guide d'ajustement dans `config.py`
3. Utilisez `demo.py` pour tester chaque composant séparément
4. Vérifiez les logs pour des messages d'erreur détaillés

## 💡 Conseils

- **Commencez toujours** par tester la vision seule
- **Utilisez le profil smooth** pour les premiers tests
- **Testez sur un circuit simple** avant les virages complexes
- **Ajustez un paramètre à la fois** pour comprendre son effet
- **Bon éclairage** = détection plus stable

Bon suivi de ligne! 🏁
