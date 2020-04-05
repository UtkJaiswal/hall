from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
'''from forms import RegistrationForm, LoginForm'''

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from flask_login import LoginManager, UserMixin, login_user

from flask_bcrypt import Bcrypt



app = Flask(__name__)


app.config['SECRET_KEY']= '8d2c6184ae40cc9efdefe76c746248dd'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager=LoginManager(app)

'''from models import User'''

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model,UserMixin):
	id=db.Column(db.Integer, primary_key=True)
	username=db.Column(db.String(20), unique=True, nullable=False)
	email=db.Column(db.String(120), unique=True, nullable=False)
	image_file=db.Column(db.String(20), nullable=False, default='default.jpg')
	password=db.Column(db.String(60), nullable=False)
	department=db.Column(db.String(20), nullable=False)
	room_no=db.Column(db.String(20), nullable=False)
	batch=db.Column(db.String(20), nullable=False)

	def __repr__(self):
		return f"User('{self.username}', '{self.email}', '{self.image_file}')"




@app.route("/")
@app.route("/home")
def home():
	return render_template('index.html')

@app.route("/about")
def about():
	return render_template('about.html' , title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
	form=RegistrationForm()
	if form.validate_on_submit():
		hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user=User(username=form.username.data, email=form.email.data, password=hashed_password, department=form.department.data, room_no=form.room_no.data, batch=form.batch.data)
		db.session.add(user)
		db.session.commit()
		flash(f'Account created for {form.username.data}!','success')
		return redirect(url_for('login'))
	return render_template('register.html' , title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
	form=LoginForm()
	if form.validate_on_submit():
		user=User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password,form.password.data):
			login_user(user, remember=form.remember.data)
			return redirect(url_for('home'))
		else:
			flash('Login Unsuccessful!!!Incorrect Email or Password')
	return render_template('login.html', title='Login', form=form)





class RegistrationForm(FlaskForm):
	username=StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
	email=StringField('Email', validators=[DataRequired(), Email()])
	password=PasswordField('Password', validators=[DataRequired()])
	confirm_password=PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	department=StringField('Department', validators=[DataRequired(), Length(min=2, max=20)])
	room_no=StringField('Room Number', validators=[DataRequired(), Length(min=2, max=20)])
	batch=StringField('Batch', validators=[DataRequired(), Length(min=2, max=20)])
	submit=SubmitField('Sign Up')

	def validate_username(self, username):
		user=User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('Username already exist')

	def validate_email(self, email):
		user=User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('Email already exist')



class LoginForm(FlaskForm):
	email=StringField('Email', validators=[DataRequired(), Email()])
	password=PasswordField('Password', validators=[DataRequired()])
	remember=BooleanField('Remember Me')
	submit=SubmitField('Login')

if __name__ =='__main__':
	app.run(debug=True)

