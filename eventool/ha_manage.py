from eventool import pcs


class HAmanager(object):
    def __init__(self, ha_hosts, vips):
        super(HAmanager, self).__init__()
        self._ha_hosts = ha_hosts
        self._vips = vips

    def get_pcs_client(self):
        """Gets a PCS host to retrieve pcs data from """
        host = self._ha_hosts[0]
        return pcs.PCSMgmt(host.ssh)

    def get_vip(self, service):
        VIP_SUFFIX = "public_vip"
        OS_prefix = "openstack-"

        proj = service[len(OS_prefix):] if service.startswith(OS_prefix) \
            else service
        proj = proj.split("-")[0]

        vip_alias = "_".join([proj, VIP_SUFFIX])
        vip = [v for v in self._vips if vip_alias in v.alias]
        if not vip:
            # TODO(yfried): find better exception
            raise Exception("vip '{v}' not found for service '{s}'".
                            format(v=vip_alias, s=service))
        return vip

    def find_service(self, service):
        """
        search order:
        1. clone
        2. regular service

        :param service:
        :return:
        """
        pcs_client = self.get_pcs_client()
        if pcs_client.find_clone(service):
            [vip] = self.get_vip(service)
            node = pcs_client.get_vip_dest(vip.address)
        else:
            node = pcs_client.find_service_node(service)
        return self._get_node(node)

    def _get_node(self, hostname):
        [node] = [n for n in self._ha_hosts
                  if n.is_host(hostname)
                  or n.is_host(pcs.PCSMgmt.strip_node_name(hostname))]
        return node