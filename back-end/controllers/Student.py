from application.setup import app
from flask_security import current_user, roles_required
from application.models import Notifications


@app.route("/notifications", methods=["GET"])
@roles_required("Student")
def get_notifications():

    notifications = Notifications.query.filter_by(user_id=current_user.id).all()

    notification_list = [
        {
            "id": notification.id,
            "title": notification.title,
            "type": notification.type,
            "created_at": notification.created_at,
            "read_at": notification.read_at,
        }
        for notification in notifications
    ]

    return notification_list, 200
