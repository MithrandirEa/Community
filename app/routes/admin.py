import os
import uuid
from datetime import datetime, timezone

from flask import (Blueprint, current_app, flash, redirect,
                   render_template, request, url_for)
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Optional, Regexp

from app import bcrypt, db
from app.models import Comment, Config, Message, Photo
from app.models import Session as SimSession
from app.utils.helpers import require_role

admin_bp = Blueprint('admin', __name__)

# Types MIME et signatures magiques autorisés pour les uploads
_ALLOWED_MIME = {'image/jpeg', 'image/png', 'image/webp'}
_MAGIC_JPEG = b'\xff\xd8\xff'
_MAGIC_PNG = b'\x89PNG'


def _check_image_magic(file_bytes: bytes):
    """
    Vérifie les magic bytes du fichier image.
    Retourne le MIME type détecté ou None si non reconnu.
    """
    if file_bytes[:3] == _MAGIC_JPEG:
        return 'image/jpeg'
    if file_bytes[:4] == _MAGIC_PNG:
        return 'image/png'
    if file_bytes[:4] == b'RIFF' and file_bytes[8:12] == b'WEBP':
        return 'image/webp'
    return None


# --- Formulaires ---

class SessionConfigForm(FlaskForm):
    fictive_start_time = StringField(
        "Heure fictive de début (HH:MM)",
        validators=[
            DataRequired(),
            Regexp(r'^\d{2}:\d{2}$', message='Format HH:MM requis.'),
        ],
    )
    submit = SubmitField('Configurer et démarrer')


class PhotoUploadForm(FlaskForm):
    scenario = StringField(
        'Dossier / Scénario',
        validators=[
            DataRequired(),
            Regexp(r'^[\w\-]+$', message='Lettres, chiffres et tirets uniquement.'),
        ],
    )
    photo = FileField('Photo', validators=[FileRequired()])
    submit = SubmitField('Uploader')


class CodeConfigForm(FlaskForm):
    code_officiel = StringField('Code Officiel', validators=[DataRequired()])
    code_population = StringField('Code Population', validators=[DataRequired()])
    new_admin_code = StringField(
        'Nouveau code Admin (vide = inchangé)',
        validators=[Optional()],
    )
    submit = SubmitField('Enregistrer')


# --- Dashboard ---

@admin_bp.route('/')
@require_role('admin')
def dashboard():
    active_session = SimSession.query.filter_by(is_active=True).first()
    last_session = SimSession.query.order_by(SimSession.id.desc()).first()

    cfg_scenario = db.session.get(Config, 'scenario_actif')
    scenario = cfg_scenario.value if cfg_scenario else ''

    form = SessionConfigForm()
    if active_session:
        form.fictive_start_time.data = active_session.fictive_start_str

    return render_template(
        'admin/dashboard.html',
        active_session=active_session,
        last_session=last_session,
        scenario=scenario,
        form=form,
        fictive_time=active_session.get_fictive_time_str() if active_session else '--:--',
    )


# --- Gestion de session ---

@admin_bp.route('/session/start', methods=['POST'])
@require_role('admin')
def session_start():
    """Configure et démarre une nouvelle session."""
    form = SessionConfigForm()
    if form.validate_on_submit():
        raw = form.fictive_start_time.data.strip()
        h, m = raw.split(':')
        start_minutes = int(h) * 60 + int(m)

        # Désactiver toute session en cours
        for s in SimSession.query.filter_by(is_active=True).all():
            s.is_active = False

        new_session = SimSession(
            fictive_start_minutes=start_minutes,
            real_started_at=datetime.now(timezone.utc).replace(tzinfo=None),
            is_active=True,
        )
        db.session.add(new_session)
        db.session.commit()
        flash(f'Session démarrée à {raw} (heure fictive).', 'success')
    else:
        flash("Format d'heure invalide (HH:MM attendu).", 'error')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/session/stop', methods=['POST'])
@require_role('admin')
def session_stop():
    """Arrête la session en cours."""
    active = SimSession.query.filter_by(is_active=True).first()
    if active:
        active.is_active = False
        active.ended_at = datetime.now(timezone.utc).replace(tzinfo=None)
        db.session.commit()
        flash('Session arrêtée.', 'success')
    else:
        flash('Aucune session active.', 'error')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/session/reset', methods=['POST'])
@require_role('admin')
def session_reset():
    """Réinitialise la session : supprime les messages et commentaires (photos conservées)."""
    active = SimSession.query.filter_by(is_active=True).first()
    if active:
        active.is_active = False
        active.ended_at = datetime.now(timezone.utc).replace(tzinfo=None)

    # Suppression en cascade des messages et commentaires de toutes les sessions
    for sess in SimSession.query.all():
        db.session.delete(sess)

    db.session.commit()
    flash('Session réinitialisée. Les messages ont été supprimés (photos conservées).', 'success')
    return redirect(url_for('admin.dashboard'))


