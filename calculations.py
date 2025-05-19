import math
from math import pi, sqrt, sin, cos, atan, radians, degrees, tan

def create_table_headers():
    """Возвращает заголовки таблицы результатов"""
    return [
        'Номер участка',
        'Глубина по вертикали, м',
        'Длина ствола, м',
        'Длина интервала, м',
        'Смещение, м',
        'Зенитный угол, град.',
        'Интенсивность искривления, град./10м'
    ]

def create_vertical_section(Hv):
    """Создает данные для вертикального участка"""
    return {
        'section': 1,
        'vertical_depth': round(Hv, 2),
        'wellbore_length': round(Hv, 2),
        'interval_length': round(Hv, 2),
        'displacement': 0,
        'zenith_angle': 0,
        'curvature_rate': 0
    }

def create_angle_build_section(section_num, prev_depth, prev_length, R, angle, displacement, angle2, H, param=None):
    """Создает данные для участка набора угла"""
    interval_length = (pi * R * angle) / 180
    if param == '-':
        R = -R
    return {
        'section': section_num,
        'vertical_depth': round(H, 2),
        'wellbore_length': round(prev_length + interval_length, 2),
        'interval_length': round(interval_length, 2),
        'displacement': round(displacement, 2),
        'zenith_angle': round(angle2, 2),
        'curvature_rate': round(573 / R, 2)
    }

def create_tangent_section(section_num, prev_depth, prev_length, L, angle, displacement):
    """Создает данные для тангенциального участка"""
    return {
        'section': section_num,
        'vertical_depth': round(prev_depth + L * cos(radians(angle)), 2),
        'wellbore_length': round(prev_length + L, 2),
        'interval_length': round(L, 2),
        'displacement': round(displacement, 2),
        'zenith_angle': round(angle, 2),
        'curvature_rate': 0
    }

def create_extra_section(section_num, H_end, H, prev_length, A, calculation_type, angle=0):
    """Создает данные для дополнительного участка"""
    if calculation_type == 'angle_stabilization':
        interval_length = H_end - H
        new_displacement = A
        new_angle = 0
    else:  # curvature_preservation
        interval_length = (H_end - H) / cos(radians(angle))
        new_displacement = A + (H_end - H) * tan(radians(angle))
        new_angle = angle

    return {
        'section': section_num,
        'vertical_depth': round(H_end, 2),
        'wellbore_length': round(prev_length + interval_length, 2),
        'interval_length': round(interval_length, 2),
        'displacement': round(new_displacement, 2),
        'zenith_angle': round(new_angle, 2),
        'curvature_rate': 0
    }

def calculate_profile(H, A, Hv, R1, calculation_type='angle_stabilization', H_end=None):
    """Расчет параметров трехинтервального профиля скважины"""
    try:

        H0 = H - Hv
        discriminant = H0**2 - A*(2*R1 - A)
        if discriminant < 0:
            raise ValueError("Невозможно выполнить расчет: подкоренное выражение отрицательное")
        div_nul = 2*R1 - A
        if div_nul == 0:
            raise ValueError("Невозможно выполнить расчет: делитель равен нулю")
        alpha1 = 2 * degrees(atan((H0 - sqrt(discriminant))/div_nul))
        L = (A - R1*(1 - cos(radians(alpha1))))/sin(radians(alpha1))

        alpha1_rad = radians(alpha1)
        sin_alpha1 = sin(alpha1_rad)
        cos_alpha1 = cos(alpha1_rad)

        table_data = {
            'headers': create_table_headers(),
            'rows': [
                create_vertical_section(Hv),
                create_angle_build_section(2, Hv, Hv, R1, alpha1, 
                                        R1 * (1 - cos(radians(alpha1))), alpha1, H),
                create_tangent_section(3, Hv + R1 * sin(alpha1), 
                                     Hv + (pi * R1 * alpha1) / 180,
                                     L, alpha1, A)
            ]
        }
        table_data['rows'][1]['vertical_depth'] =  round(Hv + R1 * sin(radians(alpha1)), 2)
        table_data['rows'][2]['vertical_depth'] =  round(H, 2)

        if H_end and H_end > H:
            table_data['rows'].append(
                create_extra_section(4, H_end, H, 
                                   table_data['rows'][-1]['wellbore_length'],
                                   A, calculation_type, alpha1)
            )

        return {
            'alpha1': round(alpha1, 2),
            'alpha1_radians': round(alpha1, 4),
            'L': round(L, 2),
            'H0': round(H0, 2),
            'table_data': table_data,
            'input_data': {
                'H': H, 'A': A, 'Hv': Hv, 'R1': R1,
                'calculation_type': calculation_type, 'H_end': H_end
            },
            'sin_alpha1': round(sin_alpha1, 4), # Add sin(alpha1) result
            'cos_alpha1': round(cos_alpha1, 4) 
        }
    except Exception as e:
        return {
            'error': str(e),
            'input_data': {
                'H': H, 'A': A, 'Hv': Hv, 'R1': R1,
                'calculation_type': calculation_type, 'H_end': H_end
            }
        }

