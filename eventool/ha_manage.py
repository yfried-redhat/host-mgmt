from eventool import parsers
from eventool import logger
from eventool import pcs


LOG = logger.getLogger(__name__)


class HAmanager(object):
    def __init__(self, ha_hosts, active_services=None):
        super(HAmanager, self).__init__()
        self._ha_hosts = ha_hosts
        self.fully_active_services = active_services or set()

    def get_pcs_client(self):
        """Gets a PCS host to retrieve pcs data from """
        host = self._ha_hosts[0]
        return pcs.PCSMgmt(host.ssh)

    def get_vip(self, service):
        """ Gets :service vip from from conf

        Deprecated: vip can be retrieved from PCS

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

    @parsers.add_argument("service")
    @parsers.cli_choice(parser="ha", subparser="op")
    def find_service(self, service):
        """Finds active node for service from HA manager

        :param service: name of clone registered in pcs
        :return:
        """
        OS_prefix = "openstack-"

        LOG.debug("Locating HA service %s" % service)
        if service in self.fully_active_services:
            # TODO(yfried): better exception
            raise Exception("%s is a fully active service" % service)
        proj = service[len(OS_prefix):] if service.startswith(OS_prefix) \
            else service
        proj = proj.split("-")[0]

        pcs_client = self.get_pcs_client()
        clones = pcs_client.find_clone(service)
        if clones:
            clone = clones.pop()
            resources = pcs_client.get_active_resources(clone)
            if len(resources) > 1:
                LOG.debug("%s is A/A service. Searching VIP for service: %s"
                          % (service, proj))
                node = pcs_client.get_vip_dest(proj)
            elif resources:
                LOG.debug("%s is A/P service. Locate active node" % service)
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