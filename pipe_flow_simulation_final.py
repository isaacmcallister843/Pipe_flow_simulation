# ---------------------- Libraries and importing
import math
import numpy as np
meter_per_inch = .0254
threshold = .05

# --------------------- Classes
"""
Pipe Class, handles all the features of the pipe 
"""

# Pressue drop is in kpA
# SI units

class Pipe:

    def __init__(self, L=0, D=0, Roughness=0, Minor_loss=0,
                 Height=0, Other_loss=0, Pressure_drop=0, D_exit=False):
        self.length = float(L)
        self.diameter = float(D)
        self.roughness = float(Roughness)
        self.minor_loss = float(Minor_loss)
        self.height = float(Height)
        self.other_loss = float(Other_loss)
        self.pressure_drop = float(Pressure_drop)
        self.area = 3.14159*.25*(self.diameter)**2
        self.D_exit = self.get_d_exit(D_exit)

    def diameter_inch_m(self):
        self.diameter = meter_per_inch * self.diameter
        self.area = 3.14159*.25*(self.diameter)**2

    def get_d_exit(self, D_exit):
        if D_exit == False:
            return self.diameter
        else:
            return D_exit

"""
Sub system Class: Used for multiple pipes
"""
# ------------ Needed variables
# pipe_list = list of pipes used in the system
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

class Subsystem:

    def __init__(self, pipe_list, Vis=0, Density=0, Target=0, Velocity_enter =False, Kin_vis=False, Flowrate=False, exit=False,
                 minor_loss_pipe=False, disp=True, max_q=.5):
        self.friction_factors_list = []
        self.velocity_list = []
        self.re_list = []
        self.pipe_lost_list = []
        self.error = 0


        self.max_q = max_q
        self.velocity_enter = Velocity_enter
        self.pipes = pipe_list
        self.density = float(Density)
        self.target = float(Target)
        self.exit = exit

        self.minor_loss_pipe = minor_loss_pipe
        self.minor_loss = self.get_minor_loss()

        self.vis = Vis
        self.kin_vis = self.kin_vis_check(Kin_vis)

        self.flowrate = self.get_flowrate(Flowrate)

        self.head_loss = self.get_head_friction(self.flowrate)
        self.presure_drop = self.head_loss * self.density * 9.81
        self.power_out = self.flowrate * self.presure_drop
        if disp:
            self.summary()

    def kin_vis_check(self, Kin_vis):
        if Kin_vis == False:
            return self.vis/self.density
        else:
            return Kin_vis

    def get_minor_loss(self):
        minor = 0
        for pipe in self.pipes:
            minor = minor + pipe.minor_loss
        return minor

    def get_friction_factor(self, reynolds, pipe):
        if reynolds < 2300:
            return 64 / reynolds
        else:
            ratio = pipe.roughness/pipe.diameter
            inner = 6.9 / reynolds + (ratio/3.7)**(1.11)
            return (1/(-1.8*math.log(inner, 10)))**2

    def get_head_friction(self, flowrate):
        loss = 0
        friction_factors = []
        velocity_list = []
        re_list = []
        pipe_lost_list = []

        for pipe in self.pipes:
            velocity = flowrate / pipe.area
            re = velocity * pipe.diameter / self.kin_vis
            friction_factor = self.get_friction_factor(re, pipe)
            pipe_loss = friction_factor * pipe.length/pipe.diameter * (velocity**2) / (2*9.81) + \
                        pipe.pressure_drop * 10**3 / (self.density * 9.81) + pipe.height
            loss = loss + pipe_loss

            pipe_lost_list.append(pipe_loss)
            friction_factors.append(friction_factor)
            velocity_list.append(velocity)
            re_list.append(re)

        self.friction_factors_list = friction_factors
        self.velocity_list = velocity_list
        self.re_list = re_list
        self.pipe_lost_list = pipe_lost_list

        if self.exit == True:
            velocity_loss = (flowrate / (3.14159/4 * self.pipes[-1].D_exit**2))**2 / (2*9.81)
        else:
            velocity_loss = 0

        if self.minor_loss_pipe != False:
            minor_loss = (flowrate / self.pipes[self.minor_loss_pipe].area)**2 * self.minor_loss / (2*9.81)

        else:
            minor_loss = 0
            for i in range(len(velocity_list)):
                minor_loss = minor_loss + velocity_list[i]**2 * self.pipes[i].minor_loss / (2* 9.81)

        return minor_loss + loss + velocity_loss

    def get_flowrate(self, Flowrate):

        if Flowrate != False:
            return Flowrate
        if self.velocity_enter != False:
            self.get_head_friction(self.velocity_enter * self.pipes[0].area)
            return self.velocity_enter * self.pipes[0].area
        else:
            print("Performing Iteration to get flowrate")
            flowrate_guess = .00001
            system_array = np.array([10000.00, 10000.00])

            while flowrate_guess < self.max_q:
                head = abs(self.get_head_friction(flowrate_guess) - self.target)
                system_array = np.vstack((system_array, [head, flowrate_guess]))
                flowrate_guess = flowrate_guess + .00001
            print(system_array)
            self.error = system_array[np.argmin(system_array[:, 0]), :][0]

            return system_array[np.argmin(system_array[:, 0]), :][1]

    def summary(self):
        print("----------------------------")
        print("Flowrate is: %f" % self.flowrate)
        print("Pressure drop is %f Pa" % self.presure_drop)
        print("Total System Head Loss %f m" % self.head_loss)
        print("Power needed to overcome head it %f W" % self.power_out)
        print("error is")
        print(self.error)
        print("----------------------------")
        print("Friciton Factor List:")
        print(self.friction_factors_list)
        print("Velocity List")
        print(self.velocity_list)
        print("Reynolds List")
        print(self.re_list)
        print("Losses List")
        print(self.pipe_lost_list)

