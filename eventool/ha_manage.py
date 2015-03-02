from eventool import pcs
from eventool import ssh_cmds


class HAmanager(object):
    def __init__(self, ha_hosts):
        super(HAmanager, self).__init__()
        self._ha_hosts = ha_hosts

    def get_pcs_client(self):
        """Gets a PCS host to retrieve pcs data from """
        host = self._ha_hosts[0]
        return pcs.PCSMgmt(host.ssh)

    def get_vip(self, service):
        """ Gets :service vip from from conf

        not needed if vip can be retrieved from PCS

        :param service:
        :return:
        """
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

    @ssh_cmds.cli_choice(parser="ha", handler="op")
    def find_service(self, service):
        """
        search order:
        1. clone
        2. regular service

        :param service:
        :return:
        """
        OS_prefix = "openstack-"

        proj = service[len(OS_prefix):] if service.startswith(OS_prefix) \
            else service
        proj = proj.split("-")[0]

        pcs_client = self.get_pcs_client()
        clones = pcs_client.find_clone(service)
        if clones:
            clone = clones.pop()
            resources = pcs_client.get_active_resources(clone)
            if len(resources) > 1:
                node = pcs_client.get_vip_dest(proj)
            elif resources:
                node = pcs_client.get_resource_node(resources.pop())
            else:
                # TODO(yfried): better exception
                raise Exception("no active resources found"
                                " for clone %s" % service)
            return self._get_node(node)
        # TODO(yfried): better exception
        raise Exception("no clones found for service '%s'" % service)

    def _get_node(self, hostname):
        [node] = [n for n in self._ha_hosts
                  if n.is_host(hostname)
                  or n.is_host(pcs.PCSMgmt.strip_node_name(hostname))]
        return node