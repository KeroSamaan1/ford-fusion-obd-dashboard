# ford-fusion-obd-dashboard

Live OBD-II dashboard for a 2020 Ford Fusion Plug-in Hybrid, built around an ELM327 USB adapter with MS-CAN/HS-CAN switching.

Reads engine and vehicle data in real time and displays it in a terminal dashboard. Built with a mock data layer so the whole thing can be developed and tested without the adapter plugged in.

## Architecture

- `obd_interface.py` - wraps `python-obd`, exposes one consistent API whether you're using real hardware or fabricated data
- `mock_data.py` - generates realistic, slowly-drifting sensor values for development without hardware
- `dashboard/display.py` - terminal UI that polls the interface and renders live readings
- `main.py` - entry point, switches between mock and real via a command line flag

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/ford-fusion-obd-dashboard.git
cd ford-fusion-obd-dashboard
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

## Usage

Run with mock data (no hardware needed):

```bash
python main.py
```

Once the ELM327 adapter is plugged in:

```bash
python main.py --real
```

Specify a port explicitly if auto-detect doesn't find it:

```bash
python main.py --real --port COM5
```

Adjust polling rate (default 0.5s):

```bash
python main.py --interval 1.0
```

## PIDs currently tracked

- RPM
- Vehicle speed
- Coolant temperature
- Fuel level
- Throttle position
- Intake air temperature

## Notes on the Fusion PHEV

This adapter has an MS-CAN/HS-CAN switch. Standard PIDs above come over HS-CAN and work with any ELM327. Hybrid-specific data (EV battery state of charge, electric motor output, EV mode status) lives on Ford's proprietary MS-CAN bus and needs extended PIDs - that's a planned addition once the basics are working and verified against the real car.

## Roadmap

- [ ] Verify all PIDs against the real adapter once it arrives
- [ ] Add Ford-specific MS-CAN PIDs for hybrid battery state of charge
- [ ] Log sessions to CSV for later review
- [ ] GUI dashboard (tkinter or similar) instead of terminal output
- [ ] Warning thresholds tuned to actual Fusion PHEV spec ranges
