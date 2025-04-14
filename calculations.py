import math
from math import pi, sqrt, sin, cos, atan, radians, degrees

def calculate_profile(H, A, Hv, R1, calculation_type='angle_stabilization', H_end=None):
    """
    Расчет параметров трехинтервального профиля скважины.
    
    Параметры:
    H  - глубина скважины (м)
    A  - смещение от вертикали (м)
    Hv - длина вертикального участка (м)
    R1 - радиус кривизны (м)
    calculation_type - тип расчета ('angle_stabilization' или 'curvature_preservation')
    H_end - конечная глубина для расчета дополнительного участка
    """
    try:
        H0 = H - Hv
        discriminant = H0**2 - A*(2*R1 - A)
        if discriminant < 0:
            raise ValueError("Невозможно выполнить расчет: подкоренное выражение отрицательное")
        
        alpha1 = 2 * math.atan((H0 - math.sqrt(discriminant))/(2*R1 - A))
        alpha1_degrees = math.degrees(alpha1)
        L = (A - R1*(1 - math.cos(alpha1)))/math.sin(alpha1)
        table_data = {
            'headers': [
                'Номер участка',
                'Глубина по вертикали, м',
                'Длина ствола, м',
                'Длина интервала, м',
                'Смещение, м',
                'Зенитный угол, град.',
                'Интенсивность искривления, град./10м'
            ],
            'rows': [
                # Участок 1 (вертикальный)
                {
                    'section': 1,
                    'vertical_depth': round(Hv, 2),
                    'wellbore_length': round(Hv, 2),
                    'interval_length': round(Hv, 2),
                    'displacement': 0,
                    'zenith_angle': 0,
                    'curvature_rate': 0
                },
                # Участок 2 (набор угла)
                {
                    'section': 2,
                    'vertical_depth': round(Hv + R1 * math.sin(alpha1), 2),
                    'wellbore_length': round(Hv + (pi * R1 * alpha1_degrees) / 180, 2),
                    'interval_length': round((pi * R1 * alpha1_degrees) / 180, 2),
                    'displacement': round(R1 * (1 - math.cos(alpha1)), 2),
                    'zenith_angle': round(alpha1_degrees, 2),
                    'curvature_rate': round(573 / R1, 2)
                },
                # Участок 3 (тангенциальный)
                {
                    'section': 3,
                    'vertical_depth': round(H, 2),
                    'wellbore_length': round(Hv + (pi * R1 * alpha1_degrees) / 180 + L, 2),
                    'interval_length': round(L, 2),
                    'displacement': round(A, 2),
                    'zenith_angle': round(alpha1_degrees, 2),
                    'curvature_rate': 0
                }
            ]
        }
        
        # Добавляем расчет дополнительного участка если задана конечная глубина
        if H_end and H_end > H:
            extra_section = {
                'section': 4,
                'vertical_depth': round(H_end, 2),
            }
            
            if calculation_type == 'angle_stabilization':
                extra_section.update({
                    'wellbore_length': round(wellbore_length + H_end - H, 2),
                    'interval_length': round(H_end - H, 2),
                    'displacement': round(A, 2),
                    'zenith_angle': 0,
                    'curvature_rate': 0
                })
            else:  # curvature_preservation
                extra_section.update({
                    'wellbore_length': round(wellbore_length + (H_end - H) / math.cos(alpha1), 2),
                    'interval_length': round((H_end - H) / math.cos(alpha1), 2),
                    'displacement': round(A + (H_end - H) * math.tan(alpha1), 2),
                    'zenith_angle': round(math.degrees(alpha1), 2),
                    'curvature_rate': 0
                })
            
            table_data['rows'].append(extra_section)
        
        return {
            'alpha1_degrees': round(math.degrees(alpha1), 2),
            'alpha1_radians': round(alpha1, 4),
            'L': round(L, 2),
            'H0': round(H0, 2),
            'table_data': table_data,
            'input_data': {
                'H': H,
                'A': A,
                'Hv': Hv,
                'R1': R1,
                'calculation_type': calculation_type,
                'H_end': H_end
            }
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'input_data': {
                'H': H,
                'A': A,
                'Hv': Hv,
                'R1': R1,
                'calculation_type': calculation_type,
                'H_end': H_end
            }
        }

