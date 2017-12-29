"""
This functions contains all models from the database.
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
import importlib

# For authentication
import hashlib
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)


import numpy as np

db = SQLAlchemy()

# association table
bench_report = db.Table('bench_report', db.Model.metadata,
                        db.Column('bench_id', db.ForeignKey('benchmark.id'),
                                  primary_key=True),
                        db.Column('report_id', db.ForeignKey('report.id'),
                                  primary_key=True))


class Benchmark(db.Model):
    """
    Model wih the list of benchmarks:

    attributes:

    - name : Short name.
    - description: Description of the table.
    - nfuns : Number of functions
    - dimension : dimensionality
    - runs : maximum number of runs
    """
    id = db.Column(db.Integer, primary_key=True)
    # Name of the benchmark to use
    name = db.Column(db.String(20), unique=True, nullable=False, index=True)
    # Title of the benchmark to use
    title = db.Column(db.String(20), unique=True, nullable=False)
    # Description of the benchmark
    description = db.Column(db.Text, default="")
    # Num of Functions
    nfuns = db.Column(db.Integer, nullable=False)
    # table name
    data_table = db.Column(db.String(20), unique=True,  nullable=False)
    # Number of example data
    example = db.Column(db.String(20), unique=True, nullable=False)
    # many to many Benchmark<->Report
    reports = db.relationship('Report', secondary=bench_report,
                              back_populates='benchmarks')

    __table_args__ = (
        db.CheckConstraint(nfuns > 0, name='nfuns_must_positive'),
    )

    def __repr__(self):
        return self.name


class Dimension(db.Model):
    """Number of dimensions possible for the relative benchmark."""
    __tablename__ = "dimension"
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False, unique=True, index=True)
    benchmark_id = db.Column(db.Integer, db.ForeignKey("benchmark.id"),
                             nullable=False)
    benchmark = db.relationship("Benchmark", lazy="joined", cascade='all,delete',
                                backref=db.backref("dimensions", uselist=True))

    def __repr__(self):
        return "{}: ({})".format(self.benchmark.name, self.value)

    __table_args__ = (
        db.CheckConstraint(value > 0, name='value_must_positive'),
    )


class Report(db.Model):
    """Type of report possible for the relative benchmark."""
    __tablename__ = "report"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, nullable=False, unique=True)
    filename = db.Column(db.String(200), nullable=False, unique=True)
    benchmarks = db.relationship("Benchmark",
                                 secondary="bench_report",
                                 back_populates='reports')

    def __repr__(self):
        return "{}".format(self.name)


class Milestone(db.Model):
    """Number of dimensions possible for the relative benchmark."""
    __tablename__ = "milestone"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False, unique=True)
    value = db.Column(db.Integer, nullable=False, unique=True)
    required = db.Column(db.Boolean, default=True)
    benchmark_id = db.Column(db.Integer, db.ForeignKey("benchmark.id"),
                             nullable=False)
    benchmark = db.relationship("Benchmark", cascade='all,delete',
                                backref=db.backref("milestones", uselist=True))

    def __repr__(self):
        return "{}: ({})".format(self.benchmark.name, self.value)

    __table_args__ = (
        db.CheckConstraint(value > 0, name='value_must_positive'),
    )


class CategoryFunction(db.Model):
    """Group the category of functions for each benchmark.
     Parameters:
     - category: name of the category
     - functions: list of functions, separated by commas.
     """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False, index=True)
    functions_str = db.Column(db.String(80), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    benchmark_id = db.Column(db.Integer, db.ForeignKey("benchmark.id"),
                             nullable=False)
    benchmark = db.relationship("Benchmark", cascade='all,delete',
                                backref=db.backref("categories", uselist=True))

    def functions(self):
        return self.functions_str.split(',')

    def __repr__(self):
        return "{}: ({})".format(self.benchmark.name, self.name,
                                 self.functions_str)

    __table_args__ = (
        db.CheckConstraint(position > 0, name='value_must_positive'),
    )


class CEC2013Data(db.Model):
    """
    Table that stores for each algorithm
    """
    __tablename__ = "cec2013lsgo"
    id = db.Column(db.Integer, primary_key=True)
    alg = db.Column(db.String(20), nullable=False)
    milestone = db.Column(db.String(5), nullable=False)
    dimension = db.Column(db.Integer, default=1000)

    F1 = db.Column(db.Float, nullable=False)
    F2 = db.Column(db.Float, nullable=False)
    F3 = db.Column(db.Float, nullable=False)
    F4 = db.Column(db.Float, nullable=False)
    F5 = db.Column(db.Float, nullable=False)
    F6 = db.Column(db.Float, nullable=False)
    F7 = db.Column(db.Float, nullable=False)
    F8 = db.Column(db.Float, nullable=False)
    F9 = db.Column(db.Float, nullable=False)
    F10 = db.Column(db.Float, nullable=False)
    F11 = db.Column(db.Float, nullable=False)
    F12 = db.Column(db.Float, nullable=False)
    F13 = db.Column(db.Float, nullable=False)
    F14 = db.Column(db.Float, nullable=False)
    F15 = db.Column(db.Float, nullable=False)

    # Add the constraint in a loop
    __table_args__ = tuple([db.CheckConstraint('F{} > 0'.format(f),
                                               name='value_{}_must_be_positive'.format(f)) for f in
                            range(1, 16)] + [db.CheckConstraint(dimension > 0,
                                                                name='dimension_must_be_positive')])

    def __repr__(self):
        return self.name


def init_db(db):
    db.create_all()

    if Benchmark.query.all():
        return

    bench = Benchmark(name="CEC2013LSGO", title="CEC'2013 Large Scale Global Optimization", nfuns=15, description="""
