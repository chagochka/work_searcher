import datetime
import os

from sqlalchemy import desc

from flask import (
	Flask,
	render_template,
	request,
	make_response,
	jsonify,
	url_for
)
from flask_login import (
	LoginManager,
	login_user,
	logout_user,
	login_required,
	current_user
)
from flask_restful import Api
from werkzeug.utils import redirect

from data import db_session, admin_api
from data.login import LoginForm
from data.register import RegisterForm
from data.users import User
from data.orders import Order
from data.replies import Reply

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chagochka_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)


def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in {'docx'}


@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
	return make_response(jsonify({'error': 'Bad Request'}), 400)


@login_manager.user_loader
def load_user(user_id):
	"""Загрузка пользователя"""
	db = db_session.create_session()
	return db.get(User, user_id)


@app.route('/')
@app.route('/index')
def index():
	"""Корневая страница"""
	return render_template('index.html', orders=db.query(Order).order_by(desc(Order.date)).all(), title='Главная')


@login_required
@app.route('/add_order', methods=['GET', 'POST'])
def add_order():
	"""Страница для создания заказа"""

	if request.method == 'POST':
		description = request.form['description']
		price = request.form['price']
		title = request.form['title']

		order = Order()
		order.hirer_id = current_user.id
		order.title = title
		order.price = price
		order.descr = description
		db.add(order)
		db.commit()

		return redirect(url_for('index'))

	return render_template('add_order.html', title='Размещение заказа')


@login_required
@app.route('/add_reply/<int:order_id>', methods=['GET', 'POST'])
def add_reply(order_id):
	"""Страница для отправления отклика"""

	if request.method == 'POST':
		reply = Reply()
		reply.worker_id = current_user.id
		reply.order_id = order_id
		reply.title = request.form['title']
		reply.descr = request.form['description']
		reply.status = 'unviewed'
		db.add(reply)
		db.commit()

		return redirect(url_for('workers_replies', order_id=0))

	return render_template('add_reply.html', order=db.get(Order, order_id), title='Оставить отклик')


@app.route('/reply/<int:reply_id>', methods=['GET', 'POST'])
@login_required
def reply_form(reply_id):
	reply = db.get(Reply, reply_id)
	order = db.get(Order, reply.order_id)

	if current_user.status == 'hirer' and order:
		reply.status = 'viewed'

		if request.method == 'POST':
			reply.status = 'accepted'

		db.commit()
	elif reply.worker_id == current_user.id:
		pass
	else:
		return "Вы не имеете права просмотреть этот отклик", 403

	return render_template('reply_form.html', reply=reply, order=order)


@login_required
@app.route('/worker_replies/<int:order_id>', methods=['GET'])
def workers_replies(order_id):
	"""Страница для просмотра откликов"""

	if order_id > 0:
		return render_template('workers_replies.html', replies=db.get(Order, order_id).replies, title='Отклики')

	return render_template('workers_replies.html', replies=sorted(db.get(
		User, current_user.id).replies, key=lambda reply: reply.date), title='Мои отклики')


@app.route('/register', methods=['GET', 'POST'])
def register():
	db = db_session.create_session()
	regform = RegisterForm()

	if regform.validate_on_submit():
		# Проверка наличия пользователя с таким email
		existing_user = db.query(User).filter(User.email == regform.email.data).first()
		if existing_user:
			return render_template('register.html',
			                       title='Регистрация', form=regform, message='Такой пользователь уже есть')

		# Создание нового пользователя
		new_user = User(
			name=regform.first_name.data,
			surname=regform.last_name.data,
			email=regform.email.data,
			status=regform.role.data,
			about=regform.about.data
		)
		new_user.set_password(regform.password.data)
		db.add(new_user)
		db.commit()
		return redirect('/login')

	return render_template(
		'register.html',
		title='Регистрация',
		form=regform
	)


@app.route('/login', methods=['GET', 'POST'])
def login():
	"""Авторизация"""
	form = LoginForm()
	if form.validate_on_submit():
		db = db_session.create_session()
		user = db.query(User).filter(User.email == form.email.data).first()
		if user and user.check_password(form.password.data):
			login_user(user, remember=form.remember_me.data)
			return redirect("/")
		return render_template(
			'login.html',
			message="Неправильный логин или пароль",
			form=form
		)
	return render_template(
		'login.html',
		title='Авторизация',
		form=form
	)


@app.route('/user/<user_login>')
@login_required
def search_user(user_login):
	"""Страница пользователя"""
	user = db.query(User).filter(User.email == user_login).first()
	return render_template('user_account_form.html', user=user, orders=user.orders, replies=user.replies,
	                       title=f'Профиль {user.name} {user.surname}')


@app.route('/logout')
@login_required
def logout():
	"""Выход из аккаунта"""
	logout_user()
	return redirect('/')


if __name__ == '__main__':
	db_session.global_init('12345')
	db = db_session.create_session()
	if not list(db.query(User).filter(User.status == 'admin')):
		admin = User()
		admin.name = 'ADMIN'
		admin.email = input('Введите свою почту: ')
		admin.status = 'admin'
		admin.set_password(input('Установите пароль: '))
		db.add(admin)
		db.commit()
	app.register_blueprint(admin_api.blueprint)
	port = int(os.environ.get('PORT', 8000))
	app.run(host='0.0.0.0', port=port)
