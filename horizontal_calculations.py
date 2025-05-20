from math import pi, sin, cos, radians, degrees, asin, sqrt, atan


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

def calc_four_int(H_h, A_h, ang_h, length_hor, radius_curve_2, radius_curve_3, zenith_angle, angle_3, type_ha, type_h, deviation_down, deviation_up, radius_curve):
    try:
        print(H_h, A_h, ang_h, length_hor, radius_curve_2, radius_curve_3, zenith_angle, angle_3, type_ha, type_h, deviation_down, deviation_up, radius_curve)
        W_4_h = sin(radians(angle_3)) - sin(radians(zenith_angle))
        W_5_h = sin(radians(ang_h)) - sin(radians(angle_3))
        V_4_h = cos(radians(zenith_angle)) - cos(radians(angle_3))
        V_5_h = cos(radians(angle_3)) - cos(radians(ang_h))
        R_r_h = (A_h - radius_curve_2 * (1 - cos(radians(zenith_angle))) - radius_curve_3 * V_4_h) / V_5_h
        Hb_h = H_h - radius_curve_2 * sin(radians(zenith_angle)) - radius_curve_3 * W_4_h - R_r_h * W_5_h

         
        table_data = {
            'headers': create_table_headers(),
            'rows': [
                {
                    'section': 1,
                    'vertical_depth': round(Hb_h, 2),
                    'wellbore_length': round(Hb_h, 2),
                    'interval_length': round(Hb_h, 2),
                    'displacement': 0,
                    'zenith_angle': 0,
                    'curvature_rate': 0
                },
                {
                    'section': 2,
                    'vertical_depth': round(Hb_h + radius_curve_2 * sin(radians(zenith_angle)), 2),
                    'wellbore_length': round((Hb_h + ((pi * radius_curve_2 * zenith_angle) / 180)), 2),
                    'interval_length': round(((pi * radius_curve_2 * zenith_angle) / 180), 2),
                    'displacement': round(radius_curve_2 * (1 - cos(radians(zenith_angle))), 2),
                    'zenith_angle': round(zenith_angle, 2),
                    'curvature_rate': round(573 / radius_curve_2, 2)
                },
                {
                    'section': 3,
                    'vertical_depth': round((Hb_h + radius_curve_2 * sin(radians(zenith_angle)) + radius_curve_3 * W_4_h), 2),
                    'wellbore_length': round(Hb_h + (pi * radius_curve_2 * zenith_angle) / 180 + (pi * radius_curve_3 * (angle_3 - zenith_angle)) / 180, 2),
                    'interval_length': round(((pi * radius_curve_3 * (angle_3 - zenith_angle)) / 180), 2),
                    'displacement': round(radius_curve_2 * (1 - cos(radians(zenith_angle)))  + radius_curve_3 * (cos(radians(zenith_angle)) - cos(radians(angle_3))), 2),
                    'zenith_angle': round(angle_3, 2),
                    'curvature_rate': round(573 / radius_curve_3, 2)
                },
                {
                    'section': 4,
                    'vertical_depth': round(H_h, 2),
                    'wellbore_length': round(Hb_h + (pi * radius_curve_2 * zenith_angle) / 180 + (pi * radius_curve_3 * (angle_3 - zenith_angle)) / 180 + (pi * R_r_h * (ang_h - angle_3)) / 180, 2),
                    'interval_length': round((pi * R_r_h * (ang_h - angle_3)) / 180, 2),
                    'displacement': round(A_h, 2),
                    'zenith_angle': round(ang_h, 2),
                    'curvature_rate': round(573 / R_r_h, 2)
                }
            ]
        }
        if type_h == 0:
            table_data['rows'].append(tand_section(5, H_h, A_h, ang_h, length_hor, type_ha, table_data['rows'][-1]['wellbore_length'], table_data['rows'][-1]['zenith_angle']))
        elif type_h == -1:
            table_data['rows'].append(
                downward_section(5, H_h, A_h, ang_h, length_hor, deviation_down, table_data['rows'][-1]['wellbore_length'])
            )
        elif type_h == 1:
            table_data['rows'].append(
                upward_section(5, H_h, A_h, ang_h, length_hor, deviation_up, table_data['rows'][-1]['wellbore_length'])
            )
        elif type_h == 2:
            table_data['rows'].extend(
                radius_curve_section(5, H_h, A_h, ang_h, length_hor, radius_curve, deviation_up, deviation_down, table_data['rows'][-1]['wellbore_length'], table_data['rows'][-1]['displacement'])
            )
        return {
            'Hb_h': round(Hb_h, 2),
            'V_4_h': round(V_4_h, 2),
            'V_5_h': round(V_5_h, 2),
            'W_5_h': round(W_4_h, 2),
            'W_4_h': round(W_5_h, 2),
            'R_r_h': round(R_r_h, 2),
            'input_data': {
                'H_h': H_h,
                'A_h': A_h,
                'ang_h': ang_h,
                'type_h': type_h
            },
            'table_data': table_data
        }
    except Exception as e:
        return {
            'error': str(e),
            'input_data': {
                'H_h': H_h,
                'A_h': A_h,
                'ang_h': ang_h,
                'type_h': type_h
            },
            'table_data': {}
        }

