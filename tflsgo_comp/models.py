"""
This functions contains all models from the database.
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
db = SQLAlchemy()


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
    name = db.Column(db.String(20), unique=True, nullable=False)
    # Description of the benchmark
    description = db.Column(db.Text, default="")
    # Num of Functions
    nfuns = db.Column(db.Integer, nullable=False)
    # table name
    data_table = db.Column(db.String(20), unique=True,  nullable=False)

    __table_args__ = (
        db.CheckConstraint(nfuns > 0, name='nfuns_must_positive'),
    )

    def __repr__(self):
        return self.name


class Dimension(db.Model):
    """Number of dimensions possible for the relative benchmark."""
    __tablename__ = "dimension"
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False, unique=True)
    benchmark_id = db.Column(db.Integer, db.ForeignKey("benchmark.id"),
                             nullable=False)
    benchmark = db.relationship("Benchmark", lazy="joined", cascade='all,delete',
                                backref=db.backref("dimensions", uselist=True))

    def __repr__(self):
        return "{}: ({})".format(self.benchmark.name, self.value)

    __table_args__ = (
        db.CheckConstraint(value > 0, name='value_must_positive'),
    )



class Milestone(db.Model):
    """Number of dimensions possible for the relative benchmark."""
    __tablename__ = "milestone"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False, unique=True)
    value = db.Column(db.Integer, nullable=False, unique=True)
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
    functions_str = db.Column(db.String(80), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    benchmark_id = db.Column(db.Integer, db.ForeignKey("benchmark.id"),
                             nullable=False)
    benchmark = db.relationship("Benchmark", cascade='all,delete',
                                backref=db.backref("categories", uselist=True))

    def functions(self):
        return self.functions_str.split(',')

    def __repr__(self):
        return "{}: ({})".format(self.benchmark.name, self.category,
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
    print('create all')
    db.create_all()

    if Benchmark.query.all():
        return

    bench = Benchmark(name="CEC2013LSGO", nfuns=15, description="""
Benchmark for the Large Scale Global Optimization competitions.
        """, data_table="cec2013lsgo")
    db.session.add(bench)
    db.session.add(Dimension(value=1000, benchmark=bench))
    milestones = ["1.2e5", "6e5", "3e6"]

    for mil_str in milestones:
        mil_value = int(round(float(mil_str)))
        db.session.add(Milestone(name=mil_str, value=mil_value,
                                 benchmark=bench))


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
    bench_data = db.session.query(Benchmark).options(joinedload("dimensions"), joinedload("milestones")).all()
    benchs = {bench.id: {'id': bench.id, 'description': bench.description, 'name':
                         bench.name, 'dimensions': [dim.value for dim in bench.dimensions],
                         'milestones': [mil.name for mil in bench.milestones]} for bench in bench_data}
    return benchs


def get_alg(bench_id):
    """
    Returns the list of algorithms in comparisons
    """
    tablenames = db.session.query(Benchmark.data_table).filter_by(id=bench_id).all()

    if not tablenames:
        return {'error': "Benchmark '{}' not found".format(bench_id), 'algs': []}

    tablename, = tablenames[0]
    data = get_class_by_tablename(tablename)
    algs = db.session.query(data.alg).all()
    return {'error': '', 'algs': algs}
