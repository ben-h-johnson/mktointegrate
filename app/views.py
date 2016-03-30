from app import app, api, mktorest, models, lm, db
from flask_restful import Resource, reqparse
#from flask.ext.login import login_user, logout_user, current_user, login_required
from flask import render_template, flash, request, redirect, g, abort, make_response
from .forms import LoginForm
import os
from datetime import datetime

# Init rest client on import
# setvars.py should be maintained locally containing restcreds dictionary
try:
	from app import setvars
	restClient = mktorest.MarketoWrapper(setvars.restcreds['munchkin_id'], 
										 setvars.restcreds['client_id'], 
										 setvars.restcreds['client_secret'])
	apiKey = setvars.apiKey
except ImportError:
	restClient = mktorest.MarketoWrapper(os.environ['munchkin_id'], os.environ['client_id'], os.environ['client_secret'])
	apiKey = os.environ['apiKey']

########################################################
#
#						Logins
#					
########################################################

#
# We use the flask-login library to manage user logins, see docs to understand these endpoints
# https://flask-login.readthedocs.org/en/latest/
#
# @app.before_request
# def before_request():
# 	g.loginform=LoginForm()
# 	g.user = current_user
# 	if current_user.is_authenticated:
# 		g.name = g.user.first_name
# 	else:
# 		g.name = None

# @lm.user_loader
# def load_user(id):
#     return models.User.query.get(int(id))

# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     g.user=None
#     return redirect('/')

# @app.route('/login', methods=['GET','POST'])
# def login():
# 	form = LoginForm()
# 	if form.validate_on_submit():
# 		# Login and validate the user.
# 		# user should be an instance of your `User` class
# 		user = models.User.query.filter_by(email=form.inputEmail.data).first()
# 		if user:
# 			login_user(user, remember=True)
# 			g.user=user
# 			new_cookie=user.set_id_cookie()
# 			db.session.add(user)
# 			db.session.commit()
# 			resp = make_response(redirect(request.referrer))
# 			resp.set_cookie('user_id', new_cookie)
# 			return resp
# 		else:
# 			flash('Invalid Email Address')
# 		return redirect(request.referrer)
# 	return redirect('/')

########################################################
#
#				Base Template and Index
#					
########################################################

# The following should contain a comprehensive list of languages and pages
# These are used to validate incoming URLs
languages = ['en', 'jp']
categories = ['solutions', 'verticals']
pages = ['base', 'b2b', 'email-marketing', 'lead-management', 'consumer-marketing', 
		 'customer-base-marketing', 'mobile-marketing', 'higher-education',
		 'financial-services', 'healthcare']

@app.route('/')
def no_language():
	return redirect('/en')

@app.route('/<language>')
@app.route('/<language>/')
def index(language):
	if language in pages:
		return redirect('/en/' + language)
	if language not in languages:
		return redirect('/en')
	return render_template(language + '/index.html', form=g.loginform, name=g.name, lang=language, page='', path='')

@app.route('/<language>/base')
def base(language):
	if language not in languages:
		return redirect('/en/base')
	return render_template(language+'/base.html', form=g.loginform, name=g.name, lang=language)

# @app.errorhandler(404)
# def page_not_found(error):
#     return render_template('page_not_found.html'), 404

########################################################
#
#	   Universal Route for Solutions and Verticals
#					
########################################################

@app.route('/<language>/<category>/<page>')
def email_marketing(language, category, page):
	if language not in languages:
		return redirect('/en/%s/%s' % (category, page))
	if category not in categories or page not in pages:
		abort(404)
	return render_template('%s/%s/%s.html' % (language, category, page), form=g.loginform, name=g.name, lang=language, path='%s/' % (category), page=page)


########################################################
#
#				Archive and Miscellany
#					
########################################################

# This was an example for pope on how to serve robots.txt, we may use it later
# @app.route('/robots.txt')
# def sendrobot():
# 	return app.send_static_file('robots.txt')