def calc_four_int_tangential(H_h, A_h, ang_h, length_hor, radius_curve_2, radius_curve_4, zenith_angle, type_ha, type_h, deviation_down, deviation_up, radius_curve):
    try:
        W_1_h = sin(radians(ang_h)) - sin(radians(zenith_angle))
        V_1_h = cos(radians(zenith_angle)) - cos(radians(ang_h))
        L_h = (A_h - (1 - cos(radians(zenith_angle))) * radius_curve_2 - radius_curve_4 * V_1_h) / sin(radians(zenith_angle))
        Hb_h = H_h - radius_curve_2 * sin(radians(zenith_angle)) - radius_curve_4 * W_1_h - L_h * cos(radians(zenith_angle))

        table_data = {
            'headers': create_table_headers(),
            'rows': [
                {
                    'section': 1,
                    'vertical_depth': round(Hb_h, 2),
                    'wellbore_length': round(Hb_h, 2),
                    'interval_length': round(Hb_h, 2),
                    'displacement': 0,
                    'zenith_angle': 0,
                    'curvature_rate': 0
                },
                {
                    'section': 2,
                    'vertical_depth': round(Hb_h + radius_curve_2 * sin(radians(zenith_angle)), 2),
                    'wellbore_length': round((Hb_h + (pi * radius_curve_2 * zenith_angle) / 180), 2),
                    'interval_length': round(((pi * radius_curve_2 * zenith_angle) / 180), 2),
                    'displacement': round(radius_curve_2 * (1 - cos(radians(zenith_angle))), 2),
                    'zenith_angle': round(zenith_angle, 2),
                    'curvature_rate': round(573 / radius_curve_2, 2)
                },
                {
                    'section': 3,
                    'vertical_depth': round((Hb_h + radius_curve_2 * sin(radians(zenith_angle)) + L_h * cos(radians(zenith_angle))), 2),
                    'wellbore_length': round(L_h + (Hb_h + (pi * radius_curve_2 * zenith_angle) / 180), 2),
                    'interval_length': round(L_h, 2),
                    'displacement': round(radius_curve_2 * (1 - cos(radians(zenith_angle))) + L_h * sin(radians(zenith_angle)), 2),
                    'zenith_angle': round(zenith_angle, 2),
                    'curvature_rate': 0
                },
                {
                    'section': 4,
                    'vertical_depth': round(H_h, 2),
                    'wellbore_length': round(L_h + (Hb_h + (pi * radius_curve_2 * zenith_angle) / 180) + (pi * radius_curve_4 * (ang_h - zenith_angle)) / 180, 2),
                    'interval_length': round((pi * radius_curve_4 * (ang_h - zenith_angle)) / 180, 2),
                    'displacement': round(A_h, 2),
                    'zenith_angle': round(ang_h, 2),
                    'curvature_rate': round(573 / radius_curve_4, 2)
                }
            ]
        }
        if type_h == 0:
            table_data['rows'].append(tand_section(5, H_h, A_h, ang_h, length_hor, type_ha, table_data['rows'][-1]['wellbore_length'], table_data['rows'][-1]['zenith_angle']))
        elif type_h == -1:
            table_data['rows'].append(
                downward_section(5, H_h, A_h, ang_h, length_hor, deviation_down, table_data['rows'][-1]['wellbore_length'])
            )
        elif type_h == 1:
            table_data['rows'].append(
                upward_section(5, H_h, A_h, ang_h, length_hor, deviation_up, table_data['rows'][-1]['wellbore_length'])
            )
        elif type_h == 2:
            table_data['rows'].extend(
                radius_curve_section(5, H_h, A_h, ang_h, length_hor, radius_curve, deviation_up, deviation_down, table_data['rows'][-1]['wellbore_length'], table_data['rows'][-1]['displacement'])
            )
        return {
            'Hb_h': round(Hb_h, 2),
            'W_1_h': round(W_1_h, 2),
            'L_h': round(L_h, 2),
            'V_1_h': round(V_1_h,2),
            'input_data': {
                'H_h': H_h,
                'A_h': A_h,
                'ang_h': ang_h,
                'type_h': type_h
            },
            'table_data': table_data
        }
    except Exception as e:
        return {
            'error': str(e),
            'input_data': {
                'H_h': H_h,
                'A_h': A_h,
                'ang_h': ang_h,
                'type_h': type_h
            },
            'table_data': {}
        }
        
