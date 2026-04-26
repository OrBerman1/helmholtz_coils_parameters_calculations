import streamlit as st
import numpy as np
from coil_physics import run_calculation
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
