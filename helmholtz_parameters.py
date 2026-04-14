# coil_physics.py
import numpy as np


def calculate_i(b_target, radius, mu, n_turns):
    coeff = (4 / 5) ** 1.5
    return (b_target * radius) / (coeff * mu * n_turns)


def calculate_resistance(wire_dia, n_turns, radius, rho):
    area = np.pi * (wire_dia / 2) ** 2
    length = 2 * n_turns * (2 * np.pi * radius)
    return rho * (length / area)


def calculate_voltage(mu, n_turns, radius, current_i, r_coil, di_dt):
    # חישוב השראות
    l_inductance = (mu * np.pi * n_turns ** 2 * radius ** 2) / (radius * 0.1)
    return (current_i * r_coil) + (l_inductance * di_dt)


def calculate_power(current_i, r_coil, radius, n_turns, wire_dia):
    power = (current_i ** 2) * r_coil
    surface_area = 2 * (2 * np.pi * radius * (n_turns * wire_dia))
    return power, power / surface_area


def calculate_error(coil_dist, mu, n_turns, current_i, radius, work_volume, b_target):
    a = coil_dist / 2
    k = (mu * n_turns * current_i * radius ** 2) / 2
    deriv_4 = -666 * k * a ** 4 / (radius ** 2 + a ** 2) ** 5.5
    z_max = work_volume / 2
    return abs(deriv_4 / 24 * z_max ** 4) / b_target * 100


def run_calculation(work_volume, coil_dist, b_target, rho, wire_dia, di_dt, mu, n_turns):
    if coil_dist < work_volume:
        return {"error": "Geometric Error: Coil distance is smaller than work volume!"}

    radius = coil_dist / 2
    current_i = calculate_i(b_target, radius, mu, n_turns)
    r_coil = calculate_resistance(wire_dia, n_turns, radius, rho)
    voltage_v = calculate_voltage(mu, n_turns, radius, current_i, r_coil, di_dt)
    power, p_density = calculate_power(current_i, r_coil, radius, n_turns, wire_dia)
    err = calculate_error(coil_dist, mu, n_turns, current_i, radius, work_volume, b_target)

    return {
        "current_a": current_i, "voltage_v": voltage_v, "resistance_ohm": r_coil,
        "power_w": power, "power_density_w_m2": p_density, "max_error_percent": err
    }
