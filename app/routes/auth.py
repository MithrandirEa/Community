from flask import Blueprint, redirect, render_template, session as flask_session, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from app import bcrypt, db

auth_bp = Blueprint('auth', __name__)


class LoginForm(FlaskForm):
    """Formulaire de connexion — un seul champ : le code d'accès."""
    code = StringField("Code d'accès", validators=[DataRequired(message='Ce champ est obligatoire.')])
    submit = SubmitField('Rejoindre')


@auth_bp.route('/')
def index():
    """Redirige la racine vers la page de connexion."""
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Authentification par code. Redirige vers le feed correspondant."""
    # Si déjà connecté, rediriger vers la bonne interface
    role = flask_session.get('role')
    if role == 'officiel':
        return redirect(url_for('officiel.feed'))
    if role == 'population':
        return redirect(url_for('population.feed'))
    if role == 'admin':
        return redirect(url_for('admin.dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        code = form.code.data.strip()

        from app.models import Config

        cfg_officiel = db.session.get(Config, 'code_officiel')
        cfg_population = db.session.get(Config, 'code_population')
        cfg_admin = db.session.get(Config, 'code_admin')

        if cfg_officiel and code == cfg_officiel.value:
            flask_session['role'] = 'officiel'
            return redirect(url_for('officiel.feed'))

        if cfg_population and code == cfg_population.value:
            flask_session['role'] = 'population'
            return redirect(url_for('population.feed'))

        if cfg_admin and bcrypt.check_password_hash(cfg_admin.value, code):
            flask_session['role'] = 'admin'
            return redirect(url_for('admin.dashboard'))

        return render_template('login.html', form=form,
                               error='Code incorrect. Demandez le code à votre animateur.')

    return render_template('login.html', form=form, error=None)


@auth_bp.route('/logout')
def logout():
    """Déconnexion et retour à la page de login."""
    flask_session.clear()
    return redirect(url_for('auth.login'))

