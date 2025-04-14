from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from calculations import calculate_profile, calculate_four_interval_profile, calculate_j_shaped_profile, calculate_s_shaped_profile
from database import init_db, save_calculation_results, get_calculation_results, get_all_calculations, delete_calculation
from openpyxl import Workbook
from datetime import datetime
import os
from math import pi, sqrt, sin, cos, atan, radians, degrees, tan

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Необходимо для использования session

# Инициализируем базу данных при запуске
init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculation')
def calculation():
    return render_template('calculation.html')

@app.route('/history')
def history():
    calculations = get_all_calculations()
    return render_template('history.html', calculations=calculations)

@app.route('/results')
def results():
    if 'calculation_results' not in session:
        return redirect(url_for('calculation'))
    
    results = session['calculation_results']
    # Добавляем тип профиля к результатам
    results['profile_type'] = 2 if 'initial_angle_degrees' in results else 1
    
    return render_template('results.html', results=results)

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        print("Form data:", dict(request.form))  # Отладочный вывод
        
        # Базовые параметры
        data = {
            'H': float(request.form['H']),
            'A': float(request.form['A']),
            'Hv': float(request.form['Hv']),
            'R1': float(request.form['R1']),
            'calculation_type': request.form.get('calculation_type', 'angle_stabilization'),
            'H_end': float(request.form.get('H_end', 0)) or None
        }
        
        # Получаем тип профиля как число
        profile_type = int(request.form.get('profile_type', 1))
        print("Profile type:", profile_type)  # Отладочный вывод
        
        if profile_type in [3, 4]:  # J-образный или S-образный
            # Добавляем параметры для J/S-образного профиля
            data.update({
                'initial_angle': float(request.form['initial_angle']),
                'R2': float(request.form['R2']),
                'R4': float(request.form['R4'])
            })
            if profile_type == 3:
                results = calculate_j_shaped_profile(**data)
            else:
                results = calculate_s_shaped_profile(**data)
        elif profile_type == 2:  # Четырехинтервальный
            data.update({
                'initial_angle': float(request.form['initial_angle']),
                'R2': float(request.form['R2'])
            })
            results = calculate_four_interval_profile(**data)
        else:  # Трехинтервальный
            results = calculate_profile(**data)
        
        # Сохраняем результаты в базу данных
        if 'error' not in results:
            calculation_id = save_calculation_results(
                depth=data['H'],
                profile_type=profile_type,
                results=results['table_data']
            )
            results['calculation_id'] = calculation_id
            results['profile_type'] = profile_type
        
        session['calculation_results'] = results
        
    except ValueError as e:
        session['calculation_results'] = {
            'error': f'Ошибка в введенных данных: {str(e)}',
            'input_data': request.form
        }
    except Exception as e:
        session['calculation_results'] = {
            'error': f'Ошибка при выполнении расчета: {str(e)}',
            'input_data': request.form
        }
    
    return redirect(url_for('results'))

@app.route('/get_calculation_data/<int:calculation_id>')
def get_calculation_data(calculation_id):
    try:
        data = get_calculation_results(calculation_id)
        if data is None:
            return jsonify({'error': 'Расчет не найден'})
        
        # Преобразуем результаты в нужный формат
        return jsonify({
            'headers': [
                'Номер участка',
                'Глубина по вертикали, м',
                'Длина ствола, м',
                'Длина интервала, м',
                'Смещение, м',
                'Зенитный угол, град.',
                'Интенсивность искривления, град./10м'
            ],
            'rows': data['results']['rows']
        })
    except Exception as e:
        print(f"Ошибка при получении данных расчета: {str(e)}")
        return jsonify({'error': str(e)})

@app.route('/delete_calculation/<int:calculation_id>', methods=['DELETE'])
def delete_calculation_route(calculation_id):
    try:
        delete_calculation(calculation_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download_excel/<int:calculation_id>')
def download_excel(calculation_id):
    try:
        data = get_calculation_results(calculation_id)
        if data is None:
            return jsonify({'error': 'Расчет не найден'}), 404

        # Создаем новую книгу Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Результаты расчета"

        # Заголовки таблицы
        headers = [
            'Номер участка',
            'Глубина по вертикали, м',
            'Длина ствола, м',
            'Длина интервала, м',
            'Смещение, м',
            'Зенитный угол, град.',
            'Интенсивность искривления, град./10м'
        ]
        
        # Записываем заголовки в первую строку
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)

        # Записываем данные точно так же, как в вашем коде
        for row in range(4):
            row_data = data['results']['rows'][row]
            ws.cell(row=row+2, column=1, value=row_data['section'])
            ws.cell(row=row+2, column=2, value=row_data['vertical_depth'])
            ws.cell(row=row+2, column=3, value=row_data['wellbore_length'])
            ws.cell(row=row+2, column=4, value=row_data['interval_length'])
            ws.cell(row=row+2, column=5, value=row_data['displacement'])
            ws.cell(row=row+2, column=6, value=row_data['zenith_angle'])
            ws.cell(row=row+2, column=7, value=row_data['curvature_rate'])

        # Настраиваем ширину столбцов
        for col in range(1, len(headers) + 1):
            ws.column_dimensions[chr(64 + col)].width = 20

        # Сохраняем файл
        filename = f"calculation_{calculation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join('temp', filename)
        
        # Создаем временную директорию, если её нет
        if not os.path.exists('temp'):
            os.makedirs('temp')
            
        wb.save(filepath)

        # Отправляем файл
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        print(f"Ошибка при создании Excel файла: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 