from tempfile import NamedTemporaryFile


def tmpfile(file_data):
    """
    Return the temporal file.

    :param file_data: file.

    """
    tmp = NamedTemporaryFile(suffix=".xls")
    tmp.close()
    file_data.save(tmp.name)
    return tmp.name


def is_error_in_args(args):
    options = ['file', 'benchmark_id']

    if 'file' not in args and 'algs' not in args:
        return 'Not reference algorithms and file missing'

    return ""
