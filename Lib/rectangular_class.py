from Lib.Cross_section import Cross
import math

class Rectangular(Cross):
    def __init__(self, forces, concrete, reinforcement, side_b, side_h):
        super().__init__(forces, concrete, reinforcement)
        self.side_b = side_b / 100 # convert in meter
        self.side_h = side_h / 100 # convert in meter

    def __longit_reinf_quantity_bending(self):
        d = self.side_h - self.reinforcement.cover - self.reinforcement.iter0_long_reinf / 2
        x = self.concrete.eps_cu / ( self.concrete.eps_cu + self.reinforcement.eps_ud ) * d
        f_c = 0.8 * x * self.side_b * self.concrete.fcd
        z = d - 0.4 * x

        # moment load capacity - destruction of both sides
        m_ab_rd = f_c * z

        if m_ab_rd > self.forces.bending:

            f_s_1 = self.forces.bending / z # force in reinforcement

            a_s_1 = f_s_1 / self.reinforcement.fyd * 10000 # quantity of reinforcement in cm2

            return (a_s_1, 0)

        else:
            new_x = self.__find_new_h_compression_zone(d)
            x_lim = 0.45 * d

            if 0 < new_x < x_lim:
                e_s_1 = self.concrete.eps_cu * ( d - new_x ) / new_x
                f_s_1 = 0.8 * self.side_b * new_x * self.concrete.fcd

                if e_s_1 >= self.reinforcement.fyd / self.reinforcement.e_s_module:
                    a_s_1 = f_s_1 / self.reinforcement.fyd * 10000
                    return (a_s_1, 0)
                else:
                    a_s_1 = f_s_1 / e_s_1 * self.reinforcement.e_s_module
                    return (a_s_1, 0)
            elif new_x > 0:
                # Bending moment can bearing with x_lim
                m_clim = 0.8 * self.side_b * x_lim * self.concrete.fcd * ( d - 0.4 * x_lim )

                # compression reinforcement for bending bearing capacity
                m_delta = self.forces.bending - m_clim

                # distance form out edge to axis of compression reinforcement
                d_2 = self.reinforcement.iter0_long_reinf / 2 + self.reinforcement.cover

                f_s_2 = m_delta / ( d - d_2 )
                eps_s_2 = (( x_lim - d_2 ) / x_lim ) * self.concrete.eps_cu


                # search stress in compresed zone
                if eps_s_2 >= self.reinforcement.fyd / self.reinforcement.e_s_module:
                    sigma_s_2 = self.reinforcement.fyd
                else:
                    sigma_s_2 = eps_s_2 * self.reinforcement.e_s_module

                # area of compresed reinforcement
                a_s_2 = f_s_2 / sigma_s_2 * 10000

            else:
                a_s_2 = "No"

            # now we calculate tension reinforcement - a_s_1
            if new_x < 0:
                a_s_1 = "No"
            else:
                f_clim = 0.8 * self.side_b * x_lim * self.concrete.fcd
                f_s_1 = f_clim + f_s_2
                a_s_1 = f_s_1 / self.reinforcement.fyd * 10000

            return (a_s_1, a_s_2)

    # Reinforcement for Shearing
    def __cross_v_reinf_quantity(self, longit_reinf_quantity_bending):
        if longit_reinf_quantity_bending[0] == 'No' or longit_reinf_quantity_bending[1] == 'No':
            return ('No', 'No')

        d = self.side_h - self.reinforcement.cover - self.reinforcement.iter0_long_reinf / 2

        k = 1 + math.sqrt( 200 / d / 1000 )
        if k > 2.0:
            k = 2.0
            self.notes.append('Set \'k\'=2')

        bw = self.side_b

        a_sl = self.__longit_reinf_quantity_bending()[0]

        ro_l = a_sl / bw / d / 1000 / 1000 * 100 # / 1000 / 1000 - bw and d in mm; * 100 a_s1 in mm2
        if ro_l > 0.02:
            raise ValueError('ro_l for v_rd_ct is FAIL!')

        sigma_cp = self.forces.pressure / self.side_b / self.side_h
        if sigma_cp > 0.2 * self.concrete.fcd:
            raise ValueError('sigma_cp for v_rd_ct is FAIL!')

        v_rd_ct = self.__find_v_rd_ct()

        if v_rd_ct > self.forces.shearing * 1000:
            cross_v_reinf_result = 0
        else:
            z = 0.9 * ( self.side_h - self.reinforcement.cover - self.reinforcement.iter0_long_reinf / 2 )
            v = self.__find_v()
            alpha_cw = self.__find_alpha_cw()

            k1 = self.__find_k1(alpha_cw, bw, z, v)
            if k1 >= 2.9:
                cross_v_reinf_result = self.forces.shearing / ( 2.5 * z * self.reinforcement.fyd ) * 10000

            elif k1 >= 2.0:
                cot_titha = self.__find_cot_titha(k1)
                cross_v_reinf_result = self.forces.shearing / ( z * self.reinforcement.fyd * cot_titha ) * 10000

            else:
                cross_v_reinf_result = 'No'

        # find longitudinal reinforcement from shear force
        longit_reinf_from_shear_force = 0

        if self.forces.shearing > 0:
            z = 0.9 * ( self.side_h - self.reinforcement.cover - self.reinforcement.iter0_long_reinf / 2 )
            v = 0.6 * ( 1 - self.concrete.fck / 250 )
            alpha_cw = 1 # there is NO prestressing

            cot_titha = 0

            def find_longit_reinf_from_shear_force(cot_titha):
                delta_f_t_d = 0.5 * self.forces.shearing * (cot_titha - alpha_cw)
                longit_reinf_from_shear_force = delta_f_t_d / self.reinforcement.fyd * 10000
                return longit_reinf_from_shear_force

            k1 = self.__find_k1(alpha_cw, bw, z, v)
            if k1 >= 2.9:
                cot_titha = self.__find_cot_titha(k1)
                longit_reinf_from_shear_force = find_longit_reinf_from_shear_force(cot_titha)

            elif k1 >= 2.0:
                cot_titha = self.__find_cot_titha(k1)
                longit_reinf_from_shear_force = find_longit_reinf_from_shear_force(cot_titha)
            else:
                longit_reinf_from_shear_force = 0

        return (cross_v_reinf_result, longit_reinf_from_shear_force)

    # reinforcement for Torsion
    def __reinf_for_tosion(self):
        if self.forces.shearing > 0:
            t_ef = self.__find_t_ef()
            a_k = self.__find_a_k(t_ef)
            tao_t = self.__find_tao_t(a_k, t_ef)
            v = self.__find_v()
            alpha_cw = self.__find_alpha_cw()
            z = 0.9 * ( self.side_h - self.reinforcement.cover - self.reinforcement.iter0_long_reinf / 2 )
            bw = self.side_b
            k1 = self.__find_k1(alpha_cw, bw, z, v)
            titha_angle = 0

            a_sw_t = 0 # cross
            a_st_h = 0 # longitudinal -> side h
            a_st_b = 0 # longitudinal -> side b

            if k1 < 2:
                pass
                # t0d0: Deside what to do if can't bearing the shear force
                # slove this problem in reinforcement_total(self)
            else:
                titha_angle = math.atan( 1 / self.__find_cot_titha(k1))

                t_rd_max = 2 * v * alpha_cw * self.concrete.fcd * t_ef * a_k * math.sin(titha_angle) * math.cos(titha_angle)
                t_rd_max *= 1000

                t_rd_c = self.concrete.fctd * t_ef * 2 * a_k
                t_rd_c *= 1000

                v_rd_max = ( alpha_cw * self.side_b * z * v * self.concrete.fcd ) / ( math.tan(titha_angle) + 1 / ( math.tan(titha_angle) ) )
                v_rd_max *= 1000

                v_rd_c = self.__find_v_rd_ct()

                if ( self.forces.torsion * 1000 / t_rd_c + self.forces.shearing * 1000 / v_rd_c ) <= 1:
                    return (0, 0, 0)
                elif ( self.forces.torsion * 1000 / t_rd_max + self.forces.shearing * 1000 / v_rd_max ) <= 1:
                    # find cross reinforcement
                    a_sw_t = self.forces.torsion / ( 2 * a_k * self.reinforcement.fyd * self.__find_cot_titha(k1)) * 10000

                    # find long by side b reinforcement
                    a_st_b = self.forces.torsion * self.__find_cot_titha(k1) * ( self.side_b - t_ef ) / ( 2 *a_k * self.reinforcement.fyd ) * 10000

                    # find long by side h reinforcement
                    a_st_h = self.forces.torsion * self.__find_cot_titha(k1) * ( self.side_h - t_ef ) / ( 2 *a_k * self.reinforcement.fyd ) * 10000

                    return (a_sw_t, a_st_b, a_st_h)
                else:
                    return ("No", "No", "No")

        else:
            # Think about: Is possible to have Torsion Withoud Shear force
            # If You deside to do Torsiion Withoud Shear force
            # Find titha_angle and e.t.
            pass


    # presstresed form torsion force
    def __find_tao_t(self, a_k, t_ef):
        return self.forces.torsion / ( 2 * a_k * t_ef )

    # find area closed form midle of sides of conditinal cross-section
    def __find_a_k(self, t_ef):
        return ( (self.side_b) - t_ef ) * ( (self.side_h) - t_ef)

    # find shickness of wall of conditinal cross-section
    def __find_t_ef(self):
        round_cross_u = self.side_b * 2 + self.side_h * 2
        area_cross_capital_a = self.side_b * self.side_h
        italic_a = self.reinforcement.cover + self.reinforcement.iter0_long_reinf / 2

        t_ef = 0
        italic_a_mulipl_two = italic_a * 2
        area_devided_round = area_cross_capital_a / round_cross_u

        if area_devided_round >= italic_a_mulipl_two:
            t_ef = area_devided_round
        else:
            t_ef = italic_a_mulipl_two

        return t_ef

    # return collect during the calculation notes
    def note(self):
        return self.notes


    # k for shearing calculation
    def __find_k1(self, alpha_cw, bw, z, v):
        k1 = ( alpha_cw * bw * z * v * self.concrete.fcd ) / self.forces.shearing
        return k1

    # angle titha for shearing calculations
    def __find_cot_titha(self, k1):
        if k1 >= 2.9:
            return 2.5
        elif k1 >= 2:
            return k1 / 2 + math.sqrt(k1 ** 2 - 4) / 2
        else:
            raise ValueError("Гърми к1 най вероятно")

    def __find_v(self):
        return 0.6 * ( 1 - self.concrete.fck / 250 )

    def __find_alpha_cw(self):
        # there is no prestressing
        return 1

    # for longitude reinforcement calculation
    # Solving quadratic
    def __find_new_h_compression_zone(self, d):
        # ' d ' is the useful height
        # a * x2 + b * x + c = 0
        a = 0.32 * self.side_b * self.concrete.fcd
        b = -0.8 * self.side_b * d * self.concrete.fcd
        c = self.forces.bending

        # determinatn
        determ = ( b**2 ) - 4 * a * c

        # if determ is negative the cross-section hasn't enough bearin capacity
        if determ < 0:
            return -1

        # the solutions
        p = math.sqrt(determ)
        sol_1 = ( -b - math.sqrt(determ) ) / ( 2 * a )
        sol_2 = ( -b + math.sqrt(determ) ) / ( 2 * a )

        if sol_1 > 0 and sol_1 < d:
            return sol_1
        elif sol_2 > 0 and sol_2 < d:
            return sol_2
        else:
            #TODO: Deside what to do with this when take mean the pressure force
            if self.forces.pressure == 0:
                return -1

    # Find max shear capacity of the cross-section
    def __find_v_rd_ct (self):

        a_sl = self.__longit_reinf_quantity_bending()[0]

        if isinstance(a_sl, float):

            d = self.side_h - self.reinforcement.cover - self.reinforcement.iter0_long_reinf / 2

            k = 1 + math.sqrt( 200 / d / 1000 )
            if k > 2.0:
                k = 2.0
                self.notes.append('Set \'k\'=2')

            b_w = self.side_b

            ro_l = a_sl / b_w / d / 1000 / 1000 * 100 # / 1000 / 1000 - bw and d in mm; * 100 a_s1 in mm2
            if ro_l > 0.02:
                raise ValueError('ro_l for v_rd_ct is FAIL!')

            sigma_cp = self.forces.pressure / self.side_b / self.side_h
            if sigma_cp > 0.2 * self.concrete.fcd:
                raise ValueError('sigma_cp for v_rd_ct is FAIL!')

            v_rd_ct_first = ( 0.12 * k * ( ( 100 * ro_l * self.concrete.fck ) ** ( 1 / 3 ) ) + 0.15 * sigma_cp ) * b_w * d
            v_rd_ct_first *= 1000

            v_rd_ct_second = ( 0.035 * math.sqrt( k ** 3 ) * math.sqrt(self.concrete.fck)  + 0.15 * sigma_cp ) * b_w * d
            v_rd_ct_second *= 1000

            return  max(v_rd_ct_first, v_rd_ct_second)

    #return reinforcement
    def reinforcement_total(self):
        longitude_bending = self.__longit_reinf_quantity_bending()
        if longitude_bending[0] == 'No' or longitude_bending[1] == 'No':
            return ('Insufficient bearing capacity for BENDING', 'Insufficient bearing capacity for BENDING',
                'Insufficient bearing capacity for BENDING',
                'Insufficient bearing capacity for BENDING', 'Insufficient bearing capacity for BENDING',
                'Insufficient bearing capacity for BENDING', 'Insufficient bearing capacity for BENDING')

        cross_shear = self.__cross_v_reinf_quantity(longitude_bending)
        if cross_shear[0] == 'No' or cross_shear[1] == 'No':
            return ('Insufficient bearing capacity for shear force', 'Insufficient bearing capacity for shear force',
            'Insufficient bearing capacity for SHEAR force',
            'Insufficient bearing capacity for SHEAR force', 'Insufficient bearing capacity for SHEAR force',
            'Insufficient bearing capacity for SHEAR force', 'Insufficient bearing capacity for SHEAR force')

        if self.forces.shearing == 0:
            return (longitude_bending[0], longitude_bending[1],
                0,
                0, 0,
                0, 0)

        else:
            torsion_reinforcement = self.__reinf_for_tosion()
            if torsion_reinforcement[0] == 'No' or torsion_reinforcement[1] == 'No' or torsion_reinforcement[2] == 'No':
                return ('Insufficient bearing capacity for TORSION force', 'Insufficient bearing capacity for TORSION force',
                'Insufficient bearing capacity for TORSION force',
                'Insufficient bearing capacity for TORSION force', 'Insufficient bearing capacity for TORSION force',
                'Insufficient bearing capacity for TORSION force', 'Insufficient bearing capacity for TORSION force')

            else:
                return (longitude_bending[0], longitude_bending[1],
                    cross_shear[1],
                    torsion_reinforcement[1], torsion_reinforcement[2],
                    cross_shear[0], torsion_reinforcement[0])