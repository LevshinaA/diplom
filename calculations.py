import math
from math import pi, sqrt, sin, cos, atan, radians, degrees

def calculate_profile(H, A, Hv, R1):
    """
    Расчет параметров трехинтервального профиля скважины.
    
    Параметры:
    H  - глубина скважины (м)
    A  - смещение от вертикали (м)
    Hv - длина вертикального участка (м)
    R1 - радиус кривизны (м)
    
    Возвращает:
    dict: Словарь с результатами расчетов
    """
    try:
        # Расчет H0
        H0 = H - Hv
        
        # Расчет зенитного угла α1 по формуле (4)
        discriminant = H0**2 - 4*(2*R1 - A)
        if discriminant < 0:
            raise ValueError("Невозможно выполнить расчет: подкоренное выражение отрицательное")
        
        alpha1 = 2 * math.atan((H0 - math.sqrt(discriminant))/(2*R1 - A))
        alpha1_degrees = math.degrees(alpha1)
        
        # Расчет длины тангенциального участка L по формуле (5)
        L = (A - R1*(1 - math.cos(alpha1)))/math.sin(alpha1)

        # Расчет данных для таблицы
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
        
        return {
            'alpha1_degrees': round(alpha1_degrees, 2),
            'alpha1_radians': round(alpha1, 4),
            'L': round(L, 2),
            'H0': round(H0, 2),
            'table_data': table_data,
            'input_data': {
                'H': H,
                'A': A,
                'Hv': Hv,
                'R1': R1
            }
        }
        
    except Exception as e:
        # В случае ошибки возвращаем словарь с описанием ошибки
        return {
            'error': str(e),
            'input_data': {
                'H': H,
                'A': A,
                'Hv': Hv,
                'R1': R1
            }
        } 