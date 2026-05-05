!Gaussian 
FUNCTION TravellingHeatSource( Model, n, t ) RESULT(f)
  USE DefUtils

  IMPLICIT NONE

  TYPE(Model_t) :: Model
  INTEGER :: n
  REAL(KIND=dp) :: t, f


  INTEGER :: timestep, prevtimestep = -1
  REAL(KIND=dp) :: Alpha, Coeff, Speed, Dist, Dist0, &
      Time, x, y, z, s, sper, r, yzero, Omega
  TYPE(Mesh_t), POINTER :: Mesh
  TYPE(ValueList_t), POINTER :: Params
  LOGICAL :: Found, NewTimestep
  
  SAVE Mesh, Params, prevtimestep, time, Alpha, Coeff, Speed, Dist, &
      Dist0, Omega
  
  timestep = GetTimestep()
  NewTimestep = ( timestep /= prevtimestep )

  IF( NewTimestep ) THEN
    Mesh => GetMesh()
    Params => Model % Simulation
    time = GetTime()
    Alpha = GetCReal(Params,'Heat source width')
    Coeff = GetCReal(Params,'Heat source coefficient')
    Speed = GetCReal(Params,'Heat source speed')
    Dist = GetCReal(Params,'Heat source distance')
    Dist0 = GetCReal(Params,'Heat source initial position', Found)
    yzero = GetCReal(Params,'y coordinate initial position', Found)
    Omega = GetCReal(Params,'Absorptance of Surface Material')
    prevtimestep = timestep
  END IF

  x = Mesh % Nodes % x(n)   
  y = Mesh % Nodes % y(n)   
  z = Mesh % Nodes % z(n)   

  s = Dist0 + time * Speed  
  !sper = MODULO( s, 2 * Dist ) 
  !IF( sper > Dist ) sper = 2 * Dist - sper

  !r = x-s!sper
  ! in 3D this could be the radius
   r = SQRT((x-s)**2 + (y-yzero)**2)
  
  !f = Coeff * EXP( -2*r**2 / Alpha**2 )
  f = Coeff * EXP( -2*r**2 / Alpha**2 -Omega * ABS(z))
    
END FUNCTION TravellingHeatSource

!Gaussian
FUNCTION FixedHeatSource( Model, n, t ) RESULT(f)
  USE DefUtils

  IMPLICIT NONE

  TYPE(Model_t) :: Model
  INTEGER :: n
  REAL(KIND=dp) :: t, f


  INTEGER :: timestep, prevtimestep = -1
  REAL(KIND=dp) :: Alpha, Coeff, Dist0, &
      Time, x, y, z, r
  TYPE(Mesh_t), POINTER :: Mesh
  TYPE(ValueList_t), POINTER :: Params
  LOGICAL :: Found, NewTimestep
  
  SAVE Mesh, Params, prevtimestep, time, Alpha, Coeff, Dist0
  
  timestep = GetTimestep()
  NewTimestep = ( timestep /= prevtimestep )

  IF( NewTimestep ) THEN
    Mesh => GetMesh()
    Params => Model % Simulation
    time = GetTime()
    Alpha = GetCReal(Params,'Heat source width')
    Coeff = GetCReal(Params,'Heat source coefficient')
    Dist0 = GetCReal(Params,'Heat source initial position', Found)
    prevtimestep = timestep
  END IF

  x = Mesh % Nodes % x(n)   
  y = Mesh % Nodes % y(n)   
  z = Mesh % Nodes % z(n)   

  ! not a function of time
  r = x-Dist0

  ! in 3D this could be the radius
  ! r = SQRT((x-s)**2 + y**2)
  
  f = Coeff * EXP( -2*r**2 / Alpha**2 )
    
END FUNCTION FixedHeatSource

