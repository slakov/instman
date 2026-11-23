"""Exact phase locking of a pair of Kuramoto oscillators.

Run with Python 3: python3 phase_locking.py > results.csv
Angles are measured in radians and time in hours. The coupling term in
each oscillator's equation is (K/2) * sin(other_phase - own_phase).
The reported gap is the faster oscillator's phase minus the slower one's.
"""

import csv
import math
import sys


PERIODS_H = (24.0, 25.0)
COUPLING_MULTIPLIERS = (0.0, 0.5, 1.0, 2.0)


def main():
    fast_period, slow_period = sorted(PERIODS_H)
    if not 0 < fast_period < slow_period:
        raise ValueError("Use two different positive natural periods.")
    fast_rate = math.tau / fast_period
    slow_rate = math.tau / slow_period
    detuning = fast_rate - slow_rate
    shared_period = math.tau / ((fast_rate + slow_rate) / 2)

    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(["fast_period_h", "slow_period_h", "K_over_detuning",
                     "K_rad_per_h", "regime", "phase_gap_deg", "shared_period_h"])
    for multiple in COUPLING_MULTIPLIERS:
        coupling = multiple * detuning
        gap = ""
        period = ""
        if multiple < 0:
            raise ValueError("This example uses attractive coupling (K >= 0).")
        if multiple < 1:
            regime = "drift"
        else:
            regime = "threshold" if multiple == 1 else "stable_lock"
            gap = f"{math.degrees(math.asin(detuning / coupling)):.6f}"
            period = f"{shared_period:.6f}"
        writer.writerow([fast_period, slow_period, multiple, f"{coupling:.9f}",
                         regime, gap, period])


if __name__ == "__main__":
    main()