# ------------ Needed variables
# Subsystem = object of class subsystem. NOTE: The flowrate doesnt need to be correct here will guess regardless
# --- One of
# flowrate_array and head_array = np array containing flowrate and head values to be fitted
# ploynomial = array in the form np.array([x^2 coef, x coef, x^0 coef ])
# H(Q) = 3 Q^2 + 2Q + 3 np.array([3,2,3])

# ------------ Additional Tools
# Terms = number of terms used for poly fit
# number_pumps = number of pumps used
# char = pump arrangment either
#           S = Series
#           P = Parallel
# Other values = NPSH Coefficents

class pump_system:
    def __init__(self, Subsystem, flowrate_array =[], head_array=[], polynomial=False, Flowrate=False, terms=2,
                 number_pumps=1, Char=False, Z_i=0, H_fi=0 ,P_v=0, diameter_pump=1, n=1):
        self.subsystem = Subsystem
        self.x_array = flowrate_array
        self.y_array = head_array
        self.terms = terms
        # Parallel and series
        self.char = Char
        self.number_pumps = float(number_pumps)

        self.diameter = diameter_pump
        self.n = n
        self.poly_fit = self.get_poly_fit(polynomial)
        self.flowrate = self.get_flowrate(Flowrate)


        # NPSH
        self.z_i = Z_i
        self.h_fi = H_fi
        self.p_v = P_v
        self.summary()


    def get_poly_fit(self, polynomial):
        if polynomial != False:
            print("Using Given Poly")
            array = np.array(polynomial)
            array = array.astype(float)
            return np.poly1d(array)
        else:
            return np.poly1d(np.polyfit(self.x_array, self.y_array, self.terms))

    def get_flowrate(self, Flowrate):

        if self.char == "S":
            H_correction = self.number_pumps
            F_correction = 1
        if self.char == "P":
            H_correction = 1
            F_correction = 1/float(self.number_pumps)
        else:
            H_correction = 1
            F_correction = 1

        if Flowrate != False:
            return Flowrate
        else:
            print("Iterating to get Flowrate")
            system_array = np.array([])
            flowrate_array = np.array([])
            Q = 0.1
            while Q < 2:
                head_pump = self.poly_fit(Q * F_correction) * H_correction
                h_system = self.subsystem.get_head_friction(Q)
                system_array = np.append(system_array, [head_pump - h_system])
                flowrate_array = np.append(flowrate_array, Q)
                Q = Q + .1

            return np.roots(np.polyfit(flowrate_array, system_array, self.terms))

    def transform(self, d_new=False, n_new=False):
        if n_new == False:
            n_new = self.n
        if d_new == False:
            d_new = self.diameter
        self.y_array = self.y_array * (d_new/self.diameter)**2 * (n_new/self.n)**2
        self.x_array = self.x_array * (d_new/self.diameter)**3 * (n_new/self.n)
        self.poly_fit = self.get_poly_fit(False)
        self.flowrate = self.get_flowrate(False)

        self.summary()


    def summary(self):
        print("----------------------")
        print("Flowrate for the system in m^3 / s")
        print(self.flowrate)
        print("Polynomial Fit is:")
        print(self.poly_fit)

    def get_NPSH(self):
        return 101*10**3 / (self.subsystem.density * 9.81) - self.z_i - \
               self.h_fi - self.p_v / (self.subsystem.density * 9.81)

pipe_1 = Pipe(L=5, D=.1, Roughness=.00001, Minor_loss=1.06)
pipe_2 = Pipe(L=8, D=.2*2, Roughness=.00003, Minor_loss=4, Height=-10)
sub = Subsystem([pipe_1, pipe_2], Density=998, Vis=.001005)

# ------------- Questions
# ------ Test
pipe_1 = Pipe(L=200, D=.25, Roughness=.0001, Height=100, Minor_loss=.5)
pipe_2 = Pipe(L=400, D=.33, Roughness=.0001, Minor_loss=1)
sub = Subsystem([pipe_1, pipe_2], Density=998, Vis=1.001*10**(-3), Target=1)

ploynomial = [-1930, 0, 90]
pump = pump_system(sub, polynomial=ploynomial)

# get info for the flowrate
Subsystem([pipe_1, pipe_2], Density=998, Vis=1.001*10**(-3), Flowrate=0.16347582)

# for part b with floware = .11
Subsystem([pipe_1, pipe_2], Density=998, Vis=1.001*10**(-3), Flowrate=0.11)



# ----------- Advanced Pump system

