def calc_five_int(H_h, A_h, ang_h, length_hor, radius_curve_2, radius_curve_4, radius_curve_5, zenith_angle, angle_4, type_ha, type_h, deviation_down, deviation_up, radius_curve):
    try:
        V_2_h = cos(radians(zenith_angle)) - cos(radians(angle_4))
        V_3_h = cos(radians(angle_4)) - cos(radians(ang_h))
        W_2_h = sin(radians(angle_4)) - sin(radians(zenith_angle))
        W_3_h = sin(radians(ang_h)) - sin(radians(angle_4))
        L_h = (A_h - (1 - cos(radians(zenith_angle))) * radius_curve_2 - radius_curve_4 * V_2_h - radius_curve_5 * V_3_h)/sin(radians(zenith_angle))
        Hb_h = H_h - radius_curve_2 * sin(radians(zenith_angle)) - radius_curve_4 * W_2_h - radius_curve_5 * W_3_h - L_h * cos(radians(zenith_angle))
         
        table_data = {
            'headers': create_table_headers(),
            'rows': [
                {
                    'section': 1,
                    'vertical_depth': round(Hb_h, 2),
                    'wellbore_length': round(Hb_h, 2),
                    'interval_length': round(Hb_h, 2),
                    'displacement': 0,
                    'zenith_angle': 0,
                    'curvature_rate': 0
                },
                {
                    'section': 2,
                    'vertical_depth': round(Hb_h + radius_curve_2 * sin(radians(zenith_angle)), 2),
                    'wellbore_length': round(Hb_h + (pi * radius_curve_2 * zenith_angle) / 180, 2),
                    'interval_length': round((pi * radius_curve_2 * zenith_angle) / 180, 2),
                    'displacement': round(radius_curve_2 * (1 - cos(radians(zenith_angle))), 2),
                    'zenith_angle': round(zenith_angle, 2),
                    'curvature_rate': round(573 / radius_curve_2, 2)
                },
                {
                    'section': 3,
                    'vertical_depth': round(Hb_h + radius_curve_2 * sin(radians(zenith_angle)) + L_h * cos(radians(zenith_angle)), 2),
                    'wellbore_length': round(L_h + Hb_h + (pi * radius_curve_2 * zenith_angle) / 180, 2),
                    'interval_length': round(L_h, 2),
                    'displacement': round(radius_curve_2 * (1 - cos(radians(zenith_angle))) + L_h * sin(radians(zenith_angle)), 2),
                    'zenith_angle': round(zenith_angle, 2),
                    'curvature_rate': 0
                },
                {
                    'section': 4,
                    'vertical_depth': round(Hb_h + radius_curve_2 * sin(radians(zenith_angle)) + L_h * cos(radians(zenith_angle)) + radius_curve_4 * W_2_h, 2),
                    'wellbore_length': round(L_h + Hb_h + (pi * radius_curve_2 * zenith_angle) / 180 + (pi * radius_curve_4 * (angle_4 - zenith_angle)) / 180, 2),
                    'interval_length': round(((pi * radius_curve_4 * (angle_4 - zenith_angle)) / 180), 2),
                    'displacement': round(radius_curve_2 * (1 - cos(radians(zenith_angle))) + L_h * sin(radians(zenith_angle)) + radius_curve_4 * (cos(radians(zenith_angle)) - cos(radians(angle_4))), 2),
                    'zenith_angle': round(angle_4, 2),
                    'curvature_rate': round(573 / radius_curve_4, 2)
                },
                {
                    'section': 5,
                    'vertical_depth': round(H_h, 2),
                    'wellbore_length': round(L_h + Hb_h + (pi * radius_curve_2 * zenith_angle) / 180 + (pi * radius_curve_4 * (angle_4 - zenith_angle)) / 180 + (pi * radius_curve_5 * (ang_h - angle_4)) / 180, 2),
                    'interval_length': round((pi * radius_curve_5 * (ang_h - angle_4)) / 180, 2),
                    'displacement': round(A_h, 2),
                    'zenith_angle': round(ang_h, 2),
                    'curvature_rate': round(573 / radius_curve_5, 2)
                }
            ]
        }
        if type_h == 0:
            table_data['rows'].append(tand_section(6, H_h, A_h, ang_h, length_hor, type_ha, table_data['rows'][-1]['wellbore_length'],  table_data['rows'][-1]['zenith_angle']))
        elif type_h == -1:
            table_data['rows'].append(
                downward_section(6, H_h, A_h, ang_h, length_hor, deviation_down, table_data['rows'][-1]['wellbore_length'])
            )
        elif type_h == 1:
            table_data['rows'].append(
                upward_section(6, H_h, A_h, ang_h, length_hor, deviation_up, table_data['rows'][-1]['wellbore_length'])
            )
        elif type_h == 2:
            table_data['rows'].extend(
                radius_curve_section(6, H_h, A_h, ang_h, length_hor, radius_curve, deviation_up, deviation_down, table_data['rows'][-1]['wellbore_length'], table_data['rows'][-1]['displacement'])
            )
        return {
            'Hb_h': round(Hb_h, 2),
            'V_2_h': round(V_2_h, 2),
            'W_3_h': round(W_3_h, 2),
            'V_3_h': round(V_3_h, 2),
            'W_2_h': round(W_2_h, 2),
            'L_h': round(L_h, 2),
            'input_data': {
                'H_h': H_h,
                'A_h': A_h,
                'ang_h': ang_h,
                'type_h': type_h
            },
            'table_data': table_data
        }
    except Exception as e:
        return {
            'error': str(e),
            'input_data': {
                'H_h': H_h,
                'A_h': A_h,
                'ang_h': ang_h,
                'type_h': type_h
            },
            'table_data': {}
        }

