import werkzeug
from flask import Flask, send_file
from flask_cors import CORS
from flask_restful import Api, Resource, reqparse
from models import db, get_alg, get_benchmarks, init_db
from utils import tmpfile, is_error_in_args


def create_app(name, options={}):
    """
    Create the app with the database connection (using Flask-SQLAlchemy).
    """
    app = Flask(name, static_url_path='', template_folder="../static_web")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../bench_lsgo.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['BUNDLE_ERRORS'] = True

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


class Compare(Resource):
    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument('file', type=werkzeug.datastructures.FileStorage,
                           location='files', required=True, help='File is missing')
        parse.add_argument('benchmark_id', type=int, location='form',
                           required=True, help='Benchmark_id is missing')
        args = parse.parse_args()
        fname = tmpfile(args['file'])
        error = is_error_in_args(args)

        if error:
            return {'error': error}


api.add_resource(Compare, '/compare')

# Avoid problem with the Same-origin policy
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

@app.route('/')
def index():
    return send_file('static/index.html')

@app.route('/<path:path>')
def path(path):
    return send_file(path)


if __name__ == '__main__':
    init_db(db)
    app.run(debug=True, port=8000)