def calculate_four_interval_profile(H, A, Hv, R1, initial_angle, R2, calculation_type='angle_stabilization', H_end=None):
    """
    Расчет параметров четырехинтервального профиля скважины.
    """
    try:
        # Основные расчеты
        H_0 = H - Hv
        Q_1 = H_0 - R1 * math.sin(math.radians(initial_angle))
        B = R1 * (1 - math.cos(math.radians(initial_angle))) + Q_1 * math.tan(math.radians(initial_angle))
        A_1 = abs(A - B)
        C = Q_1 / math.cos(math.radians(initial_angle)) + A_1 * math.sin(math.radians(initial_angle))
        T = A_1 * math.cos(math.radians(initial_angle))
        KOR = math.sqrt((C ** 2) + (T ** 2) - 2 * T * R2)
        T_0 = (R2 * (R2 - T) + C * KOR) / ((R2 - T) ** 2 + C ** 2)
        ang_2 = 90 - math.degrees(math.atan(T_0 / math.sqrt(1 - T_0 ** 2))) + initial_angle
        
        # Расчет остаточных параметров
        H_ost = H - Hv - R1 * math.sin(math.radians(initial_angle)) - R2 * (
                    math.sin(math.radians(ang_2)) - math.sin(math.radians(initial_angle)))
        A_ost = A - R1 * (1 - math.cos(math.radians(initial_angle))) - R2 * (
                    math.cos(math.radians(initial_angle)) - math.cos(math.radians(ang_2)))
        L = math.sqrt(H_ost ** 2 + A_ost ** 2)

        # Расчет значений для каждой ячейки согласно вашей схеме
        vertical_depths = [
            Hv,  # B2
            Hv + R1 * math.sin(math.radians(initial_angle)),  # B3
            Hv + R1 * math.sin(math.radians(initial_angle)) + R2 * (
                    math.sin(math.radians(ang_2)) - math.sin(math.radians(initial_angle))),  # B4
            H  # B5
        ]

        wellbore_lengths = [
            Hv,  # C2
            Hv + (math.pi * R1 * initial_angle) / 180,  # C3
            Hv + (math.pi * R1 * initial_angle) / 180 + (math.pi * R2 * (ang_2 - initial_angle)) / 180,  # C4
            Hv + (math.pi * R1 * initial_angle) / 180 + (math.pi * R2 * (ang_2 - initial_angle)) / 180 + L  # C5
        ]

        interval_lengths = [
            Hv,  # D2
            (math.pi * R1 * initial_angle) / 180,  # D3
            (math.pi * R2 * (ang_2 - initial_angle)) / 180,  # D4
            L  # D5
        ]

        displacements = [
            0,  # E2
            R1 * (1 - math.cos(math.radians(initial_angle))),  # E3
            R1 * (1 - math.cos(math.radians(initial_angle))) + R2 * (
                    math.cos(math.radians(initial_angle)) - math.cos(math.radians(ang_2))),  # E4
            A  # E5
        ]

        zenith_angles = [
            0,  # F2
            initial_angle,  # F3
            ang_2,  # F4
            ang_2  # F5
        ]

        curvature_rates = [
            0,  # G2
            573 / R1,  # G3
            573 / R2,  # G4
            0  # G5
        ]

        # Формируем таблицу результатов в том же формате, что и раньше
        table_data = {
            'headers': [
                'Номер участка',
                'Глубина по вертикали, м',
                'Длина ствола, м',
                'Длина интервала, м',
                'Смещение, м',
                'Зенитный угол, град.',
                'Интенсивность искривления, град./10м'
            ],
            'rows': []
        }

        # Заполняем данные для каждого участка
        for i in range(4):
            table_data['rows'].append({
                'section': i + 1,
                'vertical_depth': round(vertical_depths[i], 2),
                'wellbore_length': round(wellbore_lengths[i], 2),
                'interval_length': round(interval_lengths[i], 2),
                'displacement': round(displacements[i], 2),
                'zenith_angle': round(zenith_angles[i], 2),
                'curvature_rate': round(curvature_rates[i], 2)
            })
        
        # Добавляем расчет дополнительного участка если задана конечная глубина
        if H_end and H_end > H:
            extra_section = {
                'section': 5,
                'vertical_depth': round(H_end, 2),
            }
            
            if calculation_type == 'angle_stabilization':
                extra_section.update({
                    'wellbore_length': round(wellbore_lengths[-1] + H_end - H, 2),
                    'interval_length': round(H_end - H, 2),
                    'displacement': round(A, 2),
                    'zenith_angle': 0,
                    'curvature_rate': 0
                })
            else:  # curvature_preservation
                extra_section.update({
                    'wellbore_length': round(wellbore_lengths[-1] + (H_end - H) / math.cos(math.radians(ang_2)), 2),
                    'interval_length': round((H_end - H) / math.cos(math.radians(ang_2)), 2),
                    'displacement': round(A + (H_end - H) * math.tan(math.radians(ang_2)), 2),
                    'zenith_angle': round(ang_2, 2),
                    'curvature_rate': 0
                })
            
            table_data['rows'].append(extra_section)
        
        return {
            'initial_angle_degrees': round(initial_angle, 2),
            'second_angle_degrees': round(ang_2, 2),
            'L': round(L, 2),
            'H0': round(H_0, 2),
            'Q1': round(Q_1, 2),
            'B': round(B, 2),
            'A1': round(A_1, 2),
            'C': round(C, 2),
            'T': round(T, 2),
            'KOR': round(KOR, 2),
            'T0': round(T_0, 2),
            'H_ost': round(H_ost, 2),
            'A_ost': round(A_ost, 2),
            'table_data': table_data,
            'excel_format': {
                'vertical_depths': [round(x, 2) for x in vertical_depths],
                'wellbore_lengths': [round(x, 2) for x in wellbore_lengths],
                'interval_lengths': [round(x, 2) for x in interval_lengths],
                'displacements': [round(x, 2) for x in displacements],
                'zenith_angles': [round(x, 2) for x in zenith_angles],
                'curvature_rates': [round(x, 2) for x in curvature_rates]
            },
            'input_data': {
                'H': H,
                'A': A,
                'Hv': Hv,
                'R1': R1,
                'initial_angle': initial_angle,
                'R2': R2,
                'calculation_type': calculation_type,
                'H_end': H_end
            }
        }
    except Exception as e:
        return {
            'error': str(e),
            'input_data': {
                'H': H,
                'A': A,
                'Hv': Hv,
                'R1': R1,
                'initial_angle': initial_angle,
                'R2': R2,
                'calculation_type': calculation_type,
                'H_end': H_end
            }
        } 