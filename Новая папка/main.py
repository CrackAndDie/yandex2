from flask import Flask
from flask import url_for
from flask import request, redirect, jsonify, make_response
from flask import render_template, abort
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, IntegerField, DateTimeField
from wtforms.validators import DataRequired
from data import db_session
from data.users import User
from data.jobs import Jobs
from data.category import Category
from data.departments import Departments
from flask_login import login_required, login_user, logout_user, current_user
from flask_login import LoginManager
import flask_login
import jobs_api
import user_api
import requests
from requests import delete, put, get, post

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route("/")
def index():
    session = db_session.create_session()
    jobs = session.query(Jobs).all()
    users = session.query(User).all()
    return render_template("index.html", jobs=jobs, users=users)


class RegForm(FlaskForm):
    login = StringField('Login / email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_r = PasswordField('Repeat password', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    speciality = StringField('Speciality', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    city_from = StringField('Hometown', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegForm()
    if form.validate_on_submit():
        if form.password.data != form.password_r.data:
            return render_template('reg.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.login.data).first():
            return render_template('reg.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User()
        user.surname = form.surname.data
        user.name = form.name.data
        user.age = form.age.data
        user.position = form.position.data
        user.speciality = form.speciality.data
        user.address = form.address.data
        user.email = form.login.data
        user.city_from = form.city_from.data
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect("/")
    return render_template('reg.html', title='Регистрация', form=form)


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация в системе Mars One', form=form)


class JobsForm(FlaskForm):
    job = StringField('Название работы', validators=[DataRequired()])
    category = StringField('Название категории', validators=[DataRequired()])
    collaborators = StringField('Участники', validators=[DataRequired()])
    team_leader = IntegerField('Тим лид', validators=[DataRequired()])
    work_size = IntegerField('Объем работы', validators=[DataRequired()])
    # end_date = DateTimeField('Окончание работы', validators=[DataRequired()])
    is_finished = BooleanField("Закончена")
    submit = SubmitField('Применить')


@app.route('/add_job',  methods=['GET', 'POST'])
@login_required
def add_jobs():
    form = JobsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        jobs = Jobs()
        jobs.job = form.job.data
        jobs.collaborators = form.collaborators.data
        jobs.team_leader = form.team_leader.data
        jobs.work_size = form.work_size.data
        jobs.is_finished = form.is_finished.data
        cate = session.query(Category).filter(Category.name == form.category.data).first()
        if cate:
            if len(jobs.categories) == 0:
                jobs.categories.append(cate)
            else:
                jobs.categories[0] = cate
        else:
            cate = Category()
            cate.name = form.category.data
            session.add(cate)
            if len(jobs.categories) == 0:
                jobs.categories.append(cate)
            else:
                jobs.categories[0] = cate
        session.add(jobs)
        session.commit()
        return redirect('/')
    return render_template('add_job.html', title='Добавление работы',
                           form=form)


@app.route('/edit_job/<int:id_j>', methods=['GET', 'POST'])
@login_required
def edit_job(id_j):
    form = JobsForm()
    if request.method == "GET":
        session = db_session.create_session()
        jobs = session.query(Jobs).filter(Jobs.id == id_j,
                                          (Jobs.team_leader == current_user.id | current_user.id == 1)).first()
        if jobs:
            form.job.data = jobs.job
            form.collaborators.data = jobs.collaborators
            form.team_leader.data = jobs.team_leader
            form.work_size.data = jobs.work_size
            form.is_finished.data = jobs.is_finished
            form.category.data = jobs.categories[0].name
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        jobs = session.query(Jobs).filter(Jobs.id == id_j,
                                          (Jobs.team_leader == current_user.id | current_user.id == 1)).first()
        if jobs:
            jobs.job = form.job.data
            jobs.collaborators = form.collaborators.data
            jobs.team_leader = form.team_leader.data
            jobs.work_size = form.work_size.data
            jobs.is_finished = form.is_finished.data
            cate = session.query(Category).filter(Category.name == form.category.data).first()
            if cate:
                if len(jobs.categories) == 0:
                    jobs.categories.append(cate)
                else:
                    jobs.categories[0] = cate
            else:
                cate = Category()
                cate.name = form.category.data
                session.add(cate)
                if len(jobs.categories) == 0:
                    jobs.categories.append(cate)
                else:
                    jobs.categories[0] = cate
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('add_job.html', title='Редактирование работы', form=form)


@app.route('/job_delete/<int:id_j>', methods=['GET', 'POST'])
@login_required
def job_delete(id_j):
    session = db_session.create_session()
    jobs = session.query(Jobs).filter(Jobs.id == id_j,
                                      (Jobs.team_leader == current_user.id | current_user.id == 1)).first()
    if jobs:
        session.delete(jobs)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route("/departments")
def departments():
    session = db_session.create_session()
    jobs = session.query(Jobs).all()
    users = session.query(User).all()
    deps = session.query(Departments).all()
    return render_template("departments.html", jobs=jobs, users=users, deps=deps)


class DepsForm(FlaskForm):
    title = StringField('Название департамента', validators=[DataRequired()])
    members = StringField('Участники', validators=[DataRequired()])
    chief = IntegerField('Шеф', validators=[DataRequired()])
    email = StringField('Почта департамента', validators=[DataRequired()])
    submit = SubmitField('Применить')


@app.route('/add_dep',  methods=['GET', 'POST'])
@login_required
def add_dep():
    form = DepsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        deps = Departments()
        deps.title = form.title.data
        deps.members = form.members.data
        deps.chief = form.chief.data
        deps.email = form.email.data
        session.add(deps)
        session.commit()
        return redirect('/departments')
    return render_template('add_dep.html', title='Добавление департамента',
                           form=form)


@app.route('/edit_dep/<int:id_j>', methods=['GET', 'POST'])
@login_required
def edit_dep(id_j):
    form = DepsForm()
    if request.method == "GET":
        session = db_session.create_session()
        deps = session.query(Departments).filter(Departments.id == id_j,
                                                 (Departments.chief == current_user.id | current_user.id == 1)).first()
        if deps:
            form.title.data = deps.title
            form.members.data = deps.members
            form.chief.data = deps.chief
            form.email.data = deps.email
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        deps = session.query(Departments).filter(Departments.id == id_j,
                                                 (Departments.chief == current_user.id | current_user.id == 1)).first()
        if deps:
            deps.title = form.title.data
            deps.members = form.members.data
            deps.chief = form.chief.data
            deps.email = form.email.data
            session.commit()
            return redirect('/departments')
        else:
            abort(404)
    return render_template('add_dep.html', title='Редактирование департамента', form=form)


@app.route('/dep_delete/<int:id_j>', methods=['GET', 'POST'])
@login_required
def dep_delete(id_j):
    session = db_session.create_session()
    deps = session.query(Departments).filter(Departments.id == id_j,
                                             (Departments.chief == current_user.id | current_user.id == 1)).first()
    if deps:
        session.delete(deps)
        session.commit()
    else:
        abort(404)
    return redirect('/departments')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/users_show/<int:user_id>')
@login_required
def users_show(user_id):
    j = get('http://127.0.0.1:8008/api/user/{0}'.format(user_id)).json()
    city = j['user']['city_from']

    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={0}&format=json".format(city)
    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"].split()

        map_request = "https://static-maps.yandex.ru/1.x/?ll={a},{b}&z=13&l=sat".format(a=str(toponym_coodrinates[0]), b=str(toponym_coodrinates[1]))
        response = requests.get(map_request)
        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
        else:
            nas = j['user']['surname'] + ' ' + j['user']['name']
            ct = 'map{0}.png'.format(j['user']['name'] + ' ' + j['user']['surname'])
            map_file = "static/img/{0}".format(ct)
            with open(map_file, "wb") as file:
                file.write(response.content)
            return render_template('user_city.html', title='Hometown', city=ct, nas=nas, town=j['user']['city_from'])
    abort(404)


def main():
    db_session.global_init("db/blogs.sqlite")
    app.register_blueprint(jobs_api.blueprint)
    app.register_blueprint(user_api.blueprint)
    app.run(port=8008, host='127.0.0.1')


if __name__ == '__main__':
    main()
