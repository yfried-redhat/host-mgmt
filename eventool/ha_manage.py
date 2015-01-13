from eventool import pcs


class HAmanager(object):
    def __init__(self, ha_hosts):
        super(HAmanager, self).__init__()
        self._ha_hosts = ha_hosts

    def get_pcs_client(self):
        """Gets a PCS host to retrieve pcs data from """
        host = self._ha_hosts[0]
        return pcs.PCSMgmt(host.ssh.execute)

    def find_service(self, service):
        pcs_client = self.get_pcs_client()
        return pcs_client.find_service(service)

    def _get_node(self, hostname):
        [node] = [n for n in self._ha_hosts
                  if n.is_host(hostname)
                  or n.is_host(pcs.PCSMgmt.strip_node_name(hostname))]