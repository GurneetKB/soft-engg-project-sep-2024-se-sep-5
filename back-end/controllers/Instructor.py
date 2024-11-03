from application.setup import app
from flask_security import current_user, roles_required
from application.models import Notifications, NotificationPreferences, db, Milestones
from flask import abort, request
from datetime import datetime, timezone



@app.route("/instructor/milestone/publish", methods=["POST"])
#@roles_required("Instructor")
def publishMilestones():
    # Parse the request JSON for preference settings
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    deadline = data.get("deadline")
    deadline = datetime.fromisoformat(deadline)

    #requirements = data.get("requirements")
    milestoneToUpload = Milestones(title = title, description = description, deadline = deadline,created_by=current_user.id if current_user.is_authenticated else None, created_at =datetime.utcnow())
    db.session.add(milestoneToUpload)
    db.session.commit()

    return {"message": "milestone  published successfully."}, 200
