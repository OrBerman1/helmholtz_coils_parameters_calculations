import numpy as np


def check_deviation(radius, n_turns, b_target, mu):
    # Old Helmholtz coefficient
    coeff = (4 / 5) ** 1.5
    i_old = (b_target * radius) / (coeff * mu * n_turns)
    return i_old


def calculate_i_general(b_target, radius, mu, n_turns, coil_dist):
    z = coil_dist / 2
    b_single_per_amp = (mu * n_turns * radius ** 2) / (2 * (radius ** 2 + z ** 2) ** 1.5)
    return b_target / (2 * b_single_per_amp)


def calculate_resistance(wire_dia, n_turns, radius, rho):
    area = np.pi * (wire_dia / 2) ** 2
    length = 2 * n_turns * (2 * np.pi * radius)
    return rho * (length / area)


def calculate_voltage(mu, n_turns, radius, current_i, r_coil, di_dt):
    l_inductance = (mu * np.pi * n_turns ** 2 * radius ** 2) / (radius * 0.1)
    return (current_i * r_coil) + (l_inductance * di_dt)


def calculate_power(current_i, r_coil, radius, n_turns, wire_dia):
    power = (current_i ** 2) * r_coil
    surface_area = 2 * (2 * np.pi * radius * (n_turns * wire_dia))
    return power, power / surface_area


def run_calculation(work_volume, coil_dist, b_target, rho, wire_dia, di_dt, mu, n_turns, radius):
    if coil_dist < work_volume:
        return {"error": "Geometric Error: Coil distance is smaller than work volume!"}
    print(f"deviation check: {check_deviation(radius, n_turns, b_target, mu)}")
    is_helmholtz = np.isclose(coil_dist, radius, atol=1e-3)
    current_i = calculate_i_general(b_target, radius, mu, n_turns, coil_dist)
    r_coil = calculate_resistance(wire_dia, n_turns, radius, rho)
    voltage_v = calculate_voltage(mu, n_turns, radius, current_i, r_coil, di_dt)
    power, p_density = calculate_power(current_i, r_coil, radius, n_turns, wire_dia)

    return {
        "is_helmholtz": is_helmholtz, "current_a": current_i, "voltage_v": voltage_v,
        "resistance_ohm": r_coil, "power_w": power, "power_density_w_m2": p_density
    }