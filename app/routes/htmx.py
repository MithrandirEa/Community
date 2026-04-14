from datetime import datetime, timezone

from flask import Blueprint, abort, render_template, session as flask_session
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length

from app import db
from app.models import Comment, Config, Message
from app.models import Session as SimSession
from app.utils.helpers import require_role

htmx_bp = Blueprint('htmx', __name__)


class CommentForm(FlaskForm):
    content = StringField(
        validators=[
            DataRequired(message='La réponse ne peut pas être vide.'),
            Length(max=300, message='Réponse trop longue (max 300 caractères).'),
        ]
    )


@htmx_bp.route('/ping')
def ping():
    """Point de test de disponibilité."""
    return 'pong', 200


@htmx_bp.route('/feed')
@require_role('officiel', 'population', 'admin')
def feed():
    """Fragment HTMX : liste de tous les messages publiés (polling toutes les 2s)."""
    active_session = SimSession.query.filter_by(is_active=True).first()
    messages = []
    scenario = ''
    fictive_time = '--:--'

    if active_session:
        fictive_time = active_session.get_fictive_time_str()
        messages = (
            Message.query
            .filter_by(session_id=active_session.id, is_published=True)
            .order_by(Message.real_published_at.desc())
            .all()
        )
        cfg = db.session.get(Config, 'scenario_actif')
        scenario = cfg.value if cfg else ''

    return render_template(
        'partials/feed.html',
        messages=messages,
        active_session=active_session,
        user_role=flask_session.get('role'),
        scenario=scenario,
        fictive_time=fictive_time,
    )


@htmx_bp.route('/comments/<int:message_id>')
@require_role('officiel', 'population', 'admin')
def comments_section(message_id):
    """Fragment HTMX : liste des réponses + formulaire pour un message donné."""
    message = db.get_or_404(Message, message_id)
    form = CommentForm()
    comments_list = message.comments.order_by(Comment.real_created_at.asc()).all()
    return render_template(
        'partials/comments.html',
        message=message,
        comments=comments_list,
        form=form,
        user_role=flask_session.get('role'),
    )


@htmx_bp.route('/comment/<int:message_id>', methods=['POST'])
@require_role('officiel', 'population')
def post_comment(message_id):
    """Fragment HTMX : soumet une réponse, retourne la section mise à jour."""
    message = db.get_or_404(Message, message_id)
    form = CommentForm()

    if form.validate_on_submit():
        active_session = SimSession.query.filter_by(is_active=True).first()
        if not active_session:
            abort(403)
        comment = Comment(
            message_id=message_id,
            role=flask_session['role'],
            content=form.content.data.strip(),
            real_created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        db.session.add(comment)
        db.session.commit()

    new_form = CommentForm()
    comments_list = message.comments.order_by(Comment.real_created_at.asc()).all()
    return render_template(
        'partials/comments.html',
        message=message,
        comments=comments_list,
        form=new_form,
        user_role=flask_session.get('role'),
    )