!Slab movement
FUNCTION TravellingSlabVelo( Model, n, t ) RESULT(f)
  USE DefUtils

  IMPLICIT NONE

  TYPE(Model_t) :: Model
  INTEGER :: n
  REAL(KIND=dp) :: t, f


  INTEGER :: timestep, prevtimestep = -1
  REAL(KIND=dp) :: Alpha, Coeff, Speed, Dist, Dist0, &
      Time, x, y, z, s, sper, r
  TYPE(Mesh_t), POINTER :: Mesh
  TYPE(ValueList_t), POINTER :: Params
  LOGICAL :: Found, NewTimestep
  
  SAVE Mesh, Params, prevtimestep, time, Alpha, Coeff, Speed, Dist, &
      Dist0
  
  timestep = GetTimestep()
  NewTimestep = ( timestep /= prevtimestep )

  IF( NewTimestep ) THEN
    Mesh => GetMesh()
    Params => Model % Simulation
    time = GetTime()
    Speed = GetCReal(Params,'Heat source speed')
    Dist = GetCReal( Params,'Heat source distance')
    prevtimestep = timestep
  END IF

  x = Mesh % Nodes % x(n)   
  y = Mesh % Nodes % y(n)   
  z = Mesh % Nodes % z(n)   

  s = Dist0 + time * Speed  
  sper = MODULO( s, 2 * Dist ) 

  IF( sper > Dist ) THEN
    sper = 2 * Dist - sper
    f = Speed
  ELSE
    f = -Speed
  END IF
    
END FUNCTION TravellingSlabVelo


!Flat top for travelling source
FUNCTION FlatTopHeatSource( Model, n, t ) RESULT(f)
  USE DefUtils

  IMPLICIT NONE

  TYPE(Model_t) :: Model
  INTEGER :: n
  REAL(KIND=dp) :: t, f


  INTEGER :: timestep, prevtimestep = -1
  REAL(KIND=dp) :: Alpha, Coeff, Speed, Dist, Dist0, &
      Time, x, y, z, s, sper, r, yzero, Omega !, Sigma
  TYPE(Mesh_t), POINTER :: Mesh
  TYPE(ValueList_t), POINTER :: Params
  LOGICAL :: Found, NewTimestep
  
  SAVE Mesh, Params, prevtimestep, time, Alpha, Coeff, Speed, Dist, &
      Dist0, Omega   !, Sigma
  
  timestep = GetTimestep()
  NewTimestep = ( timestep /= prevtimestep )

  IF( NewTimestep ) THEN
    Mesh => GetMesh()
    Params => Model % Simulation
    time = GetTime()
    Alpha = GetCReal(Params,'Heat source width')
    Coeff = GetCReal(Params,'Heat source coefficient')
    Speed = GetCReal(Params,'Heat source speed')
    Dist = GetCReal(Params,'Heat source distance')
    Dist0 = GetCReal(Params,'Heat source initial position', Found)
    yzero = GetCReal(Params,'y coordinate initial position', Found)
    Omega = GetCReal(Params,'Absorptance of Top Surface Material')
    !Sigma = GetCReal(Params,'Absorptance of Bottom Surface Material')
    prevtimestep = timestep
  END IF

  x = Mesh % Nodes % x(n)   
  y = Mesh % Nodes % y(n)   
  z = Mesh % Nodes % z(n)   

  s = Dist0 + time * Speed  
  !sper = MODULO( s, 2 * Dist ) 
  !IF( sper > Dist ) sper = 2 * Dist - sper

  !r = x-s!sper
  ! in 3D this could be the radius
   r = SQRT((x-s)**2 + (y-yzero)**2)
  
  !f = Coeff * EXP( -2*r**2 / Alpha**2 )
  !f = Coeff * EXP( -2*r**2 / Alpha**2 -Omega * ABS(z))
  ! compute the values of flat top heat source
  ! f definition taken from Astrath et al., Appl Phys B (2009) 94: 473–481
  IF (ABS(r) < Alpha) THEN ! check for physical reasonable temperature
     CALL Warn('FlatTopHeatSource', 'Region inside the beam spot.')
          !CALL Warn('getDensity', 'Using density reference value')
  !denst = 1.11*(refDenst + alpha*(temp))
   !denst = lambda + delta*(temp)
  !f = Coeff * EXP(-Omega * ABS(z))
     IF (ABS(z) < 5.0E-08) THEN ! check for physical reasonable temperature 20 nm
     f = Coeff * EXP(-Omega * ABS(z))
     ELSE
     f = 0.05*Coeff    !0.3*Coeff** EXP(-Sigma * ABS(z))
     END IF
  ELSE
  f = 0 !f = Coeff * EXP(-Omega * ABS(z))
  END IF
    
END FUNCTION FlatTopHeatSource
