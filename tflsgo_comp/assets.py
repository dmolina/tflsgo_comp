import logging
from webassets import Bundle, Environment
from webassets.script import CommandLineEnvironment
        
bundles = {
    'home_js_libs': Bundle(
        'js/lib/jquery-3.2.1.min.js',
        'js/lib/bokeh-0.12.13.min.js',
        'js/lib/bokeh-api-0.12.13.min.js',
        'js/lib/bokeh-tables-0.12.13.min.js',
        'js/lib/bokeh-widgets-0.12.13.min.js',
        'js/lib/highcharts.js',
        'js/lib/exporting.js',
        'js/lib/offline-exporting.js',
        'js/lib/d131946008.js',
        'js/lib/popper.min.js',
        'js/lib/bootstrap.min.js',
        filters='jsmin',
        output='js/index_lib.js'),
    'home_js': Bundle(
        'js/lib/vue.js',
        'js/runcommon.js',
        'js/run.js',
        filters='jsmin',
        output='js/index.js'),
    'login_js_libs': Bundle(
        'js/lib/jquery-3.2.1.min.js',
        'js/lib/underscore.js',
        'js/lib/popper.min.js',
        'js/lib/bootstrap.min.js',
        filters='jsmin',
        output='js/login_lib.js'),
    'login_js':  Bundle(
        'js/lib/vue.js',
        'js/runcommon.js',
        'js/runlogin.js',
        filters='jsmin',
        output='js/login.js'),
    'home_css': Bundle(
        'css/lib/bokeh-widget-0.12.13.min.css',
        'css/lib/bokeh-0.12.13.min.css',
        'css/lib/bootstrap_celurian.min.css',
        'css/style.css',
        filters='cssmin',
        output='css/index.css'),
    'login_css': Bundle(
        'css/lib/bootstrap_celurian.min.css',
        'css/style.css',
        filters='cssmin',
        output='css/login.css')
    # 'home_css': Bundle(
    #     'css/lib/reset.css',
    #     'css/common.css',
    #     'css/home.css',
    #     output='gen/home.css'),

    # 'admin_js': Bundle(
    #     'js/lib/jquery-1.10.2.js',
    #     'js/lib/Chart.js',
    #     'js/admin.js',
    #     output='gen/admin.js'),

    # 'admin_css': Bundle(
    #     'css/lib/reset.css',
    #     'css/common.css',
    #     'css/admin.css',
    #     output='gen/admin.css')
}


def gen_static():
    # Setup a logger
    log = logging.getLogger('webassets')
    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.DEBUG)
    assets_env = Environment()
    assets_env.directory = "static/"
    assets_env.debug = True
    assets_env.register(bundles)
    cmdenv = CommandLineEnvironment(assets_env, log)
    # This would also work
    cmdenv.build()


if __name__ == '__main__':
    gen_static()
