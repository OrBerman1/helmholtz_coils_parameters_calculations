import streamlit as st
import numpy as np
from coil_physics import run_calculation, get_b_field_3d
import plotly.graph_objects as go


def display_graph_streamlit(graph_data):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=graph_data["z_axis"],
        y=graph_data["b_values_ut"],
        mode='lines',
        name='B Field (uT)'
    ))

    for pos in graph_data["coil_positions"]:
        fig.add_vline(x=pos, line_dash="dash", line_color="red")

    fig.update_layout(
        title="התפלגות השדה המגנטי לאורך הציר",
        xaxis_title="מיקום (מטרים)",
        yaxis_title="עוצמת שדה (uT)",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)


@st.cache_data
def generate_xy_slice_object(z_offset, radius, coil_dist, n_turns, current_i, mu, res=40):
    span = radius
    grid = np.linspace(-span, span, res)
    x_grid, y_grid = np.meshgrid(grid, grid)

    z_field = np.zeros((res, res))

    for i in range(res):
        for j in range(res):
            b_vec = get_b_field_3d(x_grid[i, j], y_grid[i, j], z_offset, radius, coil_dist, n_turns, current_i, mu)
            z_field[i, j] = np.linalg.norm(b_vec) * 1e6

    return {
        "x": grid,
        "y": grid,
        "z_matrix": z_field,
        "z_offset": z_offset,
        "params": {"R": radius, "d": coil_dist, "I": current_i}
    }


def display_3d_slice_streamlit(slice_data):
    """
    מציג מפה תרמית של החתך הניצב (XY)
    """
    fig = go.Figure(data=go.Heatmap(
        z=slice_data["z_matrix"],
        x=slice_data["x"],
        y=slice_data["y"],
        colorscale='Viridis',
        colorbar=dict(title="uT")
    ))

    fig.update_layout(
        title=f"חתך XY בגובה z = {slice_data['z_offset']} מטר",
        xaxis_title="X [m]",
        yaxis_title="Y [m]",
        width=600,
        height=600
    )

    st.plotly_chart(fig)


st.title("Coil System Calculator")

# Sidebar for all parameters
with st.sidebar:
    work_volume = st.number_input("Work Volume (m)", value=0.1)
    coil_dist = st.number_input("Coil Distance (m)", value=0.1)
    radius = st.number_input("Radius (m)", value=0.05)
    b_target = st.number_input("Target Field (T)", value=1e-4, format="%.2e")
    rho = st.number_input("Resistivity (Ohm*m)", value=1.68e-8, format="%.2e")
    wire_dia = st.number_input("Wire Diameter (m)", value=0.4e-3, format="%.4f")
    di_dt = st.number_input("dI/dt (A/s)", value=0.0)
    mu = st.number_input("Permeability", value=4*np.pi*1e-7, format="%.2e")
    n_turns = st.number_input("Turns", value=100)
    z_offset = st.sidebar.slider("Z location", min_value=-coil_dist/2, max_value=coil_dist/2, value=0.0, step=0.01)

res = run_calculation(work_volume, coil_dist, b_target, rho, wire_dia, di_dt, mu, n_turns, radius)

if "error" in res:
    st.error(res["error"])
else:
    # Display the warning prominently if it exists
    if "warning" in res:
        st.warning(res["warning"])
    graph_data = res["graph_data"]
    res.pop("graph_data")

    st.json(res)
    display_graph_streamlit(graph_data)
    slice_data = generate_xy_slice_object(z_offset, radius, coil_dist, n_turns, res["current_a"], mu)
    display_3d_slice_streamlit(slice_data)
