#!/usr/bin/env python2.7

## @file
## @brief Web interface /Flask/

## @defgroup web Web interface
## @brief Flask-based: http/https, user authorisation
## @{ 

from forth import *

import os,sys
import flask,flask_wtf,wtforms

web = flask.Flask(__name__)

web.config['SECRET_KEY'] = os.urandom(32)

import flask_login
logman = flask_login.LoginManager() ; logman.init_app(web)

from secrets import IP,PORT
from secrets import LOGIN_HASH, PSWD_HASH 
# openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
from secrets import SSL_KEYS

try:
    for i in SSL_KEYS: open(i,'r').close()
except IOError:
    SSL_KEYS = None
    IP = '127.0.0.1'
    DEBUG = True

from werkzeug.security import generate_password_hash,check_password_hash

class CmdForm(flask_wtf.FlaskForm):
    error = wtforms.StringField('no error')
    pad   = wtforms.TextAreaField('pad')
    go    = wtforms.SubmitField('GO')

@web.route('/', methods=['GET', 'POST'])
def index():
    if not flask_login.current_user.is_authenticated:
        return flask.redirect('/login')
    form = CmdForm()
    if form.validate_on_submit(): F.push(String(form.pad.data)) ; INTERPRET(F)
    return flask.render_template('index.html', form=form, vm=F.dump(slots=False))

class User(flask_login.UserMixin):
    def __init__(self,id): self.id = id
@logman.user_loader
def load_user(user_id): return User(user_id) 

class LoginForm(flask_wtf.FlaskForm):
    login = wtforms.StringField('login', [wtforms.validators.DataRequired()])
    pswd  = wtforms.PasswordField('password', [wtforms.validators.DataRequired()])
    go    = wtforms.SubmitField('GO')

@web.route('/login', methods = ['GET', 'POST'])
def login():
    flask_login.logout_user()
    form = LoginForm()
    if form.validate_on_submit():
        LOGIN = form.login.data
        PSWD  = form.pswd.data
        if  check_password_hash(LOGIN_HASH, form.login.data) \
        and check_password_hash(PSWD_HASH , form.pswd.data ):
            flask_login.login_user(User(LOGIN))
            return flask.redirect('/')
        else:
            print 'LOGIN_HASH',generate_password_hash(LOGIN)
            print 'PSWD_HASH' ,generate_password_hash(PSWD)
            return flask.redirect('/login')
    return flask.render_template('login.html',form=form)

@web.route('/logout')
@flask_login.login_required
def logout(): flask.redirect('/login')

@web.route('/<sym>')
@flask_login.login_required
def dump(sym):
    return flask.render_template('dump.html',dump=F[sym].dump())

if __name__ == '__main__':
    web.run(debug=True, host=IP, port=PORT, ssl_context = SSL_KEYS)

## @}
