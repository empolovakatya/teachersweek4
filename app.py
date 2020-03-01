from flask import Flask, render_template, request
import requests
import json
import pprint
import data
import random

to_json = {'goals': data.goals, 'teachers': data.teachers}
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(to_json, f, ensure_ascii=False, indent=4)
with open('data.json', 'r', encoding='utf-8') as filejs:
    contents = json.load(filejs)

app = Flask(__name__)


@app.route('/')
def main():
    goals_smile = {"travel": "⛱ Для путешествий", "study": "🏫 Для учебы", "work": "🏢 Для работы",
                   "relocate": "🚜 Для переезда"}
    goals=contents['goals']
    random_teachers = random.sample(contents['teachers'], 6)
    return render_template('index.html', goals=goals, goals_smile=goals_smile, teachers=random_teachers )


@app.route('/goals/<goal>/')
def goals(goal):
    teachersgoals = []
    allgoals = contents['goals']
    selectedgoal = allgoals[goal]
    for teacher in contents['teachers']:
        if goal in teacher['goals']:
            teachersgoals.append(teacher)
    teachersgoals_sorted = sorted(teachersgoals, key=lambda teacher: teacher['rating'])
    return render_template('goal.html', goal=selectedgoal, teachers=teachersgoals_sorted)


@app.route('/profiles/<id>/')
def profile(id):
    teachers = contents['teachers']
    teacher = teachers[int(id)]
    daystime = {}
    goals = {}
    for day, var in teacher['free'].items():
        for time, check in var.items():
            if check == True:
                daystime[day] = time
    for key, value in contents['goals'].items():
        if key in teacher['goals']:
            goals[key] = value
    return render_template('profile.html', teacher=teacher, daystime=daystime, goals=goals)


@app.route('/request/')
def req():
    return render_template('request.html')


@app.route('/request_done/', methods=['POST'])
def request_done():
    goal = request.form['goal']
    time = request.form['time']
    name = request.form['clientName']
    phone = request.form['clientPhone']
    to_json = [goal, time]
    with open('request.json', 'w', encoding='utf-8') as f:
        json.dump(to_json, f, ensure_ascii=False)
    goalform = {"travel": "Для путешествий", "learn": "Для школы", "work": "Для работы", "move": "Для переезда"}
    timeform = {"1-2": "1-2 часа в неделю", "3-5": "3-5 часов в неделю", "5-7": "5-7 часов в неделю",
                "7-10": "7-10 часов в неделю"}
    goalselected = goalform[goal]
    timeselected = timeform[time]
    return render_template('request_done.html', goal=goalselected, time=timeselected, name=name, phone=phone)


@app.route('/booking/<id>/<day>/<time>/')
def booking(id, day, time):
    teachers = contents['teachers']
    teacher = teachers[int(id)]
    daystime = {}
    for day1, var in teacher['free'].items():
        for time1, check in var.items():
            if check == True:
                daystime[day1] = time1
    if day in daystime.keys():
        time = daystime.get(day)
    return render_template('booking.html', teacher=teacher, time=time, day=day, daystime=daystime)


@app.route('/booking_done/', methods=['POST'])
def booking_done():
    name = request.form['clientName']
    phone = request.form['clientPhone']
    time = request.form['clientTime']
    day = request.form['clientWeekday']
    print(name, phone)
    to_json = [name, phone]
    with open('booking.json', 'w', encoding='utf-8') as f:
        json.dump(to_json, f, ensure_ascii=False)
    return render_template('booking_done.html', name=name, phone=phone, day=day, time=time)


if __name__ == '__main__':
    app.run()
