import json
from ast import literal_eval as le

from flask import Flask, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField
from wtforms.validators import InputRequired
import data

to_json = {'goals': data.goals, 'teachers': data.teachers}
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(to_json, f, ensure_ascii=False, indent=4)
with open('data.json', 'r', encoding='utf-8') as filejs:
    contents = json.load(filejs)

app = Flask(__name__)
app.secret_key = 'randrandrand6734'
app.config['SQLALCHEMY_DATABASE-URI'] = 'sqlite:///teacher_project.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Teacher(db.Model):
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    about = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    picture = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    free = db.Column(db.String, nullable=False)
    bookings = db.relationship("Booking", back_populates="teacher")
    goals = db.Column(db.String, nullable=False)


class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    weekday = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    client_name = db.Column(db.String, nullable=False)
    client_phone = db.Column(db.String, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))
    teacher = db.relationship("Teacher", back_populates="bookings")


class Request(db.Model):
    __tablename__ = "requests"
    id = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    client_name = db.Column(db.String, nullable=False)
    client_phone = db.Column(db.String, nullable=False)


db.create_all()

teachers = contents['teachers']
for profile in teachers:
    if 'travel' in profile['goals']:
        goal = 'travel'
    teacher = Teacher(name=profile['name'],
                      about=profile['about'],
                      rating=profile['rating'],
                      picture=profile['picture'],
                      price=profile['price'],
                      goals=goal,
                      free=str(profile['free']))
    db.session.add(teacher)
db.session.commit()


@app.route('/')
def main():
    goals_smile = {"travel": "⛱ Для путешествий", "study": "🏫 Для учебы", "work": "🏢 Для работы",
                   "relocate": "🚜 Для переезда"}
    goals = contents['goals']
    random_teachers = db.session.query(Teacher).order_by(func.random()).limit(6)
    return render_template('index.html', goals=goals, goals_smile=goals_smile, teachers=random_teachers)


@app.route('/goals/<goal>/')
def goals(goal):
    if goal == 'travel':
        teachers = db.session.query(Teacher).filter(Teacher.goals == 'travel').order_by(Teacher.rating)
    else:
        teachersgoals = []
        for teacher in contents['teachers']:
            if goal in teacher['goals']:
                teachersgoals.append(teacher)
        teachers = sorted(teachersgoals, key=lambda teacher: teacher['rating'])
    allgoals = contents['goals']
    selectedgoal = allgoals[goal]
    return render_template('goal.html', goal=selectedgoal, teachers=teachers)


@app.route('/profiles/<id>/')
def profile(id):
    teacher = db.session.query(Teacher).get_or_404(int(id))
    daystime = {}
    goals = {}
    freetime = le(teacher.free)
    for day, var in freetime.items():
        for time, check in var.items():
            if check == True:
                daystime[day] = time
    for key, value in contents['goals'].items():
        if key in teacher.goals:
            goals[key] = value
    return render_template('profile.html', teacher=teacher, daystime=daystime, goals=goals)


class RequestForm(FlaskForm):
    goal = RadioField('goal',
                      choices=[("travel", "Для путешествий"), ("learn", "Для школы"), ("work", "Для работы"),
                               ("move", "Для переезда")], default='travel')
    time = RadioField('time', choices=[("1-2", "1-2 часа в неделю"), ("3-5", "3-5 часов в неделю"),
                                       ("5-7", "5-7 часов в неделю"),
                                       ("7-10", "7-10 часов в неделю")], default='1-2')
    client_name = StringField('Вас зовут:', [InputRequired(message='Необходимо ввести имя')])
    client_phone = StringField('Ваш телефон:', [InputRequired(message='Необходимо ввести телефон')])


@app.route('/request/', methods=["GET", "POST"])
def req():
    form = RequestForm()
    if form.validate_on_submit():
        request = Request()
        form.populate_obj(request)
        db.session.add(request)
        db.session.commit()
        print(db.session.query(Request.client_name.first()))
        return render_template('request_done.html', goal=request.goal, time=request.time, name=request.client_name,
                               phone=request.client_phone)
    return render_template('request.html', form=form)


class BookingForm(FlaskForm):
    client_name = StringField('Вас зовут:', [InputRequired(message='Необходимо ввести имя')])
    client_phone = StringField('Ваш телефон:', [InputRequired(message='Необходимо ввести телефон')])
    time = StringField()
    weekday = StringField()


@app.route('/booking/<id>/<weekday>/<time>/', methods=["GET", "POST"])
def booking(id, weekday, time):
    form = BookingForm()
    if form.validate_on_submit():
        booking = Booking()
        form.populate_obj(booking)
        db.session.add(booking)
        db.session.commit()
        return render_template('booking_done.html', weekday=booking.weekday, time=booking.time,
                               name=booking.client_name, phone=booking.client_phone, teacher=booking.teacher)
    else:
        teacher = db.session.query(Teacher).get(int(id))
        # daystime = {}
        # freetime = le(teacher.free)
        # for day1, var in freetime.items():
        #     for time1, check in var.items():
        #         if check == True:
        #             daystime[day1] = time1
        # if weekday in daystime.keys():
        #     time = daystime.get(weekday)
        return render_template('booking.html', teacher=teacher, time=time, weekday=weekday, form=form)


# @app.route('/booking_done/', methods=['POST'])
# def booking_done():
#     name = request.form['clientName']
#     phone = request.form['clientPhone']
#     time = request.form['clientTime']
#     day = request.form['clientWeekday']
#     to_json = [name, phone]
#     with open('booking.json', 'w', encoding='utf-8') as f:
#         json.dump(to_json, f, ensure_ascii=False)
#     return render_template('booking_done.html', name=name, phone=phone, day=day, time=time)


if __name__ == '__main__':
    app.run()
