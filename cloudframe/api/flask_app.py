
import logging
import os
from flask import abort, Flask, flash, jsonify, make_response, request
from six.moves import http_client
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.utils import secure_filename

from cloudframe.manager.builder import FaaSBuilder
from cloudframe.common import exception
from cloudframe.common.job import Tasks

UPLOAD_FOLDER = '/root/faas/uploads/'
ALLOWED_EXTENSIONS = set(['tar.gz', 'yaml'])

os.environ.setdefault('LOG_LEVEL', 'DEBUG')
loglevel_map = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARN': logging.WARN,
    'ERROR': logging.ERROR,
}
logging.basicConfig(
    level=loglevel_map[os.environ['LOG_LEVEL']],
    format='%(asctime)s.%(msecs)03d %(filename)s[line:%(lineno)d]'
           ' %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='/var/log/cloudframe/faas-api.log',
    filemode='a')
LOG = logging.getLogger(__name__)


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
Builder = FaaSBuilder()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/faas_build/<ver>/<res_name>', methods=['POST'])
def upload_package(ver, res_name):
    if 'faas-package' not in request.files or 'faas-desc' not in request.files:
        LOG.error('No upload FaaS package.')
        abort(http_client.BAD_REQUEST)

    faas_pkg = request.files['faas-package']
    faas_desc = request.files['faas-desc']
    if faas_pkg.filename == '' or faas_desc.filename == '':
        LOG.error('No upload FaaS package.')
        abort(http_client.BAD_REQUEST)

    if faas_pkg and allowed_file(faas_pkg.filename):
        filename = secure_filename(faas_pkg.filename)
        path = app.config['UPLOAD_FOLDER'] + res_name
        faas_pkg.save(os.path.join(path, filename))
    else:
        LOG.error('FaaS package is invalid.')
        abort(http_client.BAD_REQUEST)
    if faas_desc and allowed_file(faas_desc.filename):
        filename = secure_filename(faas_desc.filename)
        path = app.config['UPLOAD_FOLDER'] + res_name
        faas_desc.save(os.path.join(path, filename))
    else:
        LOG.error('FaaS desc is invalid.')
        abort(http_client.BAD_REQUEST)

    desc_file = app.config['UPLOAD_FOLDER'] + res_name + '/' + faas_desc
    pkg_file = app.config['UPLOAD_FOLDER'] + res_name + '/' + faas_pkg
    info = {
        'res_name': res_name,
        'faas_desc': desc_file,
        'faas_pkg': pkg_file
    }
    item = [Builder.create_pipeline, info]
    Tasks.put_nowait(item)
    return make_response(jsonify({'result': 'OK'}), http_client.OK)


@app.route('/faas_build/<ver>/<res_name>', methods=['GET'])
def get_resource(ver, res_name):
    try:
        results = Builder.get(res_name)
        return make_response(results[1], results[0])
    except exception.CloudframeException as e:
        LOG.error('GET Resource[%(res)s] failed, error info: %(error)s',
                  {'res': res_name, 'error': e.message})
        return make_response(jsonify({'error': e.message}),
                             e.code)


app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == "__main__":
    app.run()
