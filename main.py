from flask import Flask, render_template, request, redirect, url_for, jsonify, session

app = Flask(__name__)
app.secret_key = 'secret_key'  # Ключ для безопасности сессий

districts = {
    'Центральный': ['Москва', 'Московская область', 'Тульская область', 'Рязанская область', 'Владимирская область', 'Ивановская область', 'Костромская область', 'Ярославская область', 'Тверская область', 'Смоленская область', 'Брянская область', 'Калужская область'],
    'Северо-Западный': ['Санкт-Петербург', 'Ленинградская область', 'Новгородская область', 'Псковская область', 'Карелия', 'Архангельская область', 'Мурманская область', 'Вологодская область', 'Коми'],
    'Южный': ['Краснодарский край', 'Ростовская область', 'Волгоградская область', 'Астраханская область', 'Воронежская область', 'Белгородская область', 'Курская область', 'Липецкая область', 'Тамбовская область'],
    'Северо-Кавказский': ['Ставропольский край', 'Ростовская область', 'Дагестан', 'Ингушетия', 'Кабардино-Балкария', 'Карачаево-Черкесия', 'Северная Осетия', 'Чечня'],
    'Приволжский': ['Татарстан', 'Башкортостан', 'Удмуртия', 'Марий Эл', 'Чувашия', 'Мордовия', 'Самарская область', 'Саратовская область', 'Пензенская область', 'Ульяновская область', 'Оренбургская область'],
    'Уральский': ['Свердловская область', 'Челябинская область', 'Курганская область', 'Тюменская область', 'Ханты-Мансийский АО', 'Ямало-Ненецкий АО'],
    'Сибирский': ['Красноярский край', 'Иркутская область', 'Новосибирская область', 'Омская область', 'Томская область', 'Кемеровская область', 'Алтайский край', 'Республика Алтай', 'Тыва', 'Хакасия'],
    'Дальневосточный': ['Приморский край', 'Хабаровский край', 'Амурская область', 'Камчатский край', 'Магаданская область', 'Сахалинская область', 'Еврейская АО', 'Чукотский АО']
}

# Добавленные переменные для аналитики
total_votes = 100  # Общее количество голосов
votes_distribution = {region: 0 for region in sum(districts.values(), [])}  # Словарь для отслеживания количества голосов за каждый регион

@app.route('/votes')
def votes():
    return jsonify(available_votes=session.get('available_votes', 100))

@app.route('/', methods=['GET', 'POST'])
def index():
    session['available_votes'] = 100  # Установка начального значения голосов при каждом обращении к корню
    if request.method == 'POST':
        selected = {district: request.form.getlist(district)[:3] for district, regions in districts.items()}
        votes_used = sum(len(regions) for regions in selected.values())
        session['available_votes'] -= votes_used
        session['selected_regions'] = selected
        session['top_regions'] = sum(selected.values(), [])
        for region in session['top_regions']:
            votes_distribution[region] += 1  # Обновляем количество голосов за каждый регион
        return redirect(url_for('federal_stage'))
    return render_template('index.html', districts=districts, available_votes=session['available_votes'])

@app.route('/federal_stage', methods=['GET', 'POST'])
def federal_stage():
    if request.method == 'POST':
        final_selection = request.form.getlist('regions')[:10]
        votes_used = len(final_selection)
        session['available_votes'] -= votes_used
        session['final_selection'] = final_selection
        for region in session['final_selection']:
            votes_distribution[region] += 1  # Обновляем количество голосов за каждый регион
        return redirect(url_for('results'))
    return render_template('federal_stage.html', top_regions=session.get('top_regions', []), available_votes=session['available_votes'])

@app.route('/results')
def results():
    return render_template('results.html', selected_regions=session.get('selected_regions', {}), final_selection=session.get('final_selection', []))

@app.route('/get_available_votes')
def get_available_votes():
    return str(session.get('available_votes', 100))

@app.route('/get_votes_distribution')
def get_votes_distribution():
    return jsonify(votes_distribution)

if __name__ == '__main__':
    app.run(debug=True)