def calculate_four_interval_profile(H, A, Hv, R1, initial_angle, R2, calculation_type='angle_stabilization', H_end=None):
    """Расчет параметров четырехинтервального профиля скважины"""
    try:

        H_0 = H - Hv
        Q_1 = H_0 - R1 * sin(radians(initial_angle))
        B = R1 * (1 - cos(radians(initial_angle))) + Q_1 * tan(radians(initial_angle))
        A_1 = abs(A - B)
        C = Q_1 / cos(radians(initial_angle)) + A_1 * sin(radians(initial_angle))
        T = A_1 * cos(radians(initial_angle))
        KOR_expr = (C ** 2) + (T ** 2) - 2 * T * R2
        if KOR_expr < 0:
            raise ValueError(f'Подкоренное выражение отрицательно: {KOR_expr}')
        KOR = sqrt(KOR_expr)
        T_0 = (R2 * (R2 - T) + C * KOR) / ((R2 - T) ** 2 + C ** 2)
        ang_2 = 90 - degrees(atan(T_0 / sqrt(1 - T_0 ** 2))) + initial_angle
        H_ost = H_0 - R1 * sin(radians(initial_angle)) - R2 * (sin(radians(ang_2)) - sin(radians(initial_angle)))
        A_ost = A - R1 * (1 - cos(radians(initial_angle))) - R2 * (cos(radians(initial_angle)) - cos(radians(ang_2)))
        L_n = sqrt(H_ost ** 2 + A_ost ** 2)


        table_data = {
            'headers': create_table_headers(),
            'rows': [
                create_vertical_section(Hv),
                create_angle_build_section(2, Hv, Hv, R1, initial_angle,
                                        R1 * (1 - cos(radians(initial_angle))), initial_angle, Hv + R1 * sin(radians(initial_angle))),
                create_angle_build_section(3, 
                    Hv + R1 * sin(radians(initial_angle)),
                    Hv + (pi * R1 * initial_angle) / 180,
                    R2, ang_2 - initial_angle,
                    R1 * (1 - cos(radians(initial_angle))) + 
                    R2 * (cos(radians(initial_angle)) - cos(radians(ang_2))), ang_2, H),
                create_tangent_section(4,
                    Hv,
                    Hv + (pi * R1 * initial_angle) / 180 + (pi * R2 * (ang_2 - initial_angle)) / 180,
                    L_n, ang_2, A)
            ]
        }

        table_data['rows'][2]['vertical_depth'] =  round(Hv + R1 * sin(radians(initial_angle))  + R2 * (sin(radians(ang_2)) - sin(radians(initial_angle))), 2)
        table_data['rows'][3]['vertical_depth'] =  round(H, 2)

        if H_end and H_end > H:
            table_data['rows'].append(
                create_extra_section(5, H_end, H,
                                   table_data['rows'][-1]['wellbore_length'],
                                   A, calculation_type, ang_2)
            )

        return {
            'initial_angle_degrees': round(initial_angle, 2),
            'second_angle_degrees': round(ang_2, 2),
            'H_0': round(H_0, 2),
            'Q_1': round(Q_1, 2),
            'B': round(B, 2),
            'A1': round(A_1, 2),
            'C': round(C, 2),
            'T': round(T, 2),
            'ang_2': round(ang_2, 2),
            'T_0': round(T_0, 4),
            'L_n': round(L_n, 2),
            'table_data': table_data,
            'input_data': {
                'H': H, 'A': A, 'Hv': Hv, 'R1': R1,
                'initial_angle': initial_angle, 'R2': R2,
                'calculation_type': calculation_type, 'H_end': H_end
            },
            'H_ost': round(H_ost, 2),
            'A_ost': round(A_ost, 2)
        }
    except Exception as e:
        return {
            'error': str(e),
            'input_data': {
                'H': H, 'A': A, 'Hv': Hv, 'R1': R1,
                'initial_angle': initial_angle, 'R2': R2,
                'calculation_type': calculation_type, 'H_end': H_end
            }
        }