def calc_three_int(H_h, A_h, ang_h, length_hor, radius_curve_2, zenith_angle, type_ha, type_h, deviation_down, deviation_up, radius_curve):
    try:
        R_2_h = (A_h - radius_curve_2 * (1 - cos(radians(zenith_angle)))) / (cos(radians(zenith_angle)) - cos(radians(ang_h)))
        Hb_h = H_h - radius_curve_2 * sin(radians(zenith_angle)) - R_2_h * (sin(radians(ang_h)) - sin(radians(zenith_angle)))
        I_1_h = 573 / radius_curve_2
        I_2_h = 573 / R_2_h

        table_data = {
            'headers': create_table_headers(),
            'rows': [
                {
                    'section': 1,
                    'vertical_depth': round(Hb_h, 2),
                    'wellbore_length': round(Hb_h, 2),
                    'interval_length': round(Hb_h, 2),
                    'displacement': 0,
                    'zenith_angle': 0,
                    'curvature_rate': 0
                },
                {
                    'section': 2,
                    'vertical_depth': round(Hb_h + radius_curve_2 * sin(radians(zenith_angle)), 2),
                    'wellbore_length': round(Hb_h + (pi * radius_curve_2 * zenith_angle) / 180, 2),
                    'interval_length': round((pi * radius_curve_2 * zenith_angle) / 180, 2),
                    'displacement': round(radius_curve_2 *(1 - cos(radians(zenith_angle))), 2),
                    'zenith_angle': round(zenith_angle, 2),
                    'curvature_rate': round(I_1_h, 2)
                },
                {
                    'section': 3,
                    'vertical_depth': round(H_h, 2),
                    'wellbore_length': round(Hb_h + (pi * radius_curve_2 * zenith_angle) / 180 + (pi * R_2_h * (ang_h - zenith_angle)) / 180 , 2),
                    'interval_length': round((pi * R_2_h * (ang_h - zenith_angle) / 180), 2),
                    'displacement': round(A_h, 2),
                    'zenith_angle': round(ang_h, 2),
                    'curvature_rate': round(I_2_h, 2)
                }
            ]
        }
        if type_h == 0:
            table_data['rows'].append(tand_section(4, H_h, A_h, ang_h, length_hor, type_ha, table_data['rows'][-1]['wellbore_length'], table_data['rows'][-1]['zenith_angle']))
        elif type_h == -1:
            table_data['rows'].append(
                downward_section(4, H_h, A_h, ang_h, length_hor, deviation_down, table_data['rows'][-1]['wellbore_length'])
            )
        elif type_h == 1:
            table_data['rows'].append(
                upward_section(4, H_h, A_h, ang_h, length_hor, deviation_up, table_data['rows'][-1]['wellbore_length'])
            )
        elif type_h == 2:
            table_data['rows'].extend(
                radius_curve_section(4, H_h, A_h, ang_h, length_hor, radius_curve, deviation_up, deviation_down, table_data['rows'][-1]['wellbore_length'], table_data['rows'][-1]['displacement'])
            )
        return {
            'Hb_h': round(Hb_h, 2),
            'R_2_h': round(R_2_h, 2),
            'I_1_h': round(I_1_h, 2),
            'I_2_h': round(I_2_h, 2),
            'input_data': {
                'H_h': H_h,
                'A_h': A_h,
                'ang_h': ang_h,
                'type_h': type_h
            },
            'table_data': table_data
        }
    except Exception as e:
        return {
            'error': str(e),
            'input_data': {
                'H_h': H_h,
                'A_h': A_h,
                'ang_h': ang_h,
                'type_h': type_h
            },
            'table_data': {}
        }

