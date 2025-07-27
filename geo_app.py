import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Water Infiltration Rate Calculator")

# --- 1. PIT DETAILS ---
st.header("1. Pit Details")
col1, col2, col3 = st.columns(3)
length = col1.number_input("Length (m)", value=1.20)
width = col2.number_input("Width (m)", value=0.35)
depth = col3.number_input("Depth (m)", value=1.00)
void_ratio = st.number_input("Gravel Void Ratio", value=0.3, min_value=0.0, max_value=1.0)

# --- 2. TIME–DEPTH READINGS ---
st.header("2. Time vs Water Depth Readings (mbgl)")
st.markdown("Enter time in **minutes** and depth in **mbgl**. First row should be initial, last row should be final depth.")

default_data = {
    "Time [min]": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25],
    "Depth to Water [mbgl]": [0.70, 0.71, 0.72, 0.73, 0.75, 0.75, 0.76, 0.78, 0.79, 0.79, 0.80, 0.86, 0.88, 0.925]
}
df = st.data_editor(pd.DataFrame(default_data), num_rows="dynamic")
df_clean = df.dropna()

# --- 3. INFILTRATION RATE CALCULATION ---
if len(df_clean) >= 2:
    start_depth = df_clean["Depth to Water [mbgl]"].iloc[0]
    end_depth = df_clean["Depth to Water [mbgl]"].iloc[-1]

    h75 = end_depth
    h25 = h75 - 0.150
    delta_h = h75 - h25

    # Interpolate times for h25 and h75 (linear)
    t75 = np.interp(h75, df_clean["Depth to Water [mbgl]"], df_clean["Time [min]"]) * 60
    t25 = np.interp(h25, df_clean["Depth to Water [mbgl]"], df_clean["Time [min]"]) * 60
    delta_t = t75 - t25

    v7525 = length * width * delta_h * void_ratio
    aP50 = (2 * length * delta_h) + (2 * width * delta_h) + (length * width)
    f = v7525 / (aP50 * delta_t) if aP50 * delta_t != 0 else 0

    # --- 4. RESULTS ---
    st.header("3. Results (BRE Digest 365 Method)")
    col1, col2, col3 = st.columns(3)
    col1.metric("Effective Volume (m³)", f"{v7525:.4f}")
    col2.metric("Effective Area (m²)", f"{aP50:.3f}")
    col3.metric("Infiltration Rate (m/s)", f"{f:.2e}")

    with st.expander("Infiltration Rate Calculations"):
        st.write(f"**h75:** {h75:.3f} m at **t75:** {t75:.0f} s")
        st.write(f"**h25:** {h25:.3f} m at **t25:** {t25:.0f} s")
        st.write(f"**Δh:** {delta_h:.3f} m, **Δt:** {delta_t:.0f} s")

    # --- 5. PLOT ---
    st.header("4. Soakage Rate Plot")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df_clean["Time [min]"], df_clean["Depth to Water [mbgl]"], marker="o", color="gray", label="Water Depth (mbgl)")
    ax.axhline(h75, color="red", linestyle="--", label=f"h75 = {h75:.3f} m")
    ax.axhline(h25, color="green", linestyle="--", label=f"h25 = {h25:.3f} m")
    ax.set_xlabel("Time (min)")
    ax.set_ylabel("Depth to Water (mbgl)")
    ax.set_title("Water Level Drop Over Time")
    ax.invert_yaxis()
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)
else:
    st.warning("Enter at least two valid time–depth readings.")
