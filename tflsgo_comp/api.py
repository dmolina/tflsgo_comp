"""
Program for the Task Force in Large Scale Global Optimization.
Author: Daniel  Molina Cabrera <dmolina@decsai.ugr.es>
"""
import os
import werkzeug

from flask import Flask, send_file, request
from flask_restful import Api, Resource, reqparse
from flask_cache import Cache

from assets import gen_static
from flask_compress import Compress

# from flask_admin import Admin
# from flask_admin.contrib.sql import ModelView

from models import db, get_alg, get_alg_user, get_benchmarks, get_benchmark

from models import filter_with_user_algs

from models import init_db
from models import read_data_alg, get_report
from models import validate_user, get_user_algs, validate_by_token

from models import delete_alg,  write_proposal_data

from readdata import concat_df, read_benchmark_data
from utils import tmpfile, is_error_in_args
from reports.report_utils import load_charts_library

def get_options(list):
    parse = reqparse.RequestParser()

    for option in list:
        if option in ['benchmark_id', 'dimension']:
            parse.add_argument(option, type=int, location='form',
                               required=True, help='{}_id is missing'.format(option))
        elif option in ['token', 'alg_name', 'report', 'username', 'password', 'libcharts']:
            parse.add_argument(option, type=str, location='form')
        elif option in ['algs_str']:
            parse.add_argument('algs_str', type=str, location='form')
        elif option in ['algs']:
            parse.add_argument(option, type=str, location='form',
                               action='append')
        elif option in ['mobile']:
            pass
        elif option in ['file']:
            parse.add_argument('file',
                               type=werkzeug.datastructures.FileStorage,
                               location='files', required=True,
                               help='File is missing')
        else:
            raise("option '{}' in unknown".format(option))

    dict = parse.parse_args()

    if 'mobile' in list:
        mobile_str = request.form['mobile']
        mobile = mobile_str.lower() != 'false'
        dict['mobile'] = mobile

    return dict


def create_app(name, options={}):
    """
    Create the app with the database connection (using Flask-SQLAlchemy).

    :param name: name of the application
    :param options: optional number of options for the app.
    """
    app = Flask(name)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bench_lsgo.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['BUNDLE_ERRORS'] = True
    app.config['SECRET_KEY'] = 'En un lugar de la mancha'

    for opt in options:
        app.config[opt] = options[opt]

    db.app = app
    db.init_app(app)
    # add whitenoise
    return app


app = create_app(__name__)
# admin = Admin(app, name='tflsgo', template_mode='bootstrap3')
# admin.add_view(ModelView(User, db.session))
# admin.add_view(ModelView(Algorithm, db.session))
Compress(app)
api = Api(app)
# Check Configuring Flask-Cache section for more details
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
cache.clear()
gen_static()


class Benchmark(Resource):
    """
    Rest object to receive the benchmark information.
    """
    @cache.cached(timeout=300)
    def get(self):
        """
        Return the information about benchmarks.
        """
        return {'benchmarks': get_benchmarks()}


class BenchmarkToken(Resource):
    @cache.cached(timeout=10)
    def get(self, token):
        """
        Return the benchmarks in which the author has algorithms.

        :param token: token of user.

        """
        bench = get_benchmarks()
        user = validate_by_token(app.config['SECRET_KEY'], token)

        if user:
            bench = filter_with_user_algs(bench, user)

        return {'benchmarks': bench}


class Algs(Resource):
    """
    Rest resource to receive the list of algorithm for a benchmark.
    """
    @cache.cached(timeout=10)
    def get(self, benchmark_id, dimension):
        """
        Return the algorithms available from the indicated benchmark.

        :param benchmark_id: Benchmark id.
        :param dimension: Dimension.
        :returns: json object with the algorithm list.
        :rtype: json.
        """
        result = get_alg(benchmark_id, dimension)
        return result


