import argparse
import numpy as np


POWER_THRESH = 500


def calculate_coil_system(
        work_volume=0.1, coil_dist=0.1, b_target=1e-4,
        rho=1.68e-8, wire_dia=0.4e-3, di_dt=0.0,
        mu=4 * np.pi * 1e-7, n_turns=100
):
    """
    Calculates electromagnetic and physical parameters for Helmholtz coils.
    """
    if coil_dist < work_volume:
        return {"error": "Geometric Error: Coil distance is smaller than work volume!"}

    radius = coil_dist / 2
    coeff = (4 / 5) ** 1.5
    current_i = (b_target * radius) / (coeff * mu * n_turns)

    area = np.pi * (wire_dia / 2) ** 2
    length = 2 * n_turns * (2 * np.pi * radius)
    r_coil = rho * (length / area)

    l_inductance = (mu * np.pi * n_turns ** 2 * radius ** 2) / (radius / 10)
    voltage_v = (current_i * r_coil) + (l_inductance * di_dt)

    power = (current_i ** 2) * r_coil
    surface_area = 2 * (2 * np.pi * radius * (n_turns * wire_dia))
    power_density = power / surface_area

    a = coil_dist / 2
    k = (mu * n_turns * current_i * radius ** 2) / 2
    deriv_4 = -666 * k * a ** 4 / (radius ** 2 + a ** 2) ** 5.5
    z_max = work_volume / 2
    error_tesla = abs(deriv_4 / 24 * z_max ** 4)
    error_percent = (error_tesla / b_target) * 100

    return {
        "current_a": current_i,
        "voltage_v": voltage_v,
        "resistance_ohm": r_coil,
        "power_w": power,
        "power_density_w_m2": power_density,
        "max_error_percent": error_percent
    }


if __name__ == "__main__":
    # Define the help text structure
    parser = argparse.ArgumentParser(
        description="Helmholtz Coil Design Calculator: Computes I, V, and field error for a specified setup.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("--work_volume", type=float, default=0.1, help="Size of interest region (meters)")
    parser.add_argument("--coil_dist", type=float, default=0.1, help="Distance between coils (meters)")
    parser.add_argument("--b_target", type=float, default=1e-4, help="Target magnetic field (Tesla)")
    parser.add_argument("--rho", type=float, default=1.68e-8, help="Copper resistivity (Ohm*m)")
    parser.add_argument("--wire_dia", type=float, default=0.4e-3, help="Wire diameter (meters)")
    parser.add_argument("--di_dt", type=float, default=0.0, help="Current change rate (Amps/sec)")
    parser.add_argument("--mu", type=float, default=4 * np.pi * 1e-7, help="Permeability of medium")
    parser.add_argument("--n_turns", type=int, default=100, help="Number of turns per coil")

    args = parser.parse_args()

    # Print input parameters as requested
    print("--- System Parameters ---")
    for arg, value in vars(args).items():
        print(f"{arg.replace('_', ' ').title()}: {value}")

    res = calculate_coil_system(**vars(args))

    print("\n--- Calculated Results ---")
    if isinstance(res, dict) and "error" in res:
        print(res["error"])
    else:
        for k, v in res.items():
            print(f"{k.replace('_', ' ').title()}: {v:.6f}")

        if res["power_density_w_m2"] > POWER_THRESH:
            print("\nWARNING: High power density! Active cooling may be required.")