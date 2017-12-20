from flask import Flask
from flask_restful import Resource, Api
from flask_cors import CORS
from models import db, init_db, get_benchmarks, get_alg

def create_app(name, options={}):
    """
    Create the app with the database connection (using Flask-SQLAlchemy).
    """
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
CORS(app)
api = Api(app)


class Benchmark(Resource):
    def get(self):
        return {'benchmarks': get_benchmarks()}


api.add_resource(Benchmark, '/benchmarks')


class Algs(Resource):
    def get(self, benchmark_id):
        return get_alg(benchmark_id)

api.add_resource(Algs, '/algs/<int:benchmark_id>')

if __name__ == '__main__':
    init_db(db)
    app.run(debug=True)
