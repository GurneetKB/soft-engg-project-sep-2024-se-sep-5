from application.setup import app
from apis.Student import *
from apis.Generic import *
from apis.Instructor import *


if __name__ == "__main__":
    app.run(debug=True)
