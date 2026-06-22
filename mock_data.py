"""
Mock OBD data generator.

Produces fake but realistic sensor values that drift over time, so
the dashboard has something believable to render while the real
ELM327 adapter is still in transit. Values are randomwalk-style:
each reading nudges slightly from the last one instead of jumping
around randomly, so a live dashboard looks like a real driving car
rather than noise.
"""

import random
import time

# Starting points and bounds for each simulated PID.
# (start_value, min_value, max_value, max_step_per_update)
_PID_PROFILES = {
    "RPM": (800, 700, 6000, 150),
    "SPEED": (0, 0, 120, 4),
    "COOLANT_TEMP": (70, 60, 105, 1),
    "FUEL_LEVEL": (60, 0, 100, 0.2),
    "THROTTLE_POS": (10, 0, 100, 8),
    "INTAKE_TEMP": (25, -10, 50, 0.5),
}


class MockSensorState:
    """Holds the current simulated value for every PID and evolves it over time."""

    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)

        self._values = {name: profile[0] for name, profile in _PID_PROFILES.items()}
        self._last_update = time.time()

    def _drift(self, name):
        """Nudge a single value randomly within its bounds and step size."""
        start, lo, hi, max_step = _PID_PROFILES[name]
        current = self._values[name]
        step = random.uniform(-max_step, max_step)
        new_value = max(lo, min(hi, current + step))
        self._values[name] = new_value
        return new_value

    def tick(self):
        """Advance every simulated value by one step. Call this once per polling cycle."""
        for name in _PID_PROFILES:
            self._drift(name)

        # Keep correlated values plausible: RPM and speed should move together,
        # idle RPM with high speed (or vice versa) would look fake.
        if self._values["SPEED"] < 2 and self._values["RPM"] > 1500:
            self._values["RPM"] = max(700, self._values["RPM"] - 300)

        self._last_update = time.time()

    def get(self, name):
        return self._values.get(name)
