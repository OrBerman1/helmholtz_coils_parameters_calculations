import argparse
import numpy as np
from coil_physics import run_calculation
import matplotlib.pyplot as plt


def plot_graph_cli(graph_data):
    z = graph_data["z_axis"]
    b = graph_data["b_values_ut"]
    coils = graph_data["coil_positions"]

    plt.figure(figsize=(8, 5))
    plt.plot(z, b, label='Magnetic Field (B)', color='blue')

    for pos in coils:
        plt.axvline(x=pos, color='red', linestyle='--', alpha=0.5)

    plt.title(f"Field Profile (I={graph_data['params']['I']:.3f}A)")
    plt.xlabel("Position Z [m]")
    plt.ylabel("Field [uT]")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--work_volume", type=float, default=0.1)
    parser.add_argument("--coil_dist", type=float, default=0.1)
    parser.add_argument("--radius", type=float, default=0.1)
    parser.add_argument("--b_target", type=float, default=1e-4)
    parser.add_argument("--rho", type=float, default=1.68e-8)
    parser.add_argument("--wire_dia", type=float, default=0.4e-3)
    parser.add_argument("--di_dt", type=float, default=0.0)
    parser.add_argument("--mu", type=float, default=4 * np.pi * 1e-7)
    parser.add_argument("--n_turns", type=int, default=100)

    args = parser.parse_args()
    res = run_calculation(**vars(args))

    params = vars(args)
    print("--- System Parameters ---")
    for key, value in params.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    print("\n\n")
    # Print results
    for key, value in res.items():
        if key == "graph_data":
            plot_graph_cli(value)
        elif key != "warning":
            print(f"{key.replace('_', ' ').title()}: {value}")

    # Explicitly print the warning if present
    if "warning" in res:
        print(f"\n!!! WARNING: {res['warning']} !!!")
