class Cross:
    def __init__(self, forces, concrete, reinforcement):
        self.forces = forces
        self.concrete = concrete
        self.reinforcement = reinforcement
        self.notes = []


class Circle(Cross):
    def __init__(self, forces, concrete, reinforcement, diameter):
        super().__init__(forces, concrete, reinforcement)
        self.diameter = diameter / 100 # covnert in meters


class Concrete:
    def __init__(self, fck, fcd, fctd, eps_cu):
        self.fck = fck
        self.fcd = fcd
        self.fctd = fctd
        self.eps_cu = eps_cu


class Reinforcement:
    def __init__(self, fyd, eps_ud, iter0_long_reinf, iter0_trans_reinf, cover, e_s_module):
        self.fyd = fyd
        self.eps_ud = eps_ud
        self.iter0_long_reinf = iter0_long_reinf / 100
        self.iter0_trans_reinf = iter0_trans_reinf / 100
        self.cover = cover / 100 # covnert in meter
        self.e_s_module = e_s_module


class Forces:
    def __init__(self, pressure, bending, shearing, torsion):

        if isinstance(pressure, ( int, float )):
            self.pressure = pressure / 1000 # convert in MN
        else:
            raise ValueError("\'{}\' is not number!".format(pressure))

        if isinstance(bending, ( int, float )):
            self.bending = bending / 1000 # convert in MN
        else:
            raise ValueError("\'{}\' is not number!".format(bending))

        if isinstance(shearing, ( int, float )):
             self.shearing = shearing / 1000 # convert in MN
        else:
            raise ValueError("\'{}\' is not number!".format(shearing))

        if isinstance(torsion, ( int, float )):
             self.torsion = torsion / 1000 # convert in MN
        else:
            raise ValueError("\'{}\' is not number!".format(torsion))