from flask import render_template, url_for, flash, redirect, request, Blueprint, abort, jsonify
from app import db, bcrypt
from app.models import User, Task
from flask_login import login_user, current_user, logout_user, login_required
import psutil
import datetime

main = Blueprint('main', __name__)

@main.route("/")
@login_required
def home():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', tasks=tasks)

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route("/status")
@login_required
def server_status():
    return render_template('status.html')

@main.route("/api/status")
@login_required
def api_status():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())

    services = {
        'nginx': 'stopped',
        'docker': 'stopped',
        'postgres': 'stopped'
    }

    for proc in psutil.process_iter(['name']):
        try:
            name = proc.info['name'].lower()
            if 'nginx' in name:
                services['nginx'] = 'running'
            if 'docker' in name:
                services['docker'] = 'running'
            if 'postgres' in name:
                services['postgres'] = 'running'
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return jsonify({
        'cpu': cpu,
        'ram': ram,
        'disk': disk,
        'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S'),
        'services': services
    })


@main.route("/task/new", methods=['GET', 'POST'])
@login_required
def new_task():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date_str = request.form.get('due_date')

        if due_date_str:
            due_date = datetime.datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
        else:
            due_date = datetime.datetime.utcnow()

        task = Task(title=title, description=description, due_date=due_date, author=current_user)
        db.session.add(task)
        db.session.commit()
        flash('Your task has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_task.html', title='New Task')


@main.route("/task/<int:task_id>/update", methods=['GET', 'POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        abort(403)
    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        if due_date_str:
            task.due_date = datetime.datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')

        task.completed = 'completed' in request.form

        db.session.commit()
        flash('Your task has been updated!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_task.html', title='Update Task', task=task)


@main.route("/task/<int:task_id>/delete", methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        abort(403)
    db.session.delete(task)
    db.session.commit()
    flash('Your task has been deleted!', 'success')
    return redirect(url_for('main.home'))