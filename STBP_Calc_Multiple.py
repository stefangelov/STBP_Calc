import xlwings as xl
from xlwings import Range
from datetime import datetime
from Lib import stbp_engine
from Lib.Cross_section import Concrete, Reinforcement, Forces

import os


# function for multiple sections
def multiple_sections():
    # set current time near to Calculate button to check when was last calculation
    date_now = datetime.now()
    Range('X4').value = date_now

    # take concrete things :)
    fck = Range('G3').value
    fcd = Range('G6').value
    fctd = Range('J6').value
    eps_cu = Range('G4').value

    concrete = Concrete(fck, fcd, fctd, eps_cu)

    # take reinforcement things :)
    fyd = Range('P6').value
    eps_ud = Range('P4').value
    iter0_long_reinf = Range('V2').value / 10  # covert in cm
    iter0_trans_reinf = Range('V3').value / 10  # convert in cm
    reinf_cover = Range('V4').value
    reinf_e_s_module = Range('S3').value

    reinforcement = Reinforcement(fyd, eps_ud, iter0_long_reinf,
                                  iter0_trans_reinf, reinf_cover,
                                  reinf_e_s_module)

    # get affected rows
    affected_rows = int(Range('Y6').value)

    for x in range(10, affected_rows):
        row_num = str(x + 1)
        # take force
        pressure = Range("F" + row_num).value if Range("F" + row_num).value != None else 0
        # check if pressure is > 0 add comment that it is not implement
        if pressure != 0:
            Range("F" + row_num).value = 'Not implemented!'

        bending = Range("C" + row_num).value
        shearing = Range("D" + row_num).value
        torsion = Range("E" + row_num).value

        forces = Forces(pressure, bending, shearing, torsion)

        # take dimensions of cross section
        cross_type = Range("I" + row_num).value
        hor_dim = Range("J" + row_num).value
        vert_dim = Range("L" + row_num).value

        # Create the cross-section and take necessary data
        calculated_cross_section = stbp_engine.create_func(forces, concrete,
                                                           reinforcement, cross_type,
                                                           (hor_dim, vert_dim))

        # TODO: if stbp_engine rice an exception handle it an show message in cell for Remarks

        the_reinforcement = calculated_cross_section.reinforcement_total()
        Range("N" + row_num).value = the_reinforcement[0]
        Range("O" + row_num).value = the_reinforcement[1]

        Range("P" + row_num).value = the_reinforcement[2]
        Range("Q" + row_num).value = the_reinforcement[5]

        Range("R" + row_num).value = the_reinforcement[3]
        Range("S" + row_num).value = the_reinforcement[4]
        Range("U" + row_num).value = the_reinforcement[6]


# needet for debuging when use xlwings
if __name__ == '__main__':
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'STBP_Calc.xlsm'))
    xl.Book.set_mock_caller(path)
    multiple_sections()