class AlgsUsers(Resource):
    """
    Rest resource to receive the list of algorithm for a benchmark.
    """
    # @cache.cached(timeout=30)
    def post(self):
        """
        Return the algorithms available from the indicated benchmark.

        :param benchmark_id: Benchmark id.
        :param dimension: Dimension.
        :returns: json object with the algorithm list.
        :rtype: json.
        """
        args = get_options(['benchmark_id', 'token'])
        error = ''
        result = {}
        user = None

        if 'benchmark_id' not in args:
            error = 'Benchmark id missing'
        elif 'token' in args:
            user = validate_by_token(app.config['SECRET_KEY'], args['token'])

        if user and not error:
            benchmark_id = args['benchmark_id']
            result.update({'algs': get_alg_user(benchmark_id, user)})

        result.update({'error': error})
        return result


class Delete(Resource):
    def post(self):
        args = get_options(['benchmark_id', 'token', 'algs_str'])
        benchmark_id = args['benchmark_id']
        token = args['token']
        algs = args['algs_str'].split(',')
        error = ''

        user = validate_by_token(app.config['SECRET_KEY'], token)

        if not user:
            error = 'User not identified'

        if not error and user:
            error = delete_alg(algs, user, benchmark_id)

            if not error:
                cache.clear()

        return {'error': error}


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
        args = get_options(['file', 'benchmark_id', 'algs', 'alg_name', 'report', 'dimension', 'mobile', 'libcharts'])
        error = is_error_in_args(args)
        libcharts = args.get("libcharts", "hc")
        data = {}
        result = {}
        benchmark_id = args['benchmark_id']
        dimension = args['dimension']
        old_algs = set()
        new_algs = set()

        report_module, error = get_report(args['report'], benchmark_id)

        if not error:
            bench = get_benchmark(benchmark_id)

        if args['algs'] and not error:
            data, error = read_data_alg(benchmark_id, args['algs'])
            old_algs = set(data['alg'].tolist())

        if args['file'] and not error:
            fname = tmpfile(args['file'])
            alg_name = args['alg_name']
            data_local, error = read_benchmark_data(alg_name, fname, bench)

            if not error:
                new_algs = set(data_local['alg'].tolist())
                common_alg = new_algs.intersection(old_algs)

                if common_alg:
                    error = 'Algorithms \'{}\' were already in the database'.format(", ".join(common_alg))

            if not error:
                data = concat_df(data, data_local)

        if not args['file'] and not args['algs']:
            error = 'Error: without reference algorithms the file is mandatory'

        if not error:
            # Sort by categories
            categories = sorted(bench['categories'], key=lambda cat: cat.position)
            milestones = bench['milestones_required']
            dimension = args['dimension']
            libplot = load_charts_library(libcharts)
            libplot.init()
            tables_idx, tables_titles, tables_df = report_module.create_tables(data, categories, milestones, dimension)
            tables = {'idx': tables_idx, 'titles': tables_titles, 'tables': tables_df}
            figures_json = report_module.create_figures(data, categories, milestones, libplot=libplot, dimension=dimension, mobile=args['mobile'])
            result.update({'tables': tables})
            result.update(figures_json)

        result.update({'error': error})
        return result


api.add_resource(Benchmark, '/benchmarks')
api.add_resource(BenchmarkToken, '/benchmarks/<token>')
api.add_resource(Algs, '/algs/<int:benchmark_id>/<int:dimension>')
api.add_resource(AlgsUsers, '/algs')
api.add_resource(Compare, '/compare')
api.add_resource(Delete, '/delete')


@app.route('/')
def index():
    return send_file('static/index.html')


@app.route('/update')
def update():
    return send_file('static/login.html')


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
        args = get_options(['username', 'password'])
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
        args = get_options(['token', 'file', 'benchmark_id', 'alg_name'])
        checks = ['token', 'benchmark_id']
        alg_name = args['alg_name'].upper()
        bench = None
        error = ''

        new_algs = []
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
            new_algs = data_local['alg'].unique().tolist()
            error = write_proposal_data(data_local, user, bench)

            if not error:
                cache.clear()

        result.update({'error': error, 'new_algs': new_algs, 'new_algs_str': ",".join(new_algs)})

        return result


api.add_resource(Login, '/login')
api.add_resource(Store, '/store')

if __name__ == '__main__':
    init_db(db)
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