def calc_two_int(H_h, A_h, ang_h, length_hor, type_ha, type_h, deviation_down, deviation_up, radius_curve):
    """
    Расчет параметров двухинтервального профиля горизонтальной скважины
    
    Args:
        H_h: глубина скважины
        A_h: смещение
        ang_h: угол
    
    Returns:
        dict: словарь с результатами расчета
    """
    try:
        # Основные расчеты
        Hb_h = H_h - ((A_h * sin(radians(ang_h)))/(1 - cos(radians(ang_h))))
        R_h = (H_h - Hb_h) / sin(radians(ang_h))
        I_h = 573 / R_h

        table_data = {
            'headers': create_table_headers(),
            'rows': [
                {
                    'section': 1,
                    'vertical_depth': round(Hb_h, 2),
                    'wellbore_length': round(Hb_h, 2),
                    'interval_length': round(Hb_h, 2),
                    'displacement': 0,
                    'zenith_angle': 0,
                    'curvature_rate': 0
                },
                {
                    'section': 2,
                    'vertical_depth': round(H_h, 2),
                    'wellbore_length': round(Hb_h + (pi * R_h * ang_h) / 180, 2),
                    'interval_length': round((pi * R_h * ang_h) / 180, 2),
                    'displacement': round(A_h, 2),
                    'zenith_angle': round(ang_h, 2),
                    'curvature_rate': round(I_h, 2)
                }
            ]
        }
        
        if type_h == 0:
            table_data['rows'].append(tand_section(3, H_h, A_h, ang_h, length_hor, type_ha, table_data['rows'][-1]['wellbore_length'], table_data['rows'][-1]['zenith_angle']))
        elif type_h == -1:
            table_data['rows'].append(
                downward_section(3, H_h, A_h, ang_h, length_hor, deviation_down, table_data['rows'][-1]['wellbore_length'])
            )
        elif type_h == 1:
            table_data['rows'].append(
                upward_section(3, H_h, A_h, ang_h, length_hor, deviation_up, table_data['rows'][-1]['wellbore_length'])
            )
        elif type_h == 2:
            table_data['rows'].extend(
                radius_curve_section(3, H_h, A_h, ang_h, length_hor, radius_curve, deviation_up, deviation_down, table_data['rows'][-1]['wellbore_length'], table_data['rows'][-1]['displacement'])
            )
        
        return {
            'Hb_h': round(Hb_h, 2),
            'R_h': round(R_h, 2),
            'I_h': round(I_h, 2),
            'input_data': {
                'H_h': H_h,
                'A_h': A_h,
                'ang_h': ang_h,
                'type_h': type_h
            },
            'table_data': table_data
        }
    except Exception as e:
        return {
            'error': str(e),
            'input_data': {
                'H_h': H_h,
                'A_h': A_h,
                'ang_h': ang_h,
                'type_h': type_h
            },
            'table_data': {}
        }

