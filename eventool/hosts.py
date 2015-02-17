import functools
import os
from eventool import sshutils
import yaml

from eventool import logger

LOG = logger.getLogger(__name__)
CONF_PATH = os.environ.get("HOSTS_CONF", "/etc/eventool/hosts_conf.yaml")


class Host(object):
    def __init__(self, address, user, alias=None, password=None,
                 private_key=None, os=None):

        self.address = address
        self.host_roles = []
        self.alias = alias or []
        self.password = password
        self.private_key = private_key
        self.os = os
        self.user = user
        self._ssh = None

    def add_roles(self, *roles):
        self.host_roles.extend(roles)

    def __str__(self):
        return self.address

    def __repr__(self):
        return "Host: address: {add} aliases: {als}".format(add=self.address,
                                                            als=self.alias)

    def is_host(self, hostname):
        return hostname == self.address or hostname in self.alias

    @property
    def ssh(self):
        if not self._ssh:
            ssh = sshutils.SSH(user=self.user,
                               host=self.address,
                               key_filename=self.private_key,
                               password=self.password)
            ssh._get_client()
            # except Exception as e:
            #     raise Exception("no connection to %s" % ssh.host)
            self._ssh = ssh

        return self._ssh


class Hosts(object):
    def __init__(self, path=CONF_PATH):
        super(Hosts, self).__init__()
        with open(path) as conf_data:
            hosts_conf = yaml.load(conf_data)
        self._defaults = dict()
        self._hosts = dict()
        for attribute in ["password", "os", "private_key", "user"]:
            if hosts_conf.get(attribute):
                self._defaults[attribute] = hosts_conf.get(attribute)

        for address, host in hosts_conf["hosts"].iteritems():
            if self._hosts.get(address):
                raise Exception("found duplicate address %s. "
                                "existing: %s" %
                                (address, self._hosts[address]))
            host_init = dict(self._defaults)
            host_init.update(host)
            self._hosts[address] = Host(address=address,
                                        **host_init)

        for role, hosts in hosts_conf["roles"].iteritems():
            for h in hosts:
                host = self.find_hosts(h)
                host.add_roles(role)

    def get_host_role(self, host_role):
        return [host for h, host in self._hosts.iteritems()
                if host_role in host.host_roles]

    def get_alias(self, alias):
        aliased = [host for h, host in self._hosts.iteritems()
                   if host.is_host(alias)]
        if len(aliased) > 1:
            raise Exception("found more than 1 host with alias")

        if len(aliased):
            return aliased[0]
        else:
            return None

    def find_hosts(self, target):
        """Finds hosts

        :param target: string to search host DB
        :return:
            Host if target matches host's id or alias
            list of Host objects if target matches host_role
            None if no match found
        """
        if target in self._hosts.keys():
            return self._hosts[target]
        alias_host = self.get_alias(target)
        if alias_host:
            return alias_host
        host_list = self.get_host_role(target)
        if host_list:
            if len(host_list) == 1:
                return host_list[0]
            return host_list

        # TODO(yfried):
        raise Exception("No hosts found: target: %s" % target)
