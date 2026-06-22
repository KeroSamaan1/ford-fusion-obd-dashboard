"""
Ford Fusion PHEV OBD dashboard - entry point.

Run with --mock (default) to use fabricated data with no hardware
needed. Once the ELM327 adapter arrives, run with --real and the
adapter's port specified (or leave it blank to auto-detect).

Examples:
    python main.py                  # mock data, no hardware needed
    python main.py --real           # real adapter, auto-detect port
    python main.py --real --port COM5
"""

import argparse

from obd_interface import OBDInterface
from dashboard import display


def main():
    parser = argparse.ArgumentParser(description="Ford Fusion PHEV OBD-II dashboard")
    parser.add_argument(
        "--real",
        action="store_true",
        help="Use the real ELM327 adapter instead of mock data",
    )
    parser.add_argument(
        "--port",
        default=None,
        help="Serial port for the adapter, e.g. COM5 (Windows) or /dev/ttyUSB0 (Linux). Auto-detects if omitted.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.5,
        help="Polling interval in seconds (default 0.5)",
    )
    args = parser.parse_args()

    use_mock = not args.real
    if use_mock:
        print("Running with mock data (no hardware required). Use --real once your adapter arrives.\n")

    interface = OBDInterface(use_mock=use_mock, port=args.port)
    display.run(interface, poll_interval=args.interval)


if __name__ == "__main__":
    main()
