Robot Project Roadmap
=====================

You have a complete starter kit for a Raspberry Pi + Arduino robot that must follow a painted line, cross intersections, and avoid obstacles. This document mirrors the guidance previously shared, rewritten so you can revisit each phase while working hands-on. Read through the entire roadmap once, then return to the relevant sections as you progress.

Repository Overview
-------------------

* `1_contexte`: official documentation and datasheets. Keep the “Doc robot” PDFs plus hardware datasheets (batteries, IR sensor, URM37, schematic) close.
* `2_livrables`: planning aids (`strat-syst.md`, `taches_detaillees.md`, `diagram.mmd`). Update these continuously.
* `basic_motion`: link between Raspberry Pi and Arduino (`dialogue.py`, `constants.py`, `serial_link/serial_link.ino`).
* `basic_image_processing`: sample Python code for camera-based line and intersection detection.
* `basic_infrastructure`: ZeroMQ supervision utilities (`server.py`, `robot.py`, `control.py`).
* `test_*`: individual Arduino sketches to validate motors, servos, IR, ultrasonic, and encoder hardware.

Foundations (Day 0)
-------------------

1. Read `1_contexte/documentation/Doc robot - Prise en main.docx` for wiring, pinouts, power, and safety notes.
2. Inventory every component. Cross-reference the datasheets in `1_contexte/datasheets`. Highlight battery charging instructions and motor driver specs.
3. Fully charge both battery packs. Work on a clear surface with wheels lifted until software is trusted.
4. Install required tools on your laptop: Arduino IDE (board profile “Romeo BLE”), Python 3.10+, Git, and Visual Studio Code (optional). Download Raspberry Pi Imager if reflashing is needed.

Phase 1 – Raspberry Pi Bring-Up
-------------------------------

1. Flash the provided Raspberry Pi image or Raspberry Pi OS Lite. Enable SSH and the camera via `raspi-config`.
2. On first boot:
   * Connect keyboard/monitor or Ethernet.
   * Run `sudo apt update && sudo apt upgrade`.
   * Install dependencies:
     ```
     sudo apt install python3-opencv python3-numpy python3-pip python3-zmq python3-serial git
     pip install picamera[array]
     ```
3. Clone this repository into `/home/pi/EI` and configure Git user information.
4. Test the camera (`raspistill` or `python3 basic_image_processing/perception_students.py`).
5. Create `/var/log/vac` and ensure user `pi` can write to it.
6. Configure VNC/SSH so you can work remotely.

Phase 2 – Arduino Familiarisation
---------------------------------

1. Install the Romeo BLE board package in Arduino IDE.
2. Upload `test_motors/test_motors.ino` to verify wheel motion (keep chassis lifted).
3. Upload `test_servos/test_servos.ino` and practice sending target angles (`f90`, `b45`, etc.) via Serial Monitor.
4. Upload `test_infrared/test_infrared.ino` and record the voltage thresholds for “Too close” and “Out of range”.
5. Upload `test_ultrasonic/test_ultrasonic.ino` to confirm URM37 readings and servo sweep.
6. Upload `test_encoders/test_encoders.ino` to verify encoder counts. Note pulses per wheel revolution.

Phase 3 – Understand `serial_link.ino`
--------------------------------------

1. Open `basic_motion/serial_link/serial_link.ino` in the Arduino IDE.
2. Study the command decoder tables (`UpperFn` and `LowerFn`). Recognise key commands:
   * `A` – connect handshake.
   * `C` – set both motors immediately.
   * `D` – ramp both motors gradually.
   * `I` – enable/disable IR safety.
3. Inspect the placeholder tasks (`task2`, `task5`) marked `// A COMPLETER`. These will hold your speed computation and servo sweep logic.
4. Understand how `obst` forces motors to zero. It becomes `true` when IR detects an obstacle.
5. Review the connection startup (`arduino.write(b'A20')` or `arduino.write(b'A22')` in Python scripts).

Phase 4 – Practice Pi ↔ Arduino Communication
---------------------------------------------

1. With `serial_link.ino` flashed, run `python3 basic_motion/test_moteurs.py` on your laptop. Observe handshake, motor commands, and acknowledgements.
2. Try `python3 basic_motion/dialogue.py` for manual command entry (`C 150 150`, `I1`, etc.).
3. Adjust the serial port path in scripts if you are on macOS/Windows (e.g., `COM3`).
4. Repeat the same from the Pi. Add `pi` to the `dialout` group if permissions fail (`sudo usermod -a -G dialout pi` and reboot).

Phase 5 – Camera Processing Foundations
---------------------------------------

1. Store sample images (`basic_image_processing/photo_test.jpg`, `photo_carrefour1.jpg`) on the Pi for reproducible tests.
2. Run `python3 basic_image_processing/line_detection.py`. Understand each stage: blur, threshold, morphological operations, contour detection, centroid calculation.
3. Run `python3 basic_image_processing/corner_detection.py` for intersection detection. Note the `expected_corners` parameter and the use of Harris corner detection.
4. Modify `perception_students.py` to insert your processing pipeline. After capturing an image, apply the line detection steps, keep preview windows during debugging, and always call `rawCapture.truncate(0)`.
5. Save diagnostic frames in `/var/log/vac/perception` using `cv2.imwrite` when tuning thresholds.

Phase 6 – Convert Perception to Motor Commands
----------------------------------------------