# --- Photothèque ---

@admin_bp.route('/photos')
@require_role('admin')
def photos():
    cfg_scenario = db.session.get(Config, 'scenario_actif')
    scenario_actif = cfg_scenario.value if cfg_scenario else ''

    # Grouper les photos par dossier
    all_photos = Photo.query.order_by(Photo.scenario_folder, Photo.uploaded_at.desc()).all()
    scenarios = {}
    for p in all_photos:
        scenarios.setdefault(p.scenario_folder, []).append(p)

    form = PhotoUploadForm()
    if scenario_actif:
        form.scenario.data = scenario_actif

    return render_template(
        'admin/photos.html',
        scenarios=scenarios,
        scenario_actif=scenario_actif,
        form=form,
    )


@admin_bp.route('/photos/upload', methods=['POST'])
@require_role('admin')
def photo_upload():
    """Upload une photo vers un dossier de scénario."""
    form = PhotoUploadForm()
    if not form.validate_on_submit():
        flash('Formulaire invalide.', 'error')
        return redirect(url_for('admin.photos'))

    file = form.photo.data
    scenario = form.scenario.data.strip()

    # Lire les premiers octets pour vérifier les magic bytes
    header = file.read(12)
    detected_mime = _check_image_magic(header)
    if detected_mime not in _ALLOWED_MIME:
        flash('Format non autorisé. Seuls JPEG, PNG et WebP sont acceptés.', 'error')
        return redirect(url_for('admin.photos'))

    # Remettre le curseur au début avant la sauvegarde
    file.seek(0)

    # Extension dérivée du MIME
    ext_map = {'image/jpeg': '.jpg', 'image/png': '.png', 'image/webp': '.webp'}
    ext = ext_map[detected_mime]
    original_name = secure_filename(file.filename or 'photo' + ext)
    unique_filename = f'{uuid.uuid4().hex}_{original_name}'

    # Répertoire de destination
    dest_dir = os.path.join(current_app.config['PHOTOS_FOLDER'], scenario)
    os.makedirs(dest_dir, exist_ok=True)
    file.save(os.path.join(dest_dir, unique_filename))

    # Enregistrement en base
    photo = Photo(
        scenario_folder=scenario,
        filename=unique_filename,
        original_name=original_name,
        uploaded_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    db.session.add(photo)
    db.session.commit()

    flash(f'Photo «{original_name}» uploadée dans «{scenario}».', 'success')
    return redirect(url_for('admin.photos'))


@admin_bp.route('/photos/delete/<int:photo_id>', methods=['POST'])
@require_role('admin')
def photo_delete(photo_id):
    """Supprime une photo (fichier + entrée base de données)."""
    photo = db.get_or_404(Photo, photo_id)

    filepath = os.path.join(
        current_app.config['PHOTOS_FOLDER'],
        photo.scenario_folder,
        photo.filename,
    )
    if os.path.exists(filepath):
        os.remove(filepath)

    db.session.delete(photo)
    db.session.commit()
    flash(f'Photo «{photo.original_name}» supprimée.', 'success')
    return redirect(url_for('admin.photos'))


@admin_bp.route('/photos/scenario', methods=['POST'])
@require_role('admin')
def set_scenario():
    """Définit le scénario actif (dossier de photos disponibles pour l'officiel)."""
    scenario = request.form.get('scenario', '').strip()
    cfg = db.session.get(Config, 'scenario_actif')
    if cfg:
        cfg.value = scenario
    else:
        db.session.add(Config(key='scenario_actif', value=scenario))
    db.session.commit()
    flash(f'Scénario actif : «{scenario or "aucun"}».', 'success')
    return redirect(url_for('admin.photos'))


# --- Gestion des codes d'accès ---

@admin_bp.route('/config', methods=['GET', 'POST'])
@require_role('admin')
def config():
    form = CodeConfigForm()

    if form.validate_on_submit():
        _upsert_config('code_officiel', form.code_officiel.data.strip())
        _upsert_config('code_population', form.code_population.data.strip())
        if form.new_admin_code.data:
            hashed = bcrypt.generate_password_hash(
                form.new_admin_code.data.strip()
            ).decode('utf-8')
            _upsert_config('code_admin', hashed)
        db.session.commit()
        flash("Codes d'accès mis à jour.", 'success')
        return redirect(url_for('admin.config'))

    # Pré-remplir depuis la base
    cfg_o = db.session.get(Config, 'code_officiel')
    cfg_p = db.session.get(Config, 'code_population')
    form.code_officiel.data = cfg_o.value if cfg_o else ''
    form.code_population.data = cfg_p.value if cfg_p else ''

    return render_template('admin/config.html', form=form)


def _upsert_config(key: str, value: str) -> None:
    """Met à jour ou crée une entrée Config."""
    cfg = db.session.get(Config, key)
    if cfg:
        cfg.value = value
    else:
        db.session.add(Config(key=key, value=value))

