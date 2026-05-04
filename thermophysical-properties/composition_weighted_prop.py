import pandas as pd

def compute_composition_weighted_kth_and_rho(data_frame):
    total_composition = data_frame['Composition'].sum()
    weighted_kth = (data_frame['kth (W/m-K)'] * data_frame['Composition'] / total_composition).sum()
    weighted_rho = (data_frame['rho (kg/m^3)'] * data_frame['Composition'] / total_composition).sum()
    return weighted_kth, weighted_rho

def main():
    # Read CSV data
    df = pd.read_csv('weighted_kthrho.csv')
    
    # Assuming "Composition" column contains the composition data for each element (Ti, Nb, Zr) in the alloy
    # Adjust the column name accordingly based on your CSV file.
    composition_data = df['Composition']

    # Calculate the composition-weighted thermal conductivity and density
    weighted_kth, weighted_rho = compute_composition_weighted_kth_and_rho(df)

    print(f"Composition-weighted thermal conductivity of Ti13Nb13Zr: {weighted_kth:.2f} W/m-K")
    print(f"Composition-weighted density of Ti13Nb13Zr: {weighted_rho:.2f} kg/m^3")

if __name__ == "__main__":
    main()

