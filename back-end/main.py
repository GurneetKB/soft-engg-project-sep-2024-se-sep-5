from application.setup import app
from controllers.Student import *
from controllers.Generic import *
from controllers.Instructor import *


if __name__ == "__main__":
    app.run(debug=True)
