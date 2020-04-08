from flask import Flask
from flask import url_for
from flask import request
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired
import json
import random
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/<title>')
@app.route('/index/<title>')
def index(title):
    return render_template('base.html', title=title)


@app.route('/training/<prof>')
def training(prof):
    return render_template('index.html', title=prof)


@app.route('/list_prof/<prof>')
def list_prof(prof):
    return render_template('list_p.html', title=prof)


@app.route('/answer')
@app.route('/auto_answer')
def auto_answer():
    prof = {'title': 'Анкета', 'surname': 'Ватный', 'name': 'Марк', 'education': 'выше среднего',
            'profession': 'штурман марсохода', 'sex': 'мужчина', 'motivation': 'Всегда мечтал застрять на Марсе',
            'ready': 'Да'}
    return render_template('auto_answer.html', title=prof)


class LoginForm(FlaskForm):
    username_a = StringField('id астронавта', validators=[DataRequired()])
    password_a = PasswordField('Пароль астронавта', validators=[DataRequired()])
    username_k = StringField('id капитана', validators=[DataRequired()])
    password_k = PasswordField('Пароль капитана', validators=[DataRequired()])
    submit = SubmitField('Доступ')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/success')
    return render_template('login.html', title='Аварийный доступ', form=form)


@app.route('/distribution')
def distribution():
    prof = ['Oleg', 'Nastya', 'Roma', 'Jena', 'Alex', 'Vitya']
    return render_template('distribution.html', title=prof)


@app.route('/table/<gena>/<int:age>')
def table(gena, age):
    return render_template('table.html', gena=gena, age=age)


class LoginForm2(FlaskForm):
    photo_l = FileField('Загрузить')
    submit = SubmitField('Отправить')


@app.route('/galery', methods=['GET', 'POST'])
def galery():
    form = LoginForm2()
    n = 0
    if form.validate_on_submit():
        f = form.photo_l.data
        map_file = "static/img/p_photo{0}.jpg".format(n)
        with open(map_file, "wb") as file:
            file.write(f)
        n += 1
        return render_template('galery.html', photo='p_photo{0}.jpg'.format(n), form=form)
    return render_template('galery.html', photo='', form=form)


@app.route('/member')
def member():
    f = io.open("templates/mems.json", mode="r", encoding="utf-8")
    readed = f.read()
    jsonn = json.loads(readed)['Members']
    man = random.choice(jsonn)
    print(man['prof'])
    return render_template('member.html', name=man['name'], surname=man['surname'], url=man['url'], prof=man['prof'])


if __name__ == '__main__':
    app.run(port=8008, host='127.0.0.1')
