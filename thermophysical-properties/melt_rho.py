def calculate_rho(T):
    A = -6.12812244e-05  # kg/m^3-K^2
    B = -1.17609767e-01  # kg/m^3-K
    C = 5.29571e+03      # kg/m^3
    
    T_ref = 298.15       # Reference temperature in Kelvin

    # Calculate rho at T = 1973.15 K using the provided formula
    rho = A * (T - T_ref)**2 + B * (T - T_ref) + C

    return rho

def main():
    T = 1973.15  # Temperature in Kelvin

    # Calculate the value of rho at T = 1973.15 K
    rho_at_T = calculate_rho(T)

    print(f"rho at T = 1973.15 K: {rho_at_T:.6f} kg/m^3")

if __name__ == "__main__":
    main()

