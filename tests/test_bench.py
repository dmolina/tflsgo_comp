from tflsgo_comp.models import Benchmark, init_db

def test_bench_model(db):
    init_db(db)
    benchs = db.session.query(Benchmark).all()
    assert len(benchs) == 1
