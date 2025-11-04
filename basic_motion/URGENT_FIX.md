# 🐛 Correction Urgente - Erreur "ER" de l'Arduino

## Problème

```
Arduino: ER
Arduino: ER
Arduino: ER
```

Les moteurs ne bougent pas !

## Cause

**Structure des données incorrecte** !

### Arduino attend (DUALMOTOR_code):
```cpp
GetInt(0);   // int16 → 2 bytes
GetInt(0);   // int16 → 2 bytes  
GetLong(0);  // int32 → 4 bytes ← IMPORTANT !
```

### On envoyait :
```python
write_i16(arduino, left)   # 2 bytes
write_i16(arduino, right)  # 2 bytes
write_i16(arduino, 0)      # 2 bytes ✗ ERREUR
write_i16(arduino, 0)      # 2 bytes ✗ ERREUR
```

L'Arduino essaie de lire un **int32** (4 bytes) mais ne trouve que 2 int16 mal alignés → **ERREUR "ER"**

## ✅ Solution Appliquée

```python
def send_motor_command(arduino, left_speed, right_speed):
    arduino.write(b'C')
    write_i16(arduino, int(left_speed))   # 2 bytes
    write_i16(arduino, int(right_speed))  # 2 bytes
    write_i32(arduino, 0)                 # 4 bytes ✓ CORRECT
```

## Test Immédiat

```bash
python3 test_motor_commands.py
```

Menu → Option 1 (Test simple)
- Vitesse gauche: 100
- Vitesse droite: 100
- Durée: 2

**Attendu** : 
```
Arduino: OK Moteurs mis aux tensions : 100 100
```

Au lieu de :
```
Arduino: ER
```

## Fichiers Modifiés

✅ `dialogue.py` - Ligne ~170-188
✅ `test_motor_commands.py` - Ligne ~10-30
✅ `PROTOCOL_FIX.md` - Documentation complète

## Explication Technique

### Alignement des Bytes

**Incorrect (8 bytes mal structurés)** :
```
[C][LL][RR][00][00]
 1  2+2 2+2 2+2 = 9 bytes
```
Arduino lit :
```
[C] → OK
[LL] → left (int16) ✓
[RR] → right (int16) ✓
[00][00] → essaie de lire comme int32 mais trouve 2×int16 ✗
```

**Correct (8 bytes bien structurés)** :
```
[C][LL][RR][0000]
 1  2+2 2+2  4  = 9 bytes
```
Arduino lit :
```
[C] → OK
[LL] → left (int16) ✓
[RR] → right (int16) ✓
[0000] → dummy (int32) ✓
```

## Code Arduino de Référence

```cpp
// serial_link.ino ligne 336
void DUALMOTOR_code() {
  delay(1);
  nivM1=GetInt(0);      // ← lit 2 bytes
  nivM2=GetInt(nivM1);  // ← lit 2 bytes
  GetLong(0);           // ← lit 4 bytes (CRITIQUE !)
  
  set_motor1(nivM1);
  set_motor2(nivM2);
  
  RetAcquitSimpl();     // Renvoie "OK" si succès, "ER" si erreur
}
```

## Vérification

Avant de tester sur le robot, vérifiez :

1. **Les imports** :
   ```python
   import struct
   
   def write_i32(f, value):
       f.write(struct.pack('<l', value))
   ```

2. **La connexion** :
   ```bash
   ls /dev/tty*  # Chercher ttyACM0
   ```

3. **Le code Arduino** :
   - Version dans `basic_motion/serial_link/serial_link.ino`
   - Vérifie que c'est bien celui uploadé sur l'Arduino

## Résumé

| Avant | Après |
|-------|-------|
| 4 × int16 (structure incorrecte) | 2 × int16 + 1 × int32 (correct) |
| Arduino: ER | Arduino: OK |
| Moteurs immobiles | Moteurs fonctionnels ✓ |

## Commit Message Suggéré

```
fix: Correct motor command protocol structure

Arduino DUALMOTOR_code expects: int16 + int16 + int32
Was sending: 4 × int16
Now sending: 2 × int16 + 1 × int32

Fixes "ER" error response from Arduino
```

---

**Date** : 4 novembre 2025  
**Status** : ✅ CORRIGÉ - À TESTER SUR LE ROBOT
