from functools import wraps

from flask import jsonify, make_response, Blueprint, current_app, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from . import db_session
from .users import User

blueprint = Blueprint(
	'admin_api',
	__name__,
	template_folder='templates'
)

db_session.global_init('postgres:12345@localhost:5000/db')
db_sess = db_session.create_session()

def admin_required(f):
	@wraps(f)
	@login_required
	def decorated_function(*args, **kwargs):
		with current_app.test_request_context():
			if current_user.status == "admin":
				return f(*args, **kwargs)
			else:
				return make_response(jsonify({'error': 'Отказано в доступе'}), 400)

	return decorated_function


def get_users():
	users = db_sess.query(User).filter(User.status != 'admin')
	return [user.to_dict() for user in users]


@blueprint.route('/admin/dashboard')
@admin_required
def dashboard():
	return render_template('admin_dashboard.html', users=get_users(), title='Панель администратора')


@blueprint.route('/admin/users')
@admin_required
def get_users_request():
	return jsonify(
		{
			'users':
				get_users()
		}
	)


@blueprint.route('/admin/users/<int:user_id>', methods=['GET'])
@admin_required
def get_one_user(user_id):
	user = db_sess.query(User).get(user_id)
	if not user:
		return make_response(jsonify({'error': 'Not found'}), 404)
	return jsonify(
		{
			'user': user.to_dict()
		}
	)


