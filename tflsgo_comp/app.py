from flask import Flask
from .models import db, init_db

def create_app(name, options={}):
    app = Flask(name)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../bench_lsgo.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True

    for opt in options:
        app.config[opt] = options[opt]

    db.app = app
    db.init_app(app)
    return app

app = create_app(__name__)

if __name__ == '__main__':
    init_db(db)
    app.run(debug=True)
