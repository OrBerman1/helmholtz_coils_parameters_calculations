import streamlit as st
import numpy as np
from helmholtz_parameters import run_calculation

st.title("Helmholtz Coil Designer")
with st.sidebar:
    work_volume = st.number_input("Work Volume (m)", value=0.1)
    coil_dist = st.number_input("Coil Distance (m)", value=0.1)
    b_target = st.number_input("Target Field (T)", value=1e-4, format="%.2e")
    rho = st.number_input("Resistivity (Ohm*m)", value=1.68e-8, format="%.2e")
    wire_dia = st.number_input("Wire Diameter (m)", value=0.4e-3, format="%.4f")
    di_dt = st.number_input("dI/dt (A/s)", value=0.0)
    mu = st.number_input("Permeability", value=4*np.pi*1e-7, format="%.2e")
    n_turns = st.number_input("Turns", value=100)

res = run_calculation(work_volume, coil_dist, b_target, rho, wire_dia, di_dt, mu, n_turns)
st.json(res)

