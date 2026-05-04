import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# --- Configuration & Constants derived from Fortran comments ---
# Constants are extracted from the provided comments in the Fortran code.

# Ti13Zr13Nb Constants
# (kth_ti)solid = A*(T-298.15)^2 + B*(T-298.15) + C
TI_NB_ZR = {
    "name": "Ti13Zr13Nb",
    "Tm": 1973.15, # Melting point (Kelvin)
    "solid": {
        "A": -1.66755674e-06,
        "B": 4.80727332e-03,
        "C": 2.629e+01
    },
    # (kth_ti)liquid = D*(T-1973.15) + E
    "liquid": {
        "D": 0.017,
        "E": 2.9663644e+01
    }
}

# Au (Gold) Constants
# Note: The Fortran comments for Au block were mixed with Ti text, 
# but the variable names and structure imply:
# (kth)solid = A*T^2 + B*T + C (A=0 based on comments)
# (kth)liquid = D*T + E
AU = {
    "name": "Au",
    "Tm": 1337.33, # Standard melting point for Gold
    "solid": {
        "A": 0.0,
        "B": -6.93088808e-02,
        "C": 3.38918567e+02
    },
    "liquid": {
        "D": 0.027397,
        "E": 100.0
    }
}

MATERIALS = {
    "Ti13Zr13Nb": TI_NB_ZR,
    "Au": AU
}

# --- Physics Calculation Functions ---

def get_conductivity_ti(temp):
    """
    Calculates thermal conductivity for Ti13Zr13Nb based on the provided Fortran logic.
    """
    mat = MATERIALS["Ti13Zr13Nb"]
    Tm = mat["Tm"]
    
    if temp < Tm:
        # Solid: C + B*(T-298.15) + A*(T-298.15)^2
        T_ref = 298.15
        val = (mat["solid"]["C"] + 
               mat["solid"]["B"] * (temp - T_ref) + 
               mat["solid"]["A"] * ((temp - T_ref)**2))
        phase = "Solid"
    else:
        # Liquid: E + D*(T-1973.15)
        T_ref_liquid = 1973.15
        val = (mat["liquid"]["E"] + 
               mat["liquid"]["D"] * (temp - T_ref_liquid))
        phase = "Liquid"
        
    return val, phase

def get_conductivity_au(temp):
    """
    Calculates thermal conductivity for Au based on the provided Fortran logic.
    Note: The Au liquid function in Fortran used 'lambda + delta*(temp)' 
    without an explicit offset subtraction, unlike Ti.
    """
    mat = MATERIALS["Au"]
    Tm = mat["Tm"]
    
    if temp < Tm:
        # Solid: C + B*T + A*T^2 (A is 0)
        val = (mat["solid"]["C"] + 
               mat["solid"]["B"] * temp + 
               mat["solid"]["A"] * (temp**2))
        phase = "Solid"
    else:
        # Liquid: E + D*T
        val = (mat["liquid"]["E"] + 
               mat["liquid"]["D"] * temp)
        phase = "Liquid"
        
    return val, phase

# --- Streamlit UI Layout ---

st.set_page_config(
    page_title="Thermal Conductivity Plotter",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Material Thermal Conductivity: Solid vs Liquid")
st.markdown("""
Plots thermal conductivity ($\lambda$) vs Temperature ($T$) for **Ti13Zr13Nb** and **Au**.
Based on the provided user-defined functions for ELMER.
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
    "Select Materials",
    options=list(MATERIALS.keys()),
    default=list(MATERIALS.keys()) # Select all by default
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
        k_values = []
        phases = []
        
        for T in temps:
            if mat_name == "Ti13Zr13Nb":
                k, ph = get_conductivity_ti(T)
            else: # Au
                k, ph = get_conductivity_au(T)
            
            k_values.append(k)
            phases.append(ph)
            
        # Create DataFrame for this material
        df_mat = pd.DataFrame({
            "Temperature (K)": temps,
            "Material": mat_name,
            "Phase": phases,
            "Thermal Conductivity (W/mK)": k_values
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
            ax.plot(solid_data["Temperature (K)"], solid_data["Thermal Conductivity (W/mK)"], 
                    color=c, linestyle='-', linewidth=2, label=f"{mat_name} (Solid)")
        
        # Plotting Liquid
        liquid_data = subset[subset["Temperature (K)"] >= Tm]
        if not liquid_data.empty:
            ax.plot(liquid_data["Temperature (K)"], liquid_data["Thermal Conductivity (W/mK)"], 
                    color=c, linestyle='--', linewidth=2, label=f"{mat_name} (Liquid)")
            
            # Add a marker for Melting Point transition
            # Find the point closest to Tm in the dataframe
            idx = (subset["Temperature (K)"] - Tm).abs().idxmin()
            ax.plot(subset.loc[idx, "Temperature (K)"], subset.loc[idx, "Thermal Conductivity (W/mK)"], 
                    marker='o', color='red', markersize=5)

    ax.set_title("Thermal Conductivity vs. Temperature", fontsize=14)
    ax.set_xlabel("Temperature (K)", fontsize=12)
    ax.set_ylabel(r"Conductivity $\lambda$ (W/mK)", fontsize=12)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend()
    
    st.pyplot(fig)

    # --- Data Display and Download ---
    
    st.subheader("📥 Data Download")
    st.write("Preview of the generated data:")
    st.dataframe(master_df, use_container_width=True)

    # Prepare CSV
    csv = master_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name='thermal_conductivity_data.csv',
        mime='text/csv',
    )

    # Prepare DAT (Space separated, commonly used in engineering)
    # We drop the 'Phase' column for raw numerical DAT format usually, or keep it. 
    # Keeping it allows better parsing.
    buffer = io.StringIO()
    # Using sep=' ' or '\t' for .dat files. Let's use tab-separated for clarity.
    master_df.to_csv(buffer, index=False, sep='\t')
    dat_bytes = buffer.getvalue().encode('utf-8')
    
    st.download_button(
        label="Download as DAT (Tab-Separated)",
        data=dat_bytes,
        file_name='thermal_conductivity_data.dat',
        mime='text/plain',
    )
