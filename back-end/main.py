from application.setup import app, api
from controllers.Student import *
from controllers.Generic import *
from controllers.Instructor import *

from controllers.api.milestoneAPI import MilestoneAPI, MilestoneAllAPI

# Register the Milestone API route
api.add_resource(
    MilestoneAPI, "/instructor/milestone", "/instructor/milestone/<milestone_id>"
)
api.add_resource(MilestoneAllAPI, "/instructor/all_milestone")


if __name__ == "__main__":
    app.run(debug=True)
