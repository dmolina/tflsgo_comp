#!/usr/bin/env python
"""
Program for the Task Force in Large Scale Global Optimization.
Author: Daniel  Molina Cabrera <dmolina@decsai.ugr.es>
"""
import werkzeug
from flask import Flask, send_file, request
from flask_cors import CORS
from flask_restful import Api, Resource, reqparse

from models import db, get_alg, get_benchmarks, get_benchmark, init_db
from models import read_data_alg, get_report
from readdata import read_results_from_file, error_in_data, concat_df
from utils import tmpfile, is_error_in_args


def create_app(name, options={}):
    """
    Create the app with the database connection (using Flask-SQLAlchemy).

    :param name: name of the application
    :param options: optional number of options for the app.
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
    """
    Rest object to receive the benchmark information.
    """
    def get(self):
        """
        Return the information about benchmarks.
        """
        return {'benchmarks': get_benchmarks()}


api.add_resource(Benchmark, '/benchmarks')


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


api.add_resource(Algs, '/algs/<int:benchmark_id>/<int:dimension>')


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
        print(args['report'])
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
            categories = bench['categories']
            milestones = bench['all_milestones']
            dimension = args['dimension']
            tables_idx, tables_titles, tables_df = report_module.create_tables(data, categories, milestones, dimension)
            tables = {'idx': tables_idx, 'titles': tables_titles, 'tables': tables_df}
            figures_json = report_module.create_figures(data, categories, milestones, dimension)
            error = figures_json['error']
            divs = figures_json['divs']
            figures = figures_json['plots']
            js = figures_json['js']
            result.update({'tables': tables, 'figures': figures, 'js': js, 'divs': divs})
            # print(js)

        result.update({'error': error})
        # print(result)
        return result



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


if __name__ == '__main__':
    init_db(db)
    app.run(debug=True, port=8000)
