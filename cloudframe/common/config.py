
try:
    import configparser as ConfigParser
except Exception:
    import ConfigParser

import os
import yaml

FAAS_CONFIG_PATH = '/root/faas/config/'
FAAS_UPLOAD_FOLDER = '/root/faas/uploads/'
FAAS_PIPELINE_PATH = '/root/faas/pipeline/'


class HostConfig(object):
    def __init__(self, filename):
        if not os.path.exists(filename):
            raise Exception('File not exist.')
        self.filename = filename
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.filename)

    def _get_hostnum(self):
        return self.config.getint('default', 'host_num')

    def _get_hostinfo(self, host_id):
        host = 'host' + str(host_id)
        section = self.config.items(host)
        host_info = {}
        host_info['host_ip'] = self.config.get(host, 'host_ip')
        host_info['host_par'] = host_info['host_ip']
        for item in section:
            if item[0] != 'host_ip':
                host_info['host_par'] += ' ' + item[0] + '=' + item[1]
        return host_info

    def get_host_info(self):
        host_global = {}
        host_global['registry'] = self.config.get('default', 'registry')
        host_global['min_port'] = self.config.getint('default', 'min_port')
        host_global['max_port'] = self.config.getint('default', 'max_port')

        num = self._get_hostnum()
        hosts = []
        for index in range(num):
            hosts.append(self._get_hostinfo(index + 1))
        return hosts, host_global


def get_faas_buildinfo(filename, resource):
        fo = open(filename, 'r')
        faas_input = yaml.load(fo)
        fo.close()
        resource['image_name'] = faas_input['image_name']
        resource['image_tag'] = faas_input['image_tag']
