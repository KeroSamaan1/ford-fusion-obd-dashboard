"""
OBD connection wrapper.

Wraps python-obd so the rest of the dashboard code never has to know
whether it's talking to a real ELM327 adapter or the mock data
generator. Both paths return the same shape: a dict of
{pid_name: value} with plain numbers already unwrapped from units.

Usage:
    from obd_interface import OBDInterface

    iface = OBDInterface(use_mock=True)   # or False once hardware arrives
    iface.connect()
    readings = iface.read_all()
    # readings == {"RPM": 842.0, "SPEED": 0.0, "COOLANT_TEMP": 69.6, ...}
"""

import obd

from mock_data import MockSensorState

# The PIDs the dashboard cares about. Maps our internal name to the
# python-obd command object used for real hardware queries.
WATCHED_PIDS = {
    "RPM": obd.commands.RPM,
    "SPEED": obd.commands.SPEED,
    "COOLANT_TEMP": obd.commands.COOLANT_TEMP,
    "FUEL_LEVEL": obd.commands.FUEL_LEVEL,
    "THROTTLE_POS": obd.commands.THROTTLE_POS,
    "INTAKE_TEMP": obd.commands.INTAKE_TEMP,
}


class OBDInterface:
    def __init__(self, use_mock=True, port=None):
        """
        use_mock: True to use fabricated data (no hardware needed)
        port: serial port for the real adapter, e.g. 'COM5' on Windows.
              Leave None to let python-obd auto-detect.
        """
        self.use_mock = use_mock
        self.port = port
        self._connection = None
        self._mock_state = None

    def connect(self):
        if self.use_mock:
            self._mock_state = MockSensorState()
            return True

        self._connection = obd.OBD(self.port) if self.port else obd.OBD()
        return self._connection.is_connected()

    def is_connected(self):
        if self.use_mock:
            return self._mock_state is not None
        return self._connection is not None and self._connection.is_connected()

    def read_all(self):
        """Return a dict of {pid_name: float_value} for every watched PID."""
        if self.use_mock:
            return self._read_mock()
        return self._read_real()

    def _read_mock(self):
        self._mock_state.tick()
        return {name: round(self._mock_state.get(name), 1) for name in WATCHED_PIDS}

    def _read_real(self):
        readings = {}
        for name, command in WATCHED_PIDS.items():
            response = self._connection.query(command)
            if response.is_null():
                readings[name] = None
            else:
                # response.value is a pint Quantity (number + unit) - unwrap to a plain float
                readings[name] = round(response.value.magnitude, 1)
        return readings

    def close(self):
        if not self.use_mock and self._connection is not None:
            self._connection.close()
