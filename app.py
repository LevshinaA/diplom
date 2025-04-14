from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from calculations import calculate_profile
from database import init_db, save_calculation_results, get_calculation_results, get_all_calculations, delete_calculation
from openpyxl import Workbook
from datetime import datetime
import os

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
    return render_template('results.html', results=session['calculation_results'])

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = {
            'H': float(request.form['H']),      # Глубина скважины
            'A': float(request.form['A']),      # Смещение от вертикали
            'Hv': float(request.form['Hv']),    # Длина вертикального участка
            'R1': float(request.form['R1'])     # Радиус кривизны
        }
        
        # Выполняем расчеты
        results = calculate_profile(**data)
        
        # Сохраняем результаты в базу данных
        if 'error' not in results:
            # Получаем глубину и смещение из первой строки результатов
            first_row = results['table_data']['rows'][0]
            calculation_id = save_calculation_results(
                depth=first_row['vertical_depth'],
                displacement=first_row['displacement'],
                results=results['table_data']
            )
            results['calculation_id'] = calculation_id
        
        # Сохраняем результаты в сессии для отображения
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
        
        # Записываем заголовки
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)

        # Записываем данные
        for row_idx, row in enumerate(data['results']['rows'], 2):
            ws.cell(row=row_idx, column=1, value=row['section'])
            ws.cell(row=row_idx, column=2, value=row['vertical_depth'])
            ws.cell(row=row_idx, column=3, value=row['wellbore_length'])
            ws.cell(row=row_idx, column=4, value=row['interval_length'])
            ws.cell(row=row_idx, column=5, value=row['displacement'])
            ws.cell(row=row_idx, column=6, value=row['zenith_angle'])
            ws.cell(row=row_idx, column=7, value=row['curvature_rate'])

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