def tand_section(section_num, H, A, ang, lenght, well_type, prev_length, prev_ang):
    H_g_h = lenght * cos(radians(ang)) + H
    A_g_h = lenght * sin(radians(ang)) + A
    
    return {
        'section': section_num,
        'vertical_depth': round(H_g_h, 2),
        'wellbore_length': round(lenght + prev_length,2),
        'interval_length': lenght,
        'displacement': round(A_g_h, 2),
        'zenith_angle': round(prev_ang, 2),
        'curvature_rate': 0
    }

def downward_section(section_num, H_h, A_h, ang_h, length_hor, deviation_down, prev_length):
    R_g_h = (length_hor ** 2 + deviation_down ** 2) / (2 * deviation_down)
    ang_g_h = ang_h - degrees(asin(length_hor / R_g_h))
    L_g_h = (pi / 180) * (R_g_h * abs(ang_h - ang_g_h))
    H_g_h = length_hor * cos(radians(ang_h)) + deviation_down * sin(radians(ang_h)) + H_h
    A_g_h = length_hor * sin(radians(ang_g_h)) + deviation_down * cos(radians(ang_g_h)) + A_h

    return {
        'section': section_num,
        'vertical_depth': round(H_g_h, 2),
        'wellbore_length': round(L_g_h + prev_length, 2),
        'interval_length': round(L_g_h, 2),
        'displacement': round(A_g_h, 2),
        'zenith_angle': round(ang_g_h, 2),
        'curvature_rate': round(-573 / R_g_h, 2)
    }

