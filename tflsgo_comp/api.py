"""
Program for the Task Force in Large Scale Global Optimization.
Author: Daniel  Molina Cabrera <dmolina@decsai.ugr.es>
"""
import os
import werkzeug

from flask import Flask, send_file, request
from flask_cors import CORS
from flask_restful import Api, Resource, reqparse

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from models import db, get_alg, get_benchmarks, get_benchmark, init_db, User
from models import read_data_alg, get_report
from models import validate_user, get_user_algs, validate_by_token

from readdata import read_results_from_file, error_in_data, concat_df
from utils import tmpfile, is_error_in_args


def create_app(name, options={}):
    """
    Create the app with the database connection (using Flask-SQLAlchemy).

    :param name: name of the application
    :param options: optional number of options for the app.
    """
    app = Flask(name, static_url_path='', template_folder="../static_web")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bench_lsgo.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['BUNDLE_ERRORS'] = True
    app.config['SECRET_KEY'] = 'En un lugar de la mancha'

    for opt in options:
        app.config[opt] = options[opt]

    db.app = app
    db.init_app(app)
    return app


app = create_app(__name__)
admin = Admin(app, name='tflsgo', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
CORS(app)
api = Api(app)


class Benchmark(Resource):
    """
    Rest object to receive the benchmark information.
    """
    def get(self):
        """
        Return the information about benchmarks.
        """
        return {'benchmarks': get_benchmarks()}


class Algs(Resource):
    """
    Rest resource to receive the list of algorithm for a benchmark.
    """
    def get(self, benchmark_id, dimension):
        """
        Return the algorithms available from the indicated benchmark.

        :param benchmark_id: Benchmark id.
        :param dimension: Dimension.
        :returns: json object with the algorithm list.
        :rtype: json.
        """

        return get_alg(benchmark_id, dimension)


class Compare(Resource):
    """
    Rest resource to get the data and file MOS.
    """
    def post(self):
        """
        Return the data for the comparisons.

        :returns: error: With a error, data: with data.
        :rtype: json
        """
        parse = reqparse.RequestParser()
        parse.add_argument('file', type=werkzeug.datastructures.FileStorage,
                           location='files', required=True,
                           help='File is missing')
        parse.add_argument('benchmark_id', type=int, location='form',
                           required=True, help='Benchmark_id is missing')
        parse.add_argument('algs', type=str, location='form',
                           action='append')
        parse.add_argument('alg_name', type=str, location='form', required=True)
        parse.add_argument('report', type=str, location='form', required=True)
        parse.add_argument('dimension', type=int, location='form',
                           required=True)
        args = parse.parse_args()
        error = is_error_in_args(args)
        data = ''
        result = {}
        benchmark_id = args['benchmark_id']
        dimension = args['dimension']

        report_module, error = get_report(args['report'], benchmark_id)

        if args['algs'] and not error:
            data, error = read_data_alg(benchmark_id, args['algs'])

        if args['file'] and not error:
            fname = tmpfile(args['file'])
            alg_name = args['alg_name']
            data_local, error = read_results_from_file(alg_name, fname)

            data_local['milestone'] = data_local['milestone'].astype(float).astype(int)

            if 'dimension' not in data_local:
                data_local['dimension'] = dimension

            if 'alg' not in data_local:
                data_local['alg'] = args['alg_name']

            data = concat_df(data, data_local)
            bench = get_benchmark(benchmark_id)
            error = error_in_data(data, bench['nfuns'], bench['milestones_required'])

        if not args['file'] and not args['algs']:
            error = 'Error: without reference algorithms the file is mandatory'

        if not error:
            categories = sorted(bench['categories'], key=lambda cat: cat.position)
            milestones = bench['milestones_required']
            dimension = args['dimension']
            tables_idx, tables_titles, tables_df = report_module.create_tables(data, categories, milestones, dimension)
            tables = {'idx': tables_idx, 'titles': tables_titles, 'tables': tables_df}
            figures_json = report_module.create_figures(data, categories, milestones, dimension)
            error = figures_json['error']
            divs = figures_json['divs']
            figures = figures_json['plots']
            js = figures_json['js']
            result.update({'tables': tables, 'figures': figures, 'js': js, 'divs': divs})

        result.update({'error': error})
        return result


api.add_resource(Benchmark, '/benchmarks')
api.add_resource(Algs, '/algs/<int:benchmark_id>/<int:dimension>')
api.add_resource(Compare, '/compare')


# Avoid problem with the Same-origin policy
@app.after_request
def after_request(response):
    """Avoid problem for POST in a different domain.

    :param response: add headers for modern browsers.
    :returns: None
    :rtype: None
    """
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


class Login(Resource):
    """
    Rest resource to get the data and file MOS.
    """
    def post(self):
        """
        Return the data for the comparisons.

        :returns: error: With a error, data: with data.
        :rtype: json
        """
        parse = reqparse.RequestParser()
        parse.add_argument('username', type=str, location='form',
                           required=True, help='username is missing')
        parse.add_argument('password', type=str, location='form',
                           required=True, help='password is missing')

        args = parse.parse_args()
        checks = ['username', 'password']
        error = ''
        result = {}

        for check in checks:
            if not args[check] and not error:
                error = '\'{}\' is missing'.format(check)

        if not error:
            user = validate_user(args['username'], args['password'])

            if user is None:
                error = 'Error in login'
            else:
                algs = get_user_algs(user)
                token = user.generate_auth_token(app.config['SECRET_KEY'])
                result.update({'token': token, 'username': user.username,
                               'algs': algs})

        result.update({'error': error})

        return result


class Store(Resource):
    """
    Rest resource to get the data and file MOS.
    """
    def post(self):
        """
        Return the data for the comparisons.

        :returns: error: With a error, data: with data.
        :rtype: json
        """
        print("store")
        parse = reqparse.RequestParser()
        parse.add_argument('token', type=str, location='form',
                           required=True, help='password is missing')
        parse.add_argument('file', type=werkzeug.datastructures.FileStorage,
                           location='files', required=True,
                           help='File is missing')
        parse.add_argument('benchmark_id', type=int, location='form',
                           required=True, help='Benchmark_id is missing')

        parse.add_argument('benchmark_id', type=int, location='form',
                           required=True, help='Benchmark_id is missing')
        parse.add_argument('alg_name', type=str, location='form', required=True)
        parse.add_argument('algs', type=str, location='form',
                           action='append')

        print(request.form)
        args = parse.parse_args()
        checks = ['token', 'benchmark_id']
        alg_name = args['alg_name']
        bench = None
        error = ''
        algs = []
        result = {}

        for check in checks:
            if not args[check] and not error:
                error = 'User not authenticated'

        if not error:
            user = validate_by_token(app.config['SECRET_KEY'], args['token'])

            if user is None:
                error = 'User not authenticated'
            else:
                bench = get_benchmark(args['benchmark_id'])

                if bench is None:
                    error = 'Benchmark not known'

        if not error:
            fname = tmpfile(args['file'])
            data_local, error = read_benchmark_data(alg_name, fname, bench)
            print(data_local)

        result.update({'error': error, 'algs': algs})

        print(result)
        return result


api.add_resource(Login, '/login')
api.add_resource(Store, '/store')

if __name__ == '__main__':
    init_db(db)
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
