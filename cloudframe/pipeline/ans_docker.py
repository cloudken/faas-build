
import fileinput
import logging
import os
import random
import shutil

from cloudframe.common.config import FAAS_PIPELINE_PATH
from cloudframe.common.config import FAAS_CONFIG_PATH
from cloudframe.common.utils import execute

LOG = logging.getLogger(__name__)

HOST_OK = 'host ok'
HOST_ERROR = 'host error'

WORKER_LOG_LEVEL = 'DEBUG'
WORKER_LIFE_CYCLE = 60


class Faas(object):
    def __init__(self, hosts, registry_info, base_package):
        self.registry = registry_info
        self.base_package = base_package
        src_pkg = FAAS_CONFIG_PATH + self.base_package
        shutil.copy(src_pkg, FAAS_PIPELINE_PATH)
        self.hosts_ok = []
        self.hosts_error = []
        for host in hosts:
            try:
                self._check_host(host)
                self.hosts_ok.append(host)
            except Exception as e:
                LOG.error('Check host_%(host)s failed, error_info: %(error)s',
                          {'host': host['host_ip'], 'error': e})
                self.hosts_error.append(host)

    def _check_host(self, host):
        LOG.debug('Chcke host %(host)s begin...', {'host': host['host_ip']})

        # host
        # host_par = '127.0.0.1'
        host_par = host['host_par']
        base_path = FAAS_PIPELINE_PATH
        hosts_file = base_path + 'hosts'
        fo = open(hosts_file, 'w')
        fo.write("[nodes]\n")
        fo.write(host_par)
        fo.flush()
        fo.close()

        # vars
        vars_file = base_path + 'host_vars.yml'
        for line in fileinput.input(vars_file, inplace=1):
            line = line.strip()
            strs = line.split(':')
            if 'dest_host' in strs[0]:
                line = strs[0] + ': ' + host['host_ip']
            print(line)

        # check
        ans_file = base_path + 'host_check.yml'
        execute('ansible-playbook', ans_file, '-i', hosts_file,
                check_exit_code=[0], run_as_root=True)

        LOG.debug('Check host %(host)s end.', {'host': host['host_ip']})

    def create(self, resource):
        try:
            name = resource['name']
            package = resource['package']
            image = resource['image_name']
            tag = resource['image_tag']
            num = random.randint(0, len(self.hosts_ok) - 1)
            host = self.hosts_ok[num]
            self._make_package(name, package)
            self._build_image(name, image, tag, host)
        except Exception as e:
            LOG.error('Create %(res)s failed, error info: %(err)s',
                      {'res': resource['name'], 'err': e})
            raise e

    def _make_package(self, res_name, package):
        LOG.debug('Make package %(name)s begin...', {'name': res_name})

        # mkdir and copy files
        src_path = FAAS_PIPELINE_PATH
        base_path = src_path + res_name + '/'
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        base_package_file = src_path + self.base_package
        package_name = os.path.basename(package)
        shutil.copy(base_package_file, base_path)
        shutil.copy(package, base_path)
        run_sh = src_path + 'make_package.sh'
        shutil.copy(run_sh, base_path)
        run_sh = base_path + 'make_package.sh'
        dockerfile_src_path = src_path + 'faas-worker'
        dockerfile_dst_path = base_path + 'faas-worker'
        shutil.copytree(dockerfile_src_path, dockerfile_dst_path)

        # make package
        cur_dir = os.getcwd()
        os.chdir(base_path)
        execute(run_sh, self.base_package, package_name, check_exit_code=[0], run_as_root=True)
        os.chdir(cur_dir)

        # remove base_path
        # shutil.rmtree(base_path)
        LOG.debug('Make package %(name)s end.', {'name': res_name})

    def _build_image(self, res_name, image, tag, host):
        LOG.debug('Building image %(image)s:%(tag)s begin...',
                  {'image': image, 'tag': tag})

        # mkdir and copy files
        src_path = FAAS_PIPELINE_PATH
        base_path = src_path + res_name + '/'
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        src_file = src_path + 'build_vars.yml'
        shutil.copy(src_file, base_path)
        src_file = src_path + 'image_build.yml'
        shutil.copy(src_file, base_path)

        # host
        # host_str = host + ' ansible_ssh_pass=cloud ansible_become_pass=cloud'
        host_par = host['host_par']
        hosts_file = base_path + 'hosts'
        fo = open(hosts_file, 'w')
        fo.write("[nodes]\n")
        fo.write(host_par)
        fo.flush()
        fo.close()

        # vars
        build_path = base_path + 'faas-worker/'
        vars_file = base_path + 'build_vars.yml'
        for line in fileinput.input(vars_file, inplace=1):
            line = line.strip()
            strs = line.split(':')
            if 'build_path' in strs[0]:
                line = strs[0] + ': ' + build_path
            if 'registry' in strs[0]:
                line = strs[0] + ': ' + self.registry
            if 'image_name' in strs[0]:
                line = strs[0] + ': ' + image
            if 'image_tag' in strs[0]:
                line = strs[0] + ': ' + tag
            print(line)

        # build
        ans_file = base_path + 'image_build.yml'
        execute('ansible-playbook', ans_file, '-i', hosts_file,
                check_exit_code=[0], run_as_root=True)

        # remove dir
        shutil.rmtree(base_path)
        LOG.debug('Building image %(image)s:%(tag)s end.', {'image': image, 'tag': tag})
