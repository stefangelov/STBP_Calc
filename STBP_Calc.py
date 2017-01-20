import xlwings as xl
from xlwings import Range
from datetime import datetime
from Lib import stbp_engine
from Lib.Cross_section import Concrete, Reinforcement, Forces

import os

def insert_value():
    # needet for xlwings work
    wb=xl.Book.caller()

    # hold sheet name
    the_sheet = 'STBP_Sheet'

    # set current time near to Calculate button to check when was last calculation
    date_now = datetime.now()
    Range('M26').value = date_now
    
    
    # take force
    pressure = Range('B5').value
    bending = Range('B6').value
    shearing = Range('B7').value
    torsion = Range('B8').value

    forces = Forces(pressure, bending, shearing, torsion)

    # take concrete things :)
    fck = Range('H6').value
    fcd = Range('H9').value
    fctd = Range('K9').value
    eps_cu = Range('H7').value

    concrete = Concrete(fck, fcd, fctd, eps_cu)

    # take reinforcement things :)
    fyd = Range('H16').value
    eps_ud = Range('H14').value
    iter0_long_reinf = Range('B18').value / 10 # covert in cm
    iter0_trans_reinf = Range('B19').value / 10 # convert in cm
    reinf_cover = Range('B16').value
    reinf_e_s_module = Range('K13').value

    reinforcement = Reinforcement(fyd, eps_ud, iter0_long_reinf,
                                  iter0_trans_reinf, reinf_cover,
                                  reinf_e_s_module)

    # take dimensions of cross section
    cross_type = Range('B13').value
    hor_dim = Range('B14').value
    vert_dim = Range('B15').value

    # Create the cross-section and take necessary data
    calculated_cross_section = stbp_engine.create_func(forces, concrete,
                                                       reinforcement, cross_type,
                                                       (hor_dim, vert_dim))

    #TODO: if stbp_engine rice an exception handle it an show message in cell for Remarks


    the_reinforcement = calculated_cross_section.reinforcement_total()
    Range('J19').value = the_reinforcement[0]
    Range('J20').value = the_reinforcement[1]

    Range('J22').value = the_reinforcement[2]
    Range('J23').value = the_reinforcement[5]

    Range('J26').value = the_reinforcement[3]
    Range('J27').value = the_reinforcement[4]
    Range('J28').value = the_reinforcement[6]


    #Insert notes if have any
    notes = ''
    for note in calculated_cross_section.notes:
        if len(notes) < 1:
            notes = note
        else:
            notes = notes + '; ' + note

    if len(notes) < 1:
        Range('P2').value = ''
    else:
        Range('P2').value = notes


    # insert 'not implemented' near to N Force and T Force because there isn't action for them yet
    Range('C5').value = ''
    Range('C8').value = ''
    if pressure != 0:
        Range('C5').value = 'Not implemented!'


# needet for debuging when use xlwings
if __name__ == '__main__':
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'STBP_Calc.xlsm'))
    xl.Book.set_mock_caller(path)
    insert_value()