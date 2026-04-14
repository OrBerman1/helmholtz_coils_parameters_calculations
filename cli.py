import argparse
import numpy as np
from coil_physics import run_calculation

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--work_volume", type=float, default=0.1)
    parser.add_argument("--coil_dist", type=float, default=0.1)
    parser.add_argument("--radius", type=float, default=0.05)
    parser.add_argument("--b_target", type=float, default=1e-4)
    parser.add_argument("--rho", type=float, default=1.68e-8)
    parser.add_argument("--wire_dia", type=float, default=0.4e-3)
    parser.add_argument("--di_dt", type=float, default=0.0)
    parser.add_argument("--mu", type=float, default=4 * np.pi * 1e-7)
    parser.add_argument("--n_turns", type=int, default=100)

    args = parser.parse_args()
    res = run_calculation(**vars(args))

    # Print results
    for key, value in res.items():
        if key != "warning":
            print(f"{key.replace('_', ' ').title()}: {value}")

    # Explicitly print the warning if present
    if "warning" in res:
        print(f"\n!!! WARNING: {res['warning']} !!!")