from application.setup import app
from controllers.Student import *
from controllers.Generic import *
from controllers.Instructor import *
from controllers.team_dummy import *


if __name__ == "__main__":
    app.run(debug=True)
