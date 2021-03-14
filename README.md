# Pipe_flow_simulation
Basic pipe flow simulator supporting turbomachinery 

# Motivation 
School project that I put too much effort into 

# Features
- Flowrate simulations for a variety of pipe systems (or at least the systems found in fluid mechanics textbooks) 
- Turbomachinery support

# Code examples 

The simulation is made up of three classes. 

First the the pipe class, this class holds all the information on the various pipes that makes up the system. Pipe needs inputs of L (length), D (diameter) and Roughness. Optional variables are the minor losses in the pipe, Height (elevation change across the pipe), Pressure_drop (difference in pressure) and D_exit (True of False, if exit velocities are considered.) All units are SI units, pressure is in kPa. As many pipes as needed can be easily added. 

```Python
pipe_1 = Pipe(L=5, D=.1, Roughness=.00001, Minor_loss=1.06)
pipe_2 = Pipe(L=8, D=.2*2, Roughness=.00003, Minor_loss=4, Height=-10)
```

The Subsystem class contains: 
- Needed variables
- - pipe_list = list of pipes used in the system
# Density = Density
# ---- one of:
# Vis = Viscosity
# Kin_vis = Kinematic viscosity, will be calculated from viscosity if not provided

# --------- Used to solve questions / answers to questions
# Velocity Enter = Velocity at entrance. Will be used to get flowrate and velocities
# Target = target head loss, will be used if no flowrate is provided to automatically fit
# Flowrate = if provided will calculate velocities and losses in pipes, if not will iterate to find

# --------- Additional tools
# exit = if True will include the velocity at the exit as a loss
# disp = display the results if True
# minor_loss_pipe = if False will use the minor losses coefficient and their corresponding head to get the minor losses
#                   can also be a number corresponding to the pipe velocity used to find losses.
#                   minor_loss_pipe = 2 means the 3rd pipe (3rd in the list) will be used to calculate the minor losses
# max_q = maximum flow to guess for iteration
