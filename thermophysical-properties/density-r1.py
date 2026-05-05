import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# --- Configuration & Constants derived from Fortran comments ---

# Ti13Zr13Nb Constants
TI_NB_ZR = {
    "name": "Ti13Zr13Nb",
    "Tm": 1973.15, # Melting point (Kelvin)
    "thermal_conductivity": {
        "solid": {
            "A": -1.66755674e-06, "B": 4.80727332e-03, "C": 2.629e+01,
            "offset": 298.15
        },
        "liquid": {
            "D": 0.017, "E": 2.9663644e+01,
            "offset": 1973.15
        }
    },
    "density": {
        # Solid: C + B*(T-298.15) + A*(T-298.15)^2
        "solid": {
            "A": -6.12812244e-05, "B": -1.17609767e-01, "C": 5.29571e+03,
            "offset": 298.15
        },
        # Liquid: E + D*(T-1973.15)
        "liquid": {
            "D": -0.23, "E": 4926.781505,
            "offset": 1973.15
        }
    }
}

# Au (Gold) Constants
AU = {
    "name": "Au",
    "Tm": 1337.33, # Standard melting point for Gold
    "thermal_conductivity": {
        # Solid: C + B*T + A*T^2 (A=0)
        "solid": {
            "A": 0.0, "B": -6.93088808e-02, "C": 3.38918567e+02,
            "offset": 0.0 # No offset for Au thermal solid
        },
        # Liquid: E + D*T
        "liquid": {
            "D": 0.027397, "E": 100.0,
            "offset": 0.0 # No offset for Au thermal liquid
        }
    },
    "density": {
        # Solid: C + B*T + A*T^2
        "solid": {
            "A": 0.0, "B": -1.20, "C": 19657.6,
            "offset": 0.0 
        },
        # Liquid: E + D*T
        "liquid": {
            "D": -1.44, "E": 19325.28,
            "offset": 0.0
        }
    }
}

MATERIALS = {
    "Ti13Zr13Nb": TI_NB_ZR,
    "Au": AU
}

# --- Physics Calculation Functions ---

def calculate_property(mat_name, temp, prop_type):
    mat = MATERIALS[mat_name]
    props = mat[prop_type]
    Tm = mat["Tm"]
    
    # Unpack coefficients
    # Solid coefficients
    A_s = props["solid"]["A"]
    B_s = props["solid"]["B"]
    C_s = props["solid"]["C"]
    offset_s = props["solid"]["offset"]
    
    # Liquid coefficients
    D_l = props["liquid"]["D"]
    E_l = props["liquid"]["E"]
    offset_l = props["liquid"]["offset"]
    
    if temp < Tm:
        # Solid Phase Calculation
        # Formula: C + B*(T - offset) + A*(T - offset)^2
        T_calc = temp - offset_s
        val = C_s + B_s * T_calc + A_s * (T_calc**2)
        phase = "Solid"
    else:
        # Liquid Phase Calculation
        # Formula: E + D*(T - offset)
        T_calc = temp - offset_l
        val = E_l + D_l * T_calc
        phase = "Liquid"
        
    return val, phase

# --- Streamlit UI Layout ---

st.set_page_config(
    page_title="Material Property Plotter",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Material Properties: Ti13Zr13Nb & Au")
st.markdown("""
Plots **Thermal Conductivity** or **Density** as a function of temperature based on ELMER user-defined functions.
""")

# Sidebar Controls
st.sidebar.header("Configuration")

# 1. Select Property Type
property_type = st.sidebar.radio(
    "Select Property to Plot",
    options=["Thermal Conductivity", "Density"],
    index=0
)

# 2. Temperature Range
temp_min, temp_max = st.sidebar.slider(
    "Temperature Range (K)",
    min_value=200.0, max_value=3000.0, value=(298.15, 2500.0), step=10.0
)

# 3. Material Selection
selected_materials = st.sidebar.multiselect(
    "Select Materials",
    options=list(MATERIALS.keys()),
    default=list(MATERIALS.keys())
)

# 4. Resolution
num_points = st.sidebar.slider("Data Points", 100, 1000, 500)

# --- Data Generation ---

if not selected_materials:
    st.warning("Please select at least one material.")
else:
    # Generate Temperature Array
    temps = np.linspace(temp_min, temp_max, num_points)
    
    # Prepare Data for Plotting and Download
    plot_data = []
    
    # Determine Units based on property
    if property_type == "Thermal Conductivity":
        y_label = "Thermal Conductivity (W/mK)"
        col_name = "Conductivity (W/mK)"
    else:
        y_label = "Density (kg/m³)"
        col_name = "Density (kg/m3)"
    
    for mat_name in selected_materials:
        values = []
        phases = []
        
        for T in temps:
            val, ph = calculate_property(mat_name, T, property_type.lower().replace(" ", "_"))
            values.append(val)
            phases.append(ph)
            
        # Create DataFrame for this material
        df_mat = pd.DataFrame({
            "Temperature (K)": temps,
            "Material": mat_name,
            "Phase": phases,
            col_name: values
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
            ax.plot(solid_data["Temperature (K)"], solid_data[col_name], 
                    color=c, linestyle='-', linewidth=2, label=f"{mat_name} (Solid)")
        
        # Plotting Liquid
        liquid_data = subset[subset["Temperature (K)"] >= Tm]
        if not liquid_data.empty:
            ax.plot(liquid_data["Temperature (K)"], liquid_data[col_name], 
                    color=c, linestyle='--', linewidth=2, label=f"{mat_name} (Liquid)")
            
            # Add a marker for Melting Point transition
            # Find the point closest to Tm in the dataframe
            idx = (subset["Temperature (K)"] - Tm).abs().idxmin()
            ax.plot(subset.loc[idx, "Temperature (K)"], subset.loc[idx, col_name], 
                    marker='o', color='red', markersize=5)

    ax.set_title(f"{property_type} vs. Temperature", fontsize=14)
    ax.set_xlabel("Temperature (K)", fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend()
    
    st.pyplot(fig)

    # --- Data Display and Download ---
    
    st.subheader("📥 Data Download")
    st.write(f"Preview of the {property_type.lower()} data:")
    st.dataframe(master_df, use_container_width=True)

    # Prepare CSV
    csv = master_df.to_csv(index=False).encode('utf-8')
    filename_base = property_type.lower().replace(" ", "_")
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name=f'{filename_base}_data.csv',
        mime='text/csv',
    )

    # Prepare DAT (Tab separated)
    buffer = io.StringIO()
    master_df.to_csv(buffer, index=False, sep='\t')
    dat_bytes = buffer.getvalue().encode('utf-8')
    
    st.download_button(
        label="Download as DAT (Tab-Separated)",
        data=dat_bytes,
        file_name=f'{filename_base}_data.dat',
        mime='text/plain',
    )
