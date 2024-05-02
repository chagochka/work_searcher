"""Модель для регистрационной формы"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, SelectField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError


class RegisterForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Роль', choices=[('worker', 'Работник'), ('hirer', 'Работодатель')], validators=[DataRequired()])
    about = TextAreaField('О себе', validators=[DataRequired()], render_kw={"rows": 5})
    submit = SubmitField('Зарегистрироваться')