1. Design a proportional controller: compute lateral error `error = cx - image_center_x`.
2. Create a script (e.g., `basic_motion/follow_line.py`) that:
   * Connects to Arduino (`serial.Serial('/dev/ttyACM0', 115200)`).
   * Calls your perception function.
   * Computes motor commands (`left = base_speed - k * error`, `right = base_speed + k * error`).
   * Sends commands with the `C` or `D` codes (use small base PWM such as 80).
3. Log `(timestamp, error, left, right)` to CSV for tuning.
4. Use ramp command `D` for smoother starts (`envoiCmdi(b'D', left, right, slope, 0)` pattern).
5. Implement wheel speed computation in `task2` (difference of encoder counts divided by elapsed time). Reply with speeds when the Pi issues command `S`.

Phase 7 – Obstacle Handling
---------------------------

1. Validate IR safety threshold with `test_infrared`. Adjust the analogue threshold in `task4` if needed.
2. Extend `task5` to rotate the servo and trigger ultrasonic readings. Store readings in a buffer for Pi retrieval.
3. Define simple safety zones on the Pi:
   * Front distance < 25 cm → stop.
   * Side distance < 30 cm → slow down.
4. Fuse IR and ultrasonic readings (median filter the ultrasonic data to reduce noise).
5. Test first with motors stopped, then moving slowly. Log raw sensor data for calibration.

Phase 8 – Intersections and Recovery
------------------------------------

1. When your perception pipeline detects three or more strong corners, treat it as an intersection. Decide on a policy (default straight, or preprogrammed turn order).
2. Build a simple state machine with states: `FOLLOW`, `SEARCH_LEFT`, `SEARCH_RIGHT`, `STOP`.
   * If the line disappears for more than a threshold, transition to `SEARCH`.
   * In `SEARCH`, command gentle turns using differential wheel speeds and monitor for line reacquisition.
3. Use encoder counts (`N` command) to measure how far you turn during search routines.
4. Log each state transition and sensor snapshot to help debug behaviour.

Phase 9 – ZeroMQ Supervision
----------------------------

1. On your laptop, run `python3 basic_infrastructure/server.py`. Update `server_ip` (line 19) to the laptop’s IP.
2. On the Pi, run `python3 basic_infrastructure/robot.py <server_ip> bot001`. It registers and polls for key commands.
3. On the laptop, run `python3 basic_infrastructure/control.py <server_ip>`. Enter single-character commands to send teleoperation requests (e.g., mode toggles).
4. Extend payloads:
   * Modify `robot.py` to include telemetry (battery voltage via `T`, current error, operating mode) in responses.
   * Update `server.py` to store last `key` and optionally broadcast telemetry to monitoring tools.
5. Implement watchdog behaviour: if no command arrives for >500 ms, stop the motors. Supplement Arduino safety by sending `C 0 0` when idle.

Phase 10 – MVP Field Test Checklist
-----------------------------------

1. Hardware sanity:
   * Tighten wheel screws and servo mounts.
   * Secure wiring, check grounds, confirm battery levels.
2. Software deployment:
   * Flash the latest `serial_link.ino`.
   * Start Pi scripts (use `tmux` or systemd service).
3. Dry run with wheels lifted: verify perception output and motor commands without movement.
4. Floor tests:
   * Begin with straight line following at low speed.
   * Gradually raise base speed as behaviour stabilises.
5. Obstacle introduction: place a soft block and confirm IR/ultrasonic logic. Ensure the robot stops or slows before contact.
6. Intersection test: tape a crossing and confirm your decision logic responds properly.

Phase 11 – Toward a Complete Prototype
--------------------------------------

1. Consolidate into a main orchestrator script (`main.py`) on the Pi with modules for perception, motion control, obstacle management, state machine, and telemetry.
2. Provide a configuration file (JSON or YAML) for thresholds and gains so tweaks require no code changes.
3. Add structured logging in `/var/log/vac/YYYYMMDD` (CSV for telemetry, optional video clips via `cv2.VideoWriter`).
4. Stress-test on extended tracks (e.g., figure-eight layout from `simulink/huit.jpg`). Use `simulink/suivi_ligne_huit_eleve_2022b.slx` if you have MATLAB to simulate advanced control before field trials.
5. Implement recovery heuristics:
   * Reverse and turn if IR triggers repeatedly.
   * Detect encoder mismatches indicating wheel slip.
6. Keep functions short and comment only when logic is not obvious. Follow the repository’s style conventions.

Phase 12 – Iterative Workflow Tips
----------------------------------

* Change one parameter at a time; log before/after comparisons.
* Use Git branches for experimental features and commit often.
* Allow motors to cool; avoid high-PWM stalls.
* Carry a multimeter and spare cables; many “bugs” are power or grounding issues.
* For perception tuning, record short videos under varied lighting and replay offline.

Phase 13 – Documentation and Handover
-------------------------------------

1. Update `2_livrables/taches_detaillees.md` as tasks complete.
2. Refresh `2_livrables/strat-syst.md` with real decisions and adjustments.
3. Export the architecture diagram: `mmdc -i 2_livrables/diagram.mmd -o 2_livrables/diagram.svg`.
4. Write an operator manual covering startup, teleop controls, recovery, and shutdown.
5. Before final demo, clone the SD card (golden image) and archive Arduino sketches.

Suggested Next Steps
--------------------

1. Automate launching the main script using systemd and document the service.
2. Build a lightweight ZeroMQ dashboard (terminal or web) showing telemetry.
3. Extend obstacle logic to plan detours instead of only stopping.
4. Train a simple colour classifier to improve robustness against lighting changes.
