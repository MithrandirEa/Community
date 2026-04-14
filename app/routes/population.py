from datetime import datetime, timezone

from flask import Blueprint, redirect, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

from app import db
from app.models import Message
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
            msg = Message(
                session_id=active_session.id,
                role='population',
                content=form.content.data.strip(),
                is_published=True,
                real_published_at=datetime.now(timezone.utc).replace(tzinfo=None),
            )
            db.session.add(msg)
            db.session.commit()
            return redirect(url_for('population.feed'))

    messages = []
    fictive_time = '--:--'
    if active_session:
        fictive_time = active_session.get_fictive_time_str()
        messages = (
            Message.query
            .filter_by(session_id=active_session.id, is_published=True)
            .order_by(Message.real_published_at.desc())
            .all()
        )

    return render_template(
        'population/feed.html',
        form=form,
        messages=messages,
        active_session=active_session,
        fictive_time=fictive_time,
        error=error,
    )

