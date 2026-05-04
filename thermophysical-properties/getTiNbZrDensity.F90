    !-----------------------------------------------------
    ! material property user defined function for ELMER:
    ! Density of titanium fitted as a function of temperature
    ! (kth_ti)solid = A*(T-298.15)^2 + B*(T-298.15) + C, where A = -6.12812244e-05 kg/m3K2 and B = -1.17609767e-01 kg/m3K and C = 5.29571e+03 kg/m3
    ! X.P. Zhang  et al. J. Mater. Sci. (2005), Vol. 40:4911-4916
    ! https://link.springer.com/content/pdf/10.1007/s10853-005-0418-0.pdf
    ! Written By: Anil Kunwar (Original 2015-03-13) (Modification 2021-11-16)
    ! (kth_ti)liquid = D*(T-1973.15) + E, where D = -0.23 kg/m3K  and E = 4926.781505 kg/m3
    ! https://link.springer.com/content/pdf/10.1007/s11434-011-4945-6.pdf
    !-----------------------------------------------------
    FUNCTION getDensity( model, n, temp ) RESULT(denst)
    ! modules needed
    USE DefUtils
    IMPLICIT None
    ! variables in function header
    TYPE(Model_t) :: model
    INTEGER :: n
    REAL(KIND=dp) :: temp, denst

    ! variables needed inside function
    REAL(KIND=dp) :: refDenst, alpha, beta, delta, lambda, refTemp
    Logical :: GotIt
    TYPE(ValueList_t), POINTER :: material

    ! get pointer on list for material
    material => GetMaterial()
    IF (.NOT. ASSOCIATED(material)) THEN
    CALL Fatal('getDensity', 'No material found')
    END IF

    ! read in reference conductivity at reference temperature
    refDenst = GetConstReal( material, 'Reference Density C Solid TiNbZr',GotIt)
    !refDenst = GetConstReal( material, 'Solid_ti_rho_constant',GotIt)
    IF(.NOT. GotIt) THEN
    CALL Fatal('getDensity', 'Reference Density Solid TiNbZr not found')
    END IF

    ! read in Temperature Coefficient of Resistance
    alpha = GetConstReal( material, 'Density Coeff B Solid TiNbZr', GotIt)
    IF(.NOT. GotIt) THEN
    CALL Fatal('getDensity', 'slope of Density-temperature curve solid not found')
    END IF
    
    ! read in Temperature Coefficient of Resistance
    beta = GetConstReal( material, 'Density Coeff A Solid TiNbZr', GotIt)
    IF(.NOT. GotIt) THEN
    CALL Fatal('getDensity', 'Coefficientt of T2 term solid TiNbZr not found')
    END IF
    
    ! read in Temperature Coefficient of Resistance for Liquid Ti
    delta = GetConstReal( material, 'Density Coeff D Liquid TiNbZr', GotIt)
    IF(.NOT. GotIt) THEN
    CALL Fatal('getDensity', 'Coefficient of T term liquid TiNbZr not found')
    END IF
    
    ! read in pseudo reference conductivity at reference temperature of liquid
    lambda = GetConstReal( material, 'Reference Density E Liquid TiNbZr',GotIt)
    IF(.NOT. GotIt) THEN
    CALL Fatal('getDensity', 'Reference Density Liquid TiNbZr not found')
    END IF

    ! read in reference temperature
    refTemp = GetConstReal( material, 'Melting Point Temperature TiNbZr', GotIt)
    IF(.NOT. GotIt) THEN
    CALL Fatal('getDensity', 'Reference Temperature not found')
    END IF


    ! compute density conductivity
    IF (refTemp <= temp) THEN ! check for physical reasonable temperature
       CALL Warn('getDensity', 'The TiNbZr material is in liquid state.')
            !CALL Warn('getDensity', 'Using density reference value')
    !denst = 1.11*(refDenst + alpha*(temp))
    denst = lambda + delta*(temp-1973.15)
    ELSE
    denst = refDenst + alpha*(temp-298.15) + beta*((temp-298.15)**2)
    END IF

    END FUNCTION getDensity

