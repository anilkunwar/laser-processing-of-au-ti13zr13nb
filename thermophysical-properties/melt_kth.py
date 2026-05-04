def calculate_kth_ti(T):
    A = -1.66755674e-06  # W/K/m
    B = 4.80727332e-03   # W/m
    C = 2.629e+01        # W/m-K
    
    T_ref = 298.15       # Reference temperature in Kelvin

    # Calculate kth at T = 1973.15 K using the provided formula
    kth_ti_solid = A * (T - T_ref) ** 2 + B * (T - T_ref) + C

    return kth_ti_solid

def main():
    T = 1973.15  # Temperature in Kelvin

    # Calculate the value of kth at T = 1973.15 K
    kth_ti_solid = calculate_kth_ti(T)

    print(f"kth at T = 1973.15 K (Ti, solid): {kth_ti_solid:.6f} W/m-K")

if __name__ == "__main__":
    main()

