import numpy as np
from scipy.special import ellipk, ellipe


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


def calculate_field_error(coil_dist, radius, b_target, work_volume, mu, n_turns, current_i, is_helmholtz):
    z_max = work_volume / 2
    a = coil_dist / 2

    # Check if we are at Helmholtz condition (d = R)
    if is_helmholtz:
        # Exact 4th derivative error
        k = (mu * n_turns * current_i * radius ** 2) / 2
        deriv_4 = -666 * k * a ** 4 / (radius ** 2 + a ** 2) ** 5.5
        return abs(deriv_4 / 24 * z_max ** 4) / b_target * 100
    else:
        # Exact 2nd derivative error (for non-Helmholtz)
        # B''(z) = (k * (12*a^2 - 6*R^2) / (R^2 + a^2)^3.5)
        k = (mu * n_turns * current_i * radius ** 2) / 2
        deriv_2 = k * (12 * a ** 2 - 6 * radius ** 2) / (radius ** 2 + a ** 2) ** 3.5
        return abs(deriv_2 / 2 * z_max ** 2) / b_target * 100


def calculate_wire_length(n_turns, radius):
    """
    Calculates the total wire length for both coils.
    Formula: 2 * (Number of turns per coil) * (Circumference of one turn)
    """
    # Circumference of one turn: 2 * pi * R
    circumference = 2 * np.pi * radius

    # Total length for two coils
    total_length = 2 * n_turns * circumference

    return total_length


def calculate_field_at_coil_center(mu, n_turns, current_i, radius, coil_dist, b_target):
    """
    Calculates the absolute magnetic field strength at the center of one of the coils.
    This includes the contribution from the coil itself and the second, distant coil.
    """
    # Contribution from the coil itself (at its own center)
    b_self = (mu * n_turns * current_i) / (2 * radius)

    # Contribution from the other coil (at distance d)
    b_from_far_coil = (mu * n_turns * current_i * radius ** 2) / (2 * (radius ** 2 + coil_dist ** 2) ** 1.5)

    # total_b_at_coil = np.abs(b_self + b_from_far_coil - b_target)
    total_b_at_coil = b_self + b_from_far_coil
    return total_b_at_coil


def generate_graph_data(radius, coil_dist, n_turns, current_i, mu, points=200):
    A = coil_dist / 2
    z_axis = np.linspace(-A, A, points)

    def get_b_at_z(z):
        term1 = 1 / (radius ** 2 + (z - A) ** 2) ** 1.5
        term2 = 1 / (radius ** 2 + (z + A) ** 2) ** 1.5
        return (mu * n_turns * current_i * radius ** 2 / 2) * (term1 + term2)

    b_values = np.array([get_b_at_z(z) for z in z_axis])

    return {
        "z_axis": z_axis,
        "b_values_ut": b_values * 1e6,  # המרה למיקרו-טסלה
        "coil_positions": [-A, A],
        "params": {"R": radius, "d": coil_dist, "I": current_i}
    }


def get_b_field_3d(x, y, z, radius, coil_dist, n_turns, current_i, mu):
    def single_loop_field(x, y, z_rel):
        r = np.sqrt(x ** 2 + y ** 2)

        if r < 1e-10:
            bz = (mu * n_turns * current_i * radius ** 2) / (2 * (radius ** 2 + z_rel ** 2) ** 1.5)
            return 0.0, 0.0, bz

        # k^2 = 4*R*r / ((R+r)^2 + z^2)
        k_sq = (4 * radius * r) / ((radius + r) ** 2 + z_rel ** 2)

        K = ellipk(k_sq)
        E = ellipe(k_sq)

        common = (mu * n_turns * current_i) / (2 * np.pi * np.sqrt((radius + r) ** 2 + z_rel ** 2))

        bz = common * (K + (radius ** 2 - r ** 2 - z_rel ** 2) / ((radius - r) ** 2 + z_rel ** 2) * E)

        br = common * (z_rel / r) * (-K + (radius ** 2 + r ** 2 + z_rel ** 2) / ((radius - r) ** 2 + z_rel ** 2) * E)

        bx = br * (x / r)
        by = br * (y / r)

        return bx, by, bz

    b1 = np.array(single_loop_field(x, y, z - coil_dist / 2))
    b2 = np.array(single_loop_field(x, y, z + coil_dist / 2))

    return b1 + b2


def run_calculation(work_volume, coil_dist, b_target, rho, wire_dia, di_dt, mu, n_turns, radius):
    if coil_dist < work_volume - 0.000000001:
        return {"error": "Geometric Error: Coil distance is smaller than work volume!"}
    is_helmholtz = np.isclose(coil_dist, radius, atol=1e-3)
    current_i = calculate_i_general(b_target, radius, mu, n_turns, coil_dist)
    r_coil = calculate_resistance(wire_dia, n_turns, radius, rho)
    voltage_v = calculate_voltage(mu, n_turns, radius, current_i, r_coil, di_dt)
    power, p_density = calculate_power(current_i, r_coil, radius, n_turns, wire_dia)
    error = calculate_field_error(coil_dist, radius, b_target, work_volume, mu, n_turns, current_i, is_helmholtz)
    total_wire_length = calculate_wire_length(n_turns, radius)
    total_b_at_coil = calculate_field_at_coil_center(mu, n_turns, current_i, radius, coil_dist, b_target)
    graph_data = generate_graph_data(radius, coil_dist, n_turns, current_i, mu)

    return {
        "is_helmholtz": is_helmholtz, "current_a": current_i, "voltage_v": voltage_v,
        "resistance_ohm": r_coil, "power_w": power, "power_density_w_m2": p_density,
        "max_error_percent": error,
        "total_wire_length_m": total_wire_length,
        "total_b_at_coil": total_b_at_coil,
        "graph_data": graph_data
    }
