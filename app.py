import secrets
import os
from PIL import Image
from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
'''from forms import RegistrationForm, LoginForm'''

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required

from flask_bcrypt import Bcrypt
from flask_mail import Mail,Message



app = Flask(__name__)


app.config['SECRET_KEY']= '8d2c6184ae40cc9efdefe76c746248dd'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
app.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = 'llr.hall.complaints@gmail.com',
	MAIL_PASSWORD = 'yollr123'
	)
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager=LoginManager(app)
login_manager.login_view = ('login')
login_manager.login_message_category = 'info'
mail = Mail(app)
'''from models import User'''

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model,UserMixin):
	'''
	DB model for Alum
	'''
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


# class Complaint(db.Model):
# 	'''
# 	DB Model for Student's Complaint
# 	IS THIS NEEDED, IF WE ARE MAILING
# 	'''
# 	id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String())
#     room_no = db.Column(db.String())
#     complaint = db.Column(db.String())

#     def __repr__(self):
#         return 'Complaint {} by {}'.format(self.complaint, self.name)


@app.route("/")
@app.route("/home")
def home():
	return render_template('index.html')

@app.route("/about")
def about():
	return render_template('about.html' , title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
	'''
	Sign Up for Alumni
	'''
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
	'''
	Login for Alum Portal
	'''
	form=LoginForm()
	if form.validate_on_submit():
		user=User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password,form.password.data):
			login_user(user, remember=form.remember.data)
			return redirect(url_for('dashboard'))
		else:
			flash('Login Unsuccessful!!!Incorrect Email or Password')
	return render_template('login.html', title='Login', form=form)



@app.route("/logout")
def logout():
	"""
	Logout for Alumni Portal
	"""
	logout_user()
	return redirect(url_for('home'))


def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
	output_size = (125, 125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	i.save(picture_path)
	return picture_fn



@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		'''current_user.username = form.username.data
		current_user.email = form.email.data
		current_user.department = form.department.data
		current_user.room_no = form.room_no.data
		current_user.batch = form.batch.data
		db.session.commit()'''
		flash('Your account has been updated!', 'success')
		return redirect(url_for('dashboard'))
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	return render_template('dashboard.html', title='Dashboard', image_file=image_file , form=form)


@app.route("/complaint", methods=['GET', 'POST'])
def complaint():
	'''
	Register Complaint and mail to manager 
	'''
	
	form = ComplaintForm()
	
	# render the complaint template on get request in browser
	print('request.method = ', request.method)
	if request.method ==  "GET":
		print('in get')
		return render_template('complaint.html', title='Hall Complaint', form=form)

	# on form submission, a POST request is made which sends the mail
	elif request.method == 'POST':
		if form.validate_on_submit():
			name = form.name.data
			room = form.room.data
			complaint = form.complaint.data
			try:
				msg = Message('Complaint from Boarder '+ name + '' + room, sender="llr.hall.complaints@gmail.com",recipients=["utkjaiswal58@gmail.com", "rka87338@gmail.com"])
				msg.html = "<h3>" + complaint + "</h3>"
				mail.send(msg)
				return  '<h1>Your mail has been sent Successfully</h1>'
			except:
				return 'Could not send Mail'




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



class UpdateAccountForm(FlaskForm):
	username=StringField('Name')
	email=StringField('Email')
	department=StringField('Department')
	room_no=StringField('Room Number')
	batch=StringField('Batch')
	picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
	submit=SubmitField('Update Profile')

	# def validate_username(self, username):
	# 	user=User.query.filter_by(username=username.data).first()
	# 	if user:
	# 		raise ValidationError('Username already exist')

	# def validate_email(self, email):
	# 	user=User.query.filter_by(email=email.data).first()
	# 	if user:
	# 		raise ValidationError('Email already exist')



class ComplaintForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired()])
	room = StringField('Room Number', validators=[DataRequired()])
	complaint = StringField('Complaint', validators=[DataRequired()])
	submit=SubmitField('Submit Complaint')

class LoginForm(FlaskForm):
	email=StringField('Email', validators=[DataRequired(), Email()])
	password=PasswordField('Password', validators=[DataRequired()])
	remember=BooleanField('Remember Me')
	submit=SubmitField('Login')

if __name__ =='__main__':
	app.run(debug=True)