def upward_section(section_num, H_h, A_h, ang_h, length_hor, deviation_up, prev_length):
    R_g_h = (length_hor ** 2 + deviation_up ** 2) / (2 * deviation_up)
    ang_g_h = ang_h + degrees(asin(length_hor / R_g_h))
    L_g_h = (pi / 180) * (R_g_h * abs(ang_h - ang_g_h))
    H_g_h = length_hor * cos(radians(ang_h)) - deviation_up * sin(radians(ang_h)) + H_h
    A_g_h = length_hor * sin(radians(ang_g_h)) - deviation_up * cos(radians(ang_g_h)) + A_h

    return {
        'section': section_num,
        'vertical_depth': round(H_g_h, 2),
        'wellbore_length': round(L_g_h + prev_length, 2),
        'interval_length': round(L_g_h, 2),
        'displacement': round(A_g_h, 2),
        'zenith_angle': round(ang_g_h, 2),
        'curvature_rate': round(573 / R_g_h, 2)
    }

def radius_curve_section(section_num, H_h, A_h, ang_h, length_hor, radius_curve, deviation_up, deviation_down, prev_length, prev_displacement):
    T = deviation_up + deviation_down
    B8 = (length_hor ** 2) - (T ** 2) + (deviation_up ** 2) - 2 * deviation_up * radius_curve
    M8 = B8 * deviation_down - 2 * (length_hor ** 2) * T
    Q8 = (length_hor ** 2) * (T ** 2) + B8 ** 2 / 4
    RRR = sqrt(M8 ** 2 - 4 * deviation_down ** 2 * Q8)
    R_B_D = (-M8 - RRR) / (2 * deviation_down ** 2)
    L3G1 = sqrt((radius_curve + R_B_D) * 2 * deviation_up - deviation_up ** 2)
    ZZ = L3G1 / (R_B_D+ radius_curve)
    AK1 = degrees(atan(ZZ / sqrt(1 - ZZ ** 2)))
    ang_A_B= AK1 + ang_h
    ang_B_C = ang_h
    YY = (length_hor - L3G1) / R_B_D
    DDDD = degrees(atan(YY / sqrt(1 - YY ** 2)))
    ang_C_D= ang_h - DDDD
    L_A_B = (pi / 180) * radius_curve * abs(ang_h - ang_A_B)
    L_B_C = (pi / 180) * R_B_D * abs(ang_h - ang_A_B)
    L_C_D = (pi / 180) * R_B_D * abs(ang_h - ang_C_D)
    A_A_B = radius_curve * (cos(radians(ang_h)) - cos(radians(ang_A_B)))
    A_C_D = A_h + length_hor
    A_C_D_1 = R_B_D * (cos(radians(ang_C_D)) - cos(radians(ang_B_C)))
    A_B_C = A_C_D - A_C_D_1
    H_A_B = radius_curve * (sin(radians(ang_h)) - sin(radians(ang_A_B)))
    H_B_D = H_h - deviation_up
    H_C_D = H_h + deviation_down
    return [
        {
            'section': 'A - B',
            'vertical_depth': round(H_h - H_A_B, 2),
            'wellbore_length': round(L_A_B + prev_length, 2),
            'interval_length': round(L_A_B, 2),
            'displacement': round(A_A_B + prev_displacement, 2),
            'zenith_angle': round(ang_A_B, 2),
            'curvature_rate': round(573 / radius_curve, 2)
        },
        {
            'section': 'B - C',
            'vertical_depth': round(H_B_D, 2),
            'wellbore_length': round(L_B_C + L_A_B + prev_length, 2),
            'interval_length': round(L_B_C, 2),
            'displacement': round(A_B_C, 2),
            'zenith_angle': round(ang_B_C, 2),
            'curvature_rate': round(-573 / R_B_D, 2)
        },
        {
            'section': 'C - D',
            'vertical_depth': round(H_C_D, 2),
            'wellbore_length': round(L_C_D + L_B_C + L_A_B + prev_length, 2),
            'interval_length': round(L_C_D, 2),
            'displacement': round(A_C_D, 2),
            'zenith_angle': round(ang_C_D, 2),
            'curvature_rate': round(-573 / R_B_D, 2)
        }
    ]