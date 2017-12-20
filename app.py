from flask import Flask
from models import db, init_db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bench_lsgo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
db.app = app
db.init_app(app)

if __name__ == '__main__':
    init_db(db)
    app.run(debug=True)
