
from six.moves import http_client
from datetime import datetime
import logging
import os

from cloudframe.common import exception
from cloudframe.common.config import HostConfig
from cloudframe.common.config import get_faas_buildinfo
from cloudframe.common.config import FAAS_CONFIG_PATH
from cloudframe.pipeline.ans_docker import Faas

LOG = logging.getLogger(__name__)
MAX_INS = 20

RES_STATUS_DONE = 'done'
RES_STATUS_INIT = 'initializing'
RES_STATUS_DOING = 'doing'
RES_STATUS_ERROR = 'error'


class FaaSBuilder(object):
    def __init__(self, host_config, base_package):
        config_file = FAAS_CONFIG_PATH + host_config
        base_file = FAAS_CONFIG_PATH + base_package
        self.isReady = False
        if not (os.path.isfile(config_file) and os.path.isfile(base_file)):
            LOG.error('FaaSBuilder: config %(cnf)s or package %(pkg)s is invalid.',
                      {'cnf': config_file, 'pkg': base_file})
            return

        try:
            hc = HostConfig(config_file)
            rv = hc.get_host_info()
            self.hosts = rv[0]
            self.host_global = rv[1]
            self.driver = Faas(self.hosts, self.host_global['registry'], base_package)
            self.pipelines = {}
            LOG.debug('---- config info ----')
            LOG.debug('---- global: %(global)s', {'global': self.host_global})
            for host in self.hosts:
                LOG.debug('---- host: %(host)s', {'host': host})
            self.isReady = True
        except Exception as e:
            LOG.error('Read host_config(%(config)s) failed, error_info: %(error)s',
                      {'config': config_file, 'error': e})

    def get(self, res_name):
        if not self.isReady:
            raise exception.HttpError
        if res_name not in self.pipelines:
            raise exception.NotFound
        return http_client.OK, self.pipelines[res_name]

    def create_pipeline(self, info):
        if not self.isReady:
            raise exception.HttpError
        res_name = info['res_name']
        faas_desc = info['faas_desc']
        faas_pkg = info['faas_pkg']
        LOG.debug('Pipeline for %(res)s begin...', {'res': res_name})
        resource = {
            'name': res_name,
            'package': faas_pkg,
            'created_at': datetime.now(),
            'status': RES_STATUS_INIT
        }
        self.pipelines[res_name] = resource
        try:
            get_faas_buildinfo(faas_desc, resource)
            resource['status'] = RES_STATUS_DOING
            LOG.debug('Get description end, %(res)s', {'res': resource})
            self.driver.create(resource)
            resource['status'] = RES_STATUS_DONE
            resource['finished_at'] = datetime.now()
            LOG.debug('Pipeline for %(res_name)s end.', {'res_name': res_name})
            LOG.debug('Resource info: %(res)s', {'res': resource})
        except Exception as e:
            resource['status'] = RES_STATUS_ERROR
            resource['finished_at'] = datetime.now()
            LOG.error('Pipeline for %(res_name)s failed, error info: %(err)s',
                      {'res_name': res_name, 'err': e})
