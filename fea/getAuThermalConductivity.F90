    !-----------------------------------------------------
    ! material property user defined function for ELMER:
    ! Thermal conductivity of titanium fitted as a function of temperature
    ! (kth_ti)solid = A*T^2+B*T + C, where A = 0, B= -6.93088808e-02 W /m and B = 3.38918567e+02 W/mK
    ! Cook et al, Canadian Journal of Physics , 1970 (48), pp. 254-263
    ! https://cdnsciencepub.com/doi/10.1139/p70-035
    ! Written By: Anil Kunwar (Original 2015-03-13) (Modification 2021-11-19)
    ! (kth_ti)liquid = D*T + E, where D = 0.027397 W/m K^2 and E = 100.0 W/m K
    ! Petrov et al (2015), PIERS proceedings
    ! http://laser.itp.ac.ru/publications/4A2_2431.pdf
    !-----------------------------------------------------
    FUNCTION getThermalConductivity( model, n, temp ) RESULT(thcondt)
    ! modules needed
    USE DefUtils
    IMPLICIT None
    ! variables in function header
    TYPE(Model_t) :: model
    INTEGER :: n
    REAL(KIND=dp) :: temp, thcondt

    ! variables needed inside function
    REAL(KIND=dp) :: refThCond, alpha, beta, delta, lambda, refTemp
    Logical :: GotIt
    TYPE(ValueList_t), POINTER :: material

    ! get pointer on list for material
    material => GetMaterial()
    IF (.NOT. ASSOCIATED(material)) THEN
    CALL Fatal('getThermalConductivity', 'No material found')
    END IF

    ! read in reference conductivity at reference temperature
    refThCond = GetConstReal( material, 'Reference Thermal Conductivity C Solid Au',GotIt)
    IF(.NOT. GotIt) THEN
    CALL Fatal('getThermalConductivity', 'Reference Thermal Conductivity Solid Au not found')
    END IF

    ! read in Temperature Coefficient of Resistance
    alpha = GetConstReal( material, 'Cond Coeff B Solid Au', GotIt)
    IF(.NOT. GotIt) THEN
    CALL Fatal('getThermalConductivity', 'slope of thermal conductivity-temperature curve solid not found')
    END IF
    
    ! read in Temperature Coefficient of Resistance
     beta = GetConstReal( material, 'Cond Coeff A Solid Au', GotIt)
     IF(.NOT. GotIt) THEN
     CALL Fatal('getThermalConductivity', 'Coefficientt of T2 term Solid Au not found')
     END IF
    
    ! read in Temperature Coefficient of Resistance for Liquid Au
    delta = GetConstReal( material, 'Cond Coeff D Liquid Au', GotIt)
    IF(.NOT. GotIt) THEN
    CALL Fatal('getThermalConductivity', 'Coefficient of T term Liquid Au not found')
    END IF
    
    ! read in pseudo reference conductivity at reference temperature of liquid
    lambda = GetConstReal( material, 'Reference Thermal Conductivity E Liquid Au',GotIt)
    IF(.NOT. GotIt) THEN
    CALL Fatal('getThermalConductivity', 'Reference Thermal Conductivity Liquid Au not found')
    END IF

    ! read in reference temperature
    refTemp = GetConstReal( material, 'Melting Point Temperature Au', GotIt)
    IF(.NOT. GotIt) THEN
    CALL Fatal('getThermalConductivity', 'Reference Temperature not found')
    END IF


    ! compute density conductivity
    IF (refTemp <= temp) THEN ! check for physical reasonable temperature
       CALL Warn('getThermalConductivity', 'The Au material is in liquid state.')
            !CALL Warn('getThermalConductivity', 'Using density reference value')
    !thcondt = 1.11*(refThCond + alpha*(temp))
    thcondt = lambda + delta*(temp)
    ELSE
    thcondt = refThCond + alpha*(temp) + beta*(temp**2)
    END IF

    END FUNCTION getThermalConductivity

