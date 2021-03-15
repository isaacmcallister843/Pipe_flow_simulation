# Pipe_flow_simulation
Basic pipe flow simulator supporting turbomachinery 

# Motivation 
School project that I put too much effort into 

# Features
- Flowrate simulations for a variety of pipe systems (or at least the systems found in fluid mechanics textbooks) 
- Turbomachinery support

# Code examples 

The simulation is made up of three classes. 

The pipe class holds all the information on the various pipes that makes up the system. Pipe needs inputs of L(length), D (diameter) and Roughness. Optional variables are the minor losses in the pipe, Height (elevation change across the pipe), Pressure_drop (difference in pressure) and D_exit (the exit diameter, if non defaults to False.) All units are SI units, pressure is in kPa. 

Height and pressure can be considered system qualities, they are included in the pipe class for flexibility and data collection purposes (i.e its easy to measure the elevation change of many pipes individually compared to a whole network of pipes.) 

```Python
pipe_1 = Pipe(L=5, D=.1, Roughness=.00001, Minor_loss=1.06)
pipe_2 = Pipe(L=8, D=.2*2, Roughness=.00003, Minor_loss=4, Height=-10)
```

The Subsystem class contains: 
- Needed variables
  - pipe_list = list of pipes used in the system
  - Density = the density of the fluid
  
- one of:
  - Vis = Viscosity
  - Kin_vis = Kinematic viscosity, will be calculated from viscosity if not provide
  
- Used to solve questions / answers to questions
  - Velocity Enter = Velocity at entrance. Will be used to get flowrate and other pipe velocities 
  - Target = target head loss, will be used if no flowrate is provided to calculate flowrate (defaults to 0) 
  - Flowrate = if provided will calculate velocities and losses in pipes, if not will iterate to find

- Additional tools
  - exit = if True will include the velocity at the exit as a loss, defaults to False
  - disp = display the results if True
  - minor_loss_pipe = if False will use the minor losses coefficient and their corresponding head to get the minor losses. can also be a number corresponding to the pipe velocity used to find losses (i.e minor_loss_pipe = 2 means the 3rd pipe (3rd in the list) will be used to calculate the minor losses)
  - max_q = maximum flow to guess for iteration

For this example we want to find the flowrate, after providing the system info the Subsytem class automatically calls the method summary() 

```Python
sub = Subsystem([pipe_1, pipe_2], Density=998, Vis=.001005)
```

Output: 
```
Flowrate is: 0.083390 m^3 / s
Pressure drop is -4.344941 Pa
Total System Head Loss -0.000444 m
Power needed to overcome head it -0.362325 W
error is
0.0004437969282022891
----------------------------
Friciton Factor List:
[0.013270116095496493, 0.015308843387560344]
Velocity List
[10.61755353181037, 0.6635970957381482]
Reynolds List
[1054360.0422633581, 263590.01056583953]
Losses List
[3.8123664789763967, -9.99312801305031]
```

Note that since no target head was provided the total system head was set to 0. The error term represents the net system head (Target - Head of system) closer to 0 the better. 

The last useful tool is the turbo machinery simulator. Data for the pump/turbine/whatever will given in the form of a equation relating head as a function of flowrate, or a data table containing head and flowrate values. This simulator supports both, in the case of data tables numpy is used to find a quadratic polynomial relating head and flowrate. 

For the pump_system class: 
- Needed variables
  - Subsystem = object of class subsystem. NOTE: The flowrate doesnt need to be correct will guess regardless
  
- One of
  - flowrate_array and head_array = list containing flowrate and head values to be fitted
  - ploynomial = array in the form [x^2 coef, x coef, x^0 coef ]
    - i.e H(Q) = 3 Q^2 + 2Q + 3 = [3,2,3]

- Additional Tools
  - Terms = number of terms used for poly fit (defaults to 2) 
  - number_pumps = number of pumps used, defualts to 1
  - char = pump arrangment either
    - S = Series
    - P = Parallel
    - False, default only one pump 

In this example we are given the pump curve: 

```Math 
H(Q) = -1930 Q^2 + 90
```

Converting the pump equation into a list we then pass the following to the pump class

```Python
ploynomial = [-1930, 0, 90]
pump = pump_system(sub, polynomial=ploynomial)
```

pump_system automatically returns a summary 

```
Using Given Poly
Iterating to get Flowrate
----------------------
Flowrate for the system in m^3 / s
[-0.17458287  0.172944  ]
Polynomial Fit is:
       2
-1930 x + 90
```
In this case our flowrate is 0.172944 m^3 / s
