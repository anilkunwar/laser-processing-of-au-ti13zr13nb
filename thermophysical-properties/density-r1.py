import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# --- Constants derived from Fortran comments ---

# Ti13Zr13Nb Constants
TI_NB_ZR = {
    "name": "Ti13Zr13Nb",
    "Tm": 1973.15, # Melting point (Kelvin)
    # Solid: C + B*(T-298.15) + A*(T-298.15)^2
    "solid": {
        "A": -6.12812244e-05,
        "B": -1.17609767e-01,
        "C": 5.29571e+03
    },
    # Liquid: E + D*(T-1973.15)
    "liquid": {
        "D": -0.23,
        "E": 4926.781505
    }
}

# Au (Gold) Constants
AU = {
    "name": "Au",
    "Tm": 1337.33, # Standard melting point for Gold
    # Solid: C + B*T + A*T^2 (A=0)
    "solid": {
        "A": 0.0,
        "B": -1.20,
        "C": 19657.6
    },
    # Liquid: E + D*T
    "liquid": {
        "D": -1.44,
        "E": 19325.28
    }
}

MATERIALS = {
    "Ti13Zr13Nb": TI_NB_ZR,
    "Au": AU
}

# --- Physics Calculation Functions ---

def get_density(temp, material_name):
    """
    Calculates Density based on the provided Fortran logic for 'getDensity'.
    """
    mat = MATERIALS[material_name]
    Tm = mat["Tm"]
    
    if temp < Tm:
        # SOLID PHASE
        if material_name == "Ti13Zr13Nb":
            # Formula: C + B*(T-298.15) + A*(T-298.15)^2
            T_offset = 298.15
            val = (mat["solid"]["C"] + 
                   mat["solid"]["B"] * (temp - T_offset) + 
                   mat["solid"]["A"] * ((temp - T_offset)**2))
        else: # Au
            # Formula: C + B*T + A*T^2
            val = (mat["solid"]["C"] + 
                   mat["solid"]["B"] * temp + 
                   mat["solid"]["A"] * (temp**2))
        phase = "Solid"
    else:
        # LIQUID PHASE
        if material_name == "Ti13Zr13Nb":
            # Formula: E + D*(T-1973.15)
            T_offset = 1973.15
            val = (mat["liquid"]["E"] + 
                   mat["liquid"]["D"] * (temp - T_offset))
        else: # Au
            # Formula: E + D*T
            val = (mat["liquid"]["E"] + 
                   mat["liquid"]["D"] * temp)
        phase = "Liquid"
        
    return val, phase

# --- Streamlit UI Layout ---

st.set_page_config(
    page_title="Material Density Plotter",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⚖️ Material Density: Ti13Zr13Nb & Au")
st.markdown("""
Plots **Density** ($\rho$) vs Temperature ($T$) for Solid and Liquid phases.
""")

# Sidebar Controls
st.sidebar.header("Configuration")

# Temperature Range
temp_min, temp_max = st.sidebar.slider(
    "Temperature Range (K)",
    min_value=200.0, max_value=3000.0, value=(298.15, 2500.0), step=10.0
)

# Material Selection
selected_materials = st.sidebar.multiselect(
    "Select Materials (Select one or both)",
    options=list(MATERIALS.keys()),
    default=list(MATERIALS.keys())
)

# Resolution
num_points = st.sidebar.slider("Data Points", 100, 1000, 500)

# --- Data Generation ---

if not selected_materials:
    st.warning("Please select at least one material.")
else:
    # Generate Temperature Array
    temps = np.linspace(temp_min, temp_max, num_points)
    
    # Prepare Data for Plotting and Download
    plot_data = []
    
    for mat_name in selected_materials:
        density_values = []
        phases = []
        
        for T in temps:
            rho, ph = get_density(T, mat_name)
            density_values.append(rho)
            phases.append(ph)
            
        # Create DataFrame for this material
        df_mat = pd.DataFrame({
            "Temperature (K)": temps,
            "Material": mat_name,
            "Phase": phases,
            "Density (kg/m3)": density_values
        })
        plot_data.append(df_mat)

    # Concatenate all data into one master dataframe
    master_df = pd.concat(plot_data, ignore_index=True)

    # --- Plotting ---
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = {"Ti13Zr13Nb": "#1f77b4", "Au": "#ff7f0e"}
    
    for mat_name in selected_materials:
        subset = master_df[master_df["Material"] == mat_name]
        mat_info = MATERIALS[mat_name]
        Tm = mat_info["Tm"]
        c = colors.get(mat_name, "black")
        
        # Plotting Solid
        solid_data = subset[subset["Temperature (K)"] < Tm]
        if not solid_data.empty:
            ax.plot(solid_data["Temperature (K)"], solid_data["Density (kg/m3)"], 
                    color=c, linestyle='-', linewidth=2, label=f"{mat_name} (Solid)")
        
        # Plotting Liquid
        liquid_data = subset[subset["Temperature (K)"] >= Tm]
        if not liquid_data.empty:
            ax.plot(liquid_data["Temperature (K)"], liquid_data["Density (kg/m3)"], 
                    color=c, linestyle='--', linewidth=2, label=f"{mat_name} (Liquid)")
            
            # Add a marker for Melting Point transition
            idx = (subset["Temperature (K)"] - Tm).abs().idxmin()
            ax.plot(subset.loc[idx, "Temperature (K)"], subset.loc[idx, "Density (kg/m3)"], 
                    marker='o', color='red', markersize=5)

    ax.set_title("Density vs. Temperature", fontsize=14)
    ax.set_xlabel("Temperature (K)", fontsize=12)
    ax.set_ylabel(r"Density $\rho$ (kg/m$^3$)", fontsize=12)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend()
    
    st.pyplot(fig)

    # --- Data Display and Download ---
    
    st.subheader("📥 Data Download")
    st.write("Preview of the generated density data:")
    st.dataframe(master_df, use_container_width=True)

    # Prepare CSV
    csv = master_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name='density_data.csv',
        mime='text/csv',
    )

    # Prepare DAT (Tab separated)
    buffer = io.StringIO()
    master_df.to_csv(buffer, index=False, sep='\t')
    dat_bytes = buffer.getvalue().encode('utf-8')
    
    st.download_button(
        label="Download as DAT (Tab-Separated)",
        data=dat_bytes,
        file_name='density_data.dat',
        mime='text/plain',
    )
