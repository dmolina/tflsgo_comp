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

    if not args['file'] and ('algs' not in args or not args['algs']):
        return 'When there is not selected algorithms the file is mandatory'

    return ""
