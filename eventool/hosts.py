from rally.common import sshutils as rally_ssh

from eventool import logger

LOG = logger.getLogger(__name__)


class Host(object):
    def __init__(self, address, user, alias="", host_role="", password=None,
                 private_key=None, os=None):

        self.address = address
        self.host_role = host_role
        self.alias = alias
        self.password = password
        self.private_key = private_key
        self.os = os
        self.user = user
        self._ssh = None

    @property
    def ssh(self):
        if not self._ssh:
            self._ssh = rally_ssh.SSH(user=self.user,
                                              host=self.address,
                                     key_filename=self.private_key,
                                     password=self.password)
        return self._ssh


class Hosts(object):
    def __init__(self, hosts_conf):
        super(Hosts, self).__init__()
        self._defaults = dict()
        self._hosts = dict()
        for attribute in ["password", "os", "private_key", "user"]:
            if hosts_conf.get(attribute):
                self._defaults[attribute] = hosts_conf.get(attribute)

        for role, hosts in hosts_conf["roles"].iteritems():
            for address, host in hosts.iteritems():
                host_init = dict(self._defaults)
                host_init.update(host)
                self._hosts[address] = Host(address=address,
                                            host_role=role,
                                            **host_init)

    def get_host_role(self, host_role):
        return [host for h, host in self._hosts.iteritems()
                if host.host_role == host_role]

    def get_alias(self, alias):
        aliased = [host for h, host in self._hosts.iteritems()
                   if host.alias == alias]
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
        host_list = self.get_host_role(target)
        if host_list:
            if len(host_list) == 1:
                return host_list[0]
            return host_list
        alias_host = self.get_alias(target)
        if alias_host:
            return alias_host

        # TODO(yfried):
        raise Exception("No hosts found")