Benchmark for the Large Scale Global Optimization competitions.
        """, data_table="cec2013lsgo", example="example_cec2013")
    db.session.add(bench)
    db.session.add(Dimension(value=1000, benchmark=bench))
    db.session.add(Report(name="cec2013_classical", filename="report_cec2013",
                          description="Classic Benchmark for LSGO (F1 criterion)", benchmarks=[bench]))

    db.session.add(Report(name="test", filename="report_test",
                          description="Test", benchmarks=[bench]))

    # Create milestone with required and optional
    milestones_required = np.array([1.2e5, 6e5, 3e6], dtype=np.int32)
    milestones_optional = np.linspace(3e5, 3e6, 10, dtype=np.int32)
    milestones = np.unique(np.append(milestones_optional, milestones_required))

    def f(x):
        return x in milestones_required

    fv = np.vectorize(f)
    required = fv(milestones)

    for mil, req in zip(milestones, required):
        mil_str = "{:.1E}".format(mil)
        db.session.add(Milestone(name=mil_str, value=int(mil), required=req,
                                 benchmark=bench))

    categories = [
        {'name': 'Unimodal', 'functions': '1,2,3'},
        {'name': 'Functions with a separable subcomponent', 'functions': '4,5,6,7'},
        {'name': 'Functions with no separable subcomponents', 'functions': '8,9,10,11'},
        {'name': 'Overlapping Functions', 'functions': '12,13,14'},
        {'name': 'Non-separable Functions', 'functions': '15'}
        ]

    for i, cat in enumerate(categories):
        cat = CategoryFunction(name=cat['name'], functions_str=cat['functions'], position=i+1, benchmark=bench)
        db.session.add(cat)

    # User add
    user = User(username='tflsgo@gmail.com')

    with open("admin_passwd.txt") as file:
        pwd = file.readlines()[0].strip()

    user.hash_password(pwd)
    db.session.add(user)
    db.session.commit()


def get_class_by_tablename(tablename):
    """Return class reference mapped to table.

    :param tablename: String with name of table.
    :return: Class reference or None.
    """
    for c in db.Model._decl_class_registry.values():
        if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
            return c


def get_results(query):
    return [row.__dict__ for row in query.all()]


def get_benchmarks():
    """
    Returns all benchmarks.
    """
    bench_data = db.session.query(Benchmark).options(joinedload("dimensions"), joinedload("milestones"), joinedload("reports")).all()
    benchs = {bench.id: {'id': bench.id, 'description': bench.description, 'name':
                         bench.name, 'title': bench.title,
                         'example': bench.example,
                         'dimensions': [dim.value for dim in bench.dimensions],
                         'reports': [{'name': report.name, 'description': report.description} for report in bench.reports]}
              for bench in bench_data}
    return benchs


def get_benchmark(benchmark_id):
    """
    Returns all benchmarks.

    :param benchmark_id: benchmark id
    """
    bench = db.session.query(Benchmark).filter_by(id=benchmark_id).options(joinedload("dimensions"), joinedload("milestones"), joinedload("categories")).one()
    milestones = bench.milestones

    bench_data = {'id': bench.id, 'description': bench.description,
                  'nfuns': bench.nfuns, 'name': bench.name,
                  'title': bench.title, 'dimensions': [dim.value for dim
                                                       in bench.dimensions],
                  'milestones_required': [mil.value for mil in milestones if mil.required],
                  'all_milestones': [mil.value for mil in milestones if not mil.required],
                  'categories': [cat for cat in bench.categories]}
    return bench_data


def get_alg(bench_id, dimension):
    """
    Returns the list of algorithms in comparisons
    """
    tablenames = db.session.query(Benchmark.data_table).filter_by(id=bench_id).all()

    if not tablenames:
        return {'error': "Benchmark '{}' not found".format(bench_id),
                'algs': []}

    tablename, = tablenames[0]
    data = get_class_by_tablename(tablename)
    algs = db.session.query(data.alg).filter_by(dimension=dimension).all()
    return {'error': '', 'algs': algs}


def read_data_alg(benchmark_id, algs):
    """
    Read the data.

    :param benchmark_id: id from benchmark
    :param algs: alg
    :return: tuple (data, error)
    """
    bench = db.session.query(Benchmark).filter_by(id=benchmark_id).all()
    error = ''
    data = ''

    if bench:
        error = 'id \'{}\' is not a known benchmark'.format(benchmark_id)
    else:
        data_class = get_class_by_tablename(bench[0].tablename)
        data = db.session.query(data_class).filter(data_class.alg in algs)

    return data, error


def get_report(report_id, benchmark_id):
    """Return the report from the database.

    :param report_id: report_id.
    :returns: tuple (function, error)
    :rtype: tuple(function, error)
    """
    error = ''
    filename = ''
    report_module = ''

    if not report_id:
        error = 'Report is missing'
    else:
        reports = db.session.query(Report).filter(Report.name == report_id).all()

        if not reports:
            error = 'Report selected is not related with the benchmark chosen'
        else:
            filename = reports[0].filename

    if not error:
        report_name = "reports." + filename
        report_module = importlib.import_module(report_name, __name__)

    return report_module, error


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(64), nullable=False)

    def hash_password(self, password):
        code = hashlib.sha256(password.encode('utf-8')).hexdigest()
        self.password_hash = code

    def verify_password(self, password):
        code = hashlib.sha256(password.encode('utf-8')).hexdigest()
        return code == self.password_hash

    def generate_auth_token(self, secret_key, expiration=600):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')


class Algorithm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False, index=True)
    benchmark_id = db.Column(db.Integer, db.ForeignKey("benchmark.id"),
                             nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    benchmark = db.relationship("Benchmark", cascade='all,delete')
    user = db.relationship("User", cascade='all,delete',
                           backref=db.backref("algorithms", uselist=True))


def validate_user(username, password):
    user = db.session.query(User).filter_by(username=username).options(joinedload("algorithms")).first()

    if user is None:
        return None

    if not user.verify_password(password):
        return None

    return user


def validate_by_token(secret_key, token):
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user


def get_user_algs(user):
    return [alg.name for alg in user.algorithms]
