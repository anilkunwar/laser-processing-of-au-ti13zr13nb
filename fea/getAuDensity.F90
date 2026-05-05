    !-----------------------------------------------------
    ! material property user defined function for ELMER:
    ! Density of titanium fitted as a function of temperature
    ! (kth_ti)solid = A*T^2 + B*T + C, where A = 0 kg/m3K2 and B = -1.20 kg/m3K and C = 19657.6 kg/m3 (adapted from Au18Zn alloy)
    ! Ricci  et al. Gold Bulletin (2001), Vol. 34:41-49
    ! https://link.springer.com/article/10.1007%2FBF03214811
    ! https://asmedigitalcollection.asme.org/heattransfer/article/130/6/062401/466820/An-Interfacial-Tracking-Method-for-Ultrashort
    ! https://link.springer.com/content/pdf/10.1007/BF03216580.pdf
    ! Written By: Anil Kunwar (Original 2015-03-13) (Modification 2021-11-16)
    ! (kth_ti)liquid = D*T + E, where D = -1.44 kg/m3K  and E = 19325.28 kg/m3
    ! Paradis  et al. Gold Bulletin (2008), Vol. 41:242-245
    ! https://link.springer.com/article/10.1007%2FBF03214876
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
    refDenst = GetConstReal( material, 'Reference Density C Solid Au',GotIt)
    IF(.NOT. GotIt) THEN
    CALL Fatal('getDensity', 'Reference Density Solid Au not found')
    END IF

    ! read in Temperature Coefficient of Resistance
    alpha = GetConstReal( material, 'Density Coeff B Solid Au', GotIt)
    IF(.NOT. GotIt) THEN
    CALL Fatal('getDensity', 'slope of Density-temperature curve solid not found')
    END IF
    
    ! read in Temperature Coefficient of Resistance
    beta = GetConstReal( material, 'Density Coeff A Solid Au', GotIt)
    IF(.NOT. GotIt) THEN
    CALL Fatal('getDensity', 'Coefficientt of T2 term solid Au not found')
    END IF
    
    ! read in Temperature Coefficient of Resistance for Liquid Ti
    delta = GetConstReal( material, 'Density Coeff D Liquid Au', GotIt)
    IF(.NOT. GotIt) THEN
    CALL Fatal('getDensity', 'Coefficient of T term liquid Au not found')
    END IF
    
    ! read in pseudo reference conductivity at reference temperature of liquid
    lambda = GetConstReal( material, 'Reference Density E Liquid Au',GotIt)
    IF(.NOT. GotIt) THEN
    CALL Fatal('getDensity', 'Reference Density Liquid Au not found')
    END IF

    ! read in reference temperature
    refTemp = GetConstReal( material, 'Melting Point Temperature Au', GotIt)
    IF(.NOT. GotIt) THEN
    CALL Fatal('getDensity', 'Reference Temperature not found')
    END IF


    ! compute density conductivity
    IF (refTemp <= temp) THEN ! check for physical reasonable temperature
       CALL Warn('getDensity', 'The Au material is in liquid state.')
            !CALL Warn('getDensity', 'Using density reference value')
    !denst = 1.11*(refDenst + alpha*(temp))
    denst = lambda + delta*(temp)
    ELSE
    denst = refDenst + alpha*(temp) + beta*(temp**2)
    END IF

    END FUNCTION getDensity

