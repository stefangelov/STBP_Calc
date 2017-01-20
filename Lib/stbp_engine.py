from Lib.Cross_section import Circle
from Lib.rectangular_class import Rectangular

def create_func(forces, concrete, reinforcement, cross_type, dimensions):
    if cross_type == 'rec':
        return Rectangular(forces, concrete, reinforcement, dimensions[0], dimensions[1])

    elif cross_type == 'cir':
        return Circle(forces, concrete, reinforcement, dimensions[0])

    else:
        raise ValueError('The type of cross-section is not valid!')
