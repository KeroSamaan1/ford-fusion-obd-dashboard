"""
Terminal dashboard.

Polls the OBD interface on a fixed interval and redraws a simple
live readout in the terminal. This is the v1 display - a GUI
(tkinter or a Pi touchscreen) can read from the same OBDInterface
later without changing anything here.
"""

import os
import time

PID_LABELS = {
    "RPM": ("RPM", "rpm"),
    "SPEED": ("Speed", "km/h"),
    "COOLANT_TEMP": ("Coolant temp", "C"),
    "FUEL_LEVEL": ("Fuel level", "%"),
    "THROTTLE_POS": ("Throttle", "%"),
    "INTAKE_TEMP": ("Intake air temp", "C"),
}

WARNING_THRESHOLDS = {
    "COOLANT_TEMP": 110,   # overheating territory
    "RPM": 6500,           # near redline for most engines
}


def _clear():
    os.system("cls" if os.name == "nt" else "clear")


def _format_line(pid_name, value):
    label, unit = PID_LABELS.get(pid_name, (pid_name, ""))
    if value is None:
        return f"  {label:<18} --"

    flag = ""
    threshold = WARNING_THRESHOLDS.get(pid_name)
    if threshold is not None and value >= threshold:
        flag = "  <-- HIGH"

    return f"  {label:<18} {value:>8.1f} {unit}{flag}"


def run(interface, poll_interval=0.5):
    """
    Continuously poll the given OBDInterface and render readings to
    the terminal until interrupted with Ctrl+C.
    """
    print("Connecting...")
    if not interface.connect():
        print("Failed to connect to OBD adapter. Check the connection and try again.")
        return

    print("Connected. Starting dashboard - press Ctrl+C to stop.\n")
    time.sleep(1)

    try:
        while True:
            readings = interface.read_all()

            _clear()
            print("========== Ford Fusion PHEV - Live OBD Dashboard ==========\n")
            for pid_name in PID_LABELS:
                print(_format_line(pid_name, readings.get(pid_name)))
            print("\n=============================================================")
            print("Ctrl+C to stop")

            time.sleep(poll_interval)

    except KeyboardInterrupt:
        print("\nStopping dashboard.")
    finally:
        interface.close()