def calculate_j_shaped_profile(H, A, Hv, R1, initial_angle, R4, calculation_type='angle_stabilization', H_end=None):
    """Расчет параметров J-образного профиля скважины"""
    try:

        B = R1 * (1 - cos(radians(initial_angle))) + (H - Hv - R1 * sin(radians(initial_angle))) * tan(radians(initial_angle))
        Q = sqrt(2 * R4 * abs(A - B) * cos(radians(initial_angle)) - (A - B) ** 2 * (cos(radians(initial_angle)) ** 2))
        C = ((H - Hv - R1 * sin(radians(initial_angle))) / cos(radians(initial_angle))) + abs(A - B) * sin(radians(initial_angle))
        L = C - Q
        ang_p = initial_angle + degrees(atan(Q / sqrt(R4 ** 2 - Q ** 2)))

        
        table_data = {
            'headers': create_table_headers(),
            'rows': [
                create_vertical_section(Hv),
                create_angle_build_section(2, Hv, Hv, R1, initial_angle,
                                        R1 * (1 - cos(radians(initial_angle))), initial_angle, Hv + R1 * sin(radians(initial_angle))),
                create_tangent_section(3,
                    Hv + R1 * sin(radians(initial_angle)),
                    Hv + (pi * R1 * initial_angle) / 180,
                    L, initial_angle,
                    R1 * (1 - cos(radians(initial_angle))) + L * sin(radians(initial_angle))),
                create_angle_build_section(4,
                    H,
                    Hv + (pi * R1 * initial_angle) / 180 + L,
                    R4, ang_p - initial_angle, A, ang_p, H),
            ]
        }

        if H_end and H_end > H:
            table_data['rows'].append(
                create_extra_section(5, H_end, H,
                                   table_data['rows'][-1]['wellbore_length'],
                                   A, calculation_type, ang_p)
            )

        return {
            'initial_angle_degrees': round(initial_angle, 2),
            'ang_p_degrees': round(ang_p, 2),
            'L': round(L, 2),
            'B': round(B, 2),
            'Q': round(Q, 2),
            'C': round(C, 2),
            'table_data': table_data,
            'input_data': {
                'H': H, 'A': A, 'Hv': Hv, 'R1': R1,
                'initial_angle': initial_angle, 'R4': R4,
                'calculation_type': calculation_type, 'H_end': H_end
            },
          }
    except Exception as e:
        return {
            'error': str(e),
            'input_data': {
                'H': H, 'A': A, 'Hv': Hv, 'R1': R1,
                'initial_angle': initial_angle, 'R4': R4,
                'calculation_type': calculation_type, 'H_end': H_end
            }
        }

def calculate_s_shaped_profile(H, A, Hv, R1, initial_angle, R4, calculation_type='angle_stabilization', H_end=None):
    """Расчет параметров S-образного профиля скважины"""
    try:
        B = R1 * (1 - cos(radians(initial_angle))) + (H - Hv - R1 * sin(radians(initial_angle))) * tan(radians(initial_angle))
        Q = sqrt(2 * R4 * abs(A - B) * cos(radians(initial_angle)) - (A - B) ** 2 * (cos(radians(initial_angle)) ** 2))
        C = ((H - Hv - R1 * sin(radians(initial_angle))) / cos(radians(initial_angle))) + abs(A - B) * sin(radians(initial_angle))
        L = C - Q
        ang_p = initial_angle - degrees(atan(Q / sqrt(R4 ** 2 - Q ** 2)))

       
        table_data = {
            'headers': create_table_headers(),
            'rows': [
                create_vertical_section(Hv),
                create_angle_build_section(2, Hv, Hv, R1, initial_angle,
                                        R1 * (1 - cos(radians(initial_angle))), initial_angle, Hv + R1 * sin(radians(initial_angle))),
                create_tangent_section(3,
                    Hv + R1 * sin(radians(initial_angle)),
                    Hv + (pi * R1 * initial_angle) / 180,
                    L, initial_angle,
                    R1 * (1 - cos(radians(initial_angle))) + L * sin(radians(initial_angle))),
                create_angle_build_section(4,
                    H,
                    Hv + (pi * R1 * initial_angle) / 180 + L,
                    R4, -ang_p + initial_angle, A, ang_p, H, '-'),
            ]
        }

        if H_end and H_end > H:
            table_data['rows'].append(
                create_extra_section(5, H_end, H,
                                   table_data['rows'][-1]['wellbore_length'],
                                   A, calculation_type, ang_p)
            )

        return {
            'initial_angle_degrees': round(initial_angle, 2),
            'ang_p_degrees': round(ang_p, 2),
            'L': round(L, 2),
            'B': round(B, 2),
            'Q': round(Q, 2),
            'C': round(C, 2),
            'table_data': table_data,
            'input_data': {
                'H': H, 'A': A, 'Hv': Hv, 'R1': R1,
                'initial_angle': initial_angle, 'R4': R4,
                'calculation_type': calculation_type, 'H_end': H_end
            },
        }
    except Exception as e:
        return {
            'error': str(e),
            'input_data': {
                'H': H, 'A': A, 'Hv': Hv, 'R1': R1,
                'initial_angle': initial_angle, 'R4': R4,
                'calculation_type': calculation_type, 'H_end': H_end
            }
        }