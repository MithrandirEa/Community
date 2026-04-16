from datetime import datetime, timezone

from flask import Blueprint, redirect, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

from app import db
from app.models import Message, NameEntry
from app.models import Session as SimSession
from app.utils.helpers import require_role

population_bp = Blueprint('population', __name__)


class PopulationMessageForm(FlaskForm):
    content = TextAreaField(
        'Message',
        validators=[
            DataRequired(message='Le message ne peut pas être vide.'),
            Length(max=500, message='Message trop long (max 500 caractères).'),
        ],
    )
    # Nom fictif du personnage (optionnel, issu du NamePack de la session)
    sender_name = StringField(validators=[Optional()])
    submit = SubmitField('Publier')


@population_bp.route('/population', methods=['GET', 'POST'])
@require_role('population')
def feed():
    form = PopulationMessageForm()
    active_session = SimSession.query.filter_by(is_active=True).first()
    error = None

    if form.validate_on_submit():
        if not active_session:
            error = 'Aucune session active. Contactez votre animateur.'
        else:
            # Validation du sender_name : doit appartenir aux noms population du pack actif
            sender = (form.sender_name.data or '').strip() or None
            sender_avatar = None
            if sender and active_session.name_pack_id:
                valid = NameEntry.query.filter_by(
                    pack_id=active_session.name_pack_id,
                    role='population',
                    label=sender,
                ).first()
                if not valid:
                    sender = None
                else:
                    sender_avatar = valid.avatar_filename

            msg = Message(
                session_id=active_session.id,
                role='population',
                content=form.content.data.strip(),
                is_published=True,
                real_published_at=datetime.now(timezone.utc).replace(tzinfo=None),
                sender_name=sender,
                sender_avatar_filename=sender_avatar,
            )
            db.session.add(msg)
            db.session.commit()
            return redirect(url_for('population.feed'))

    messages = []
    fictive_time = '--:--'
    sender_names = []
    if active_session:
        fictive_time = active_session.get_fictive_time_str()
        messages = (
            Message.query
            .filter_by(session_id=active_session.id, is_published=True)
            .order_by(Message.real_published_at.desc())
            .all()
        )
        if active_session.name_pack_id:
            sender_names = (
                NameEntry.query
                .filter_by(pack_id=active_session.name_pack_id, role='population')
                .order_by(NameEntry.label)
                .all()
            )

    return render_template(
        'population/feed.html',
        form=form,
        messages=messages,
        active_session=active_session,
        fictive_time=fictive_time,
        error=error,
        sender_names=sender_names,
    )

