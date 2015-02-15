import collections
import json
from eventool import ssh_cmds
from eventool import logger
import xmltodict
# from lxml import etree as xml_parser
from xml.dom import minidom as xml_parser

LOG = logger.getLogger(__name__)


class PCSMgmt(ssh_cmds.tmp_cmd):

    def __init__(self, ssh):
        super(PCSMgmt, self).__init__(ssh)
        self._dict_xml = None
        self._cluster = None
        # self._haproxy_conf = None

    @property
    def cluster(self):
        self._cluster = self._cluster or self.status_xml()
        return self._cluster

    # @property
    # def haproxy(self):
    #     self._haproxy_conf = self._haproxy_conf or self._get_haproxy_conf()
    #     return self._haproxy_conf

    # @ssh_cmds.command_decorator
    # def _get_haproxy_conf(self,):
    #     cmd = "cat /etc/haproxy/haproxy.cfg"
    #     return cmd, HAProxy


    @ssh_cmds.cli_choice(parser="pcs", handler="op")
    @ssh_cmds.command_decorator
    def status(self):
        cmd = "pcs status"
        return cmd, self._noop_parser

    @ssh_cmds.cli_choice(parser="pcs", handler="op")
    @ssh_cmds.command_decorator
    def status_xml(self):
        cmd = "crm_mon -X"
        return cmd, self._parse_xml

    def _parse_xml(self, raw_xml):
        self._dict_xml = xmltodict.parse(raw_xml)
        # return xml_parser.parseString(raw_xml)
        return xml_parser.parseString(raw_xml)

    def find_service_node(self, service):
        resources = self.find_resource(service)
        if not resources:
            # TODO(yfried): replace with a better exception
            raise Exception("resource {0} NotFound".
                            format(service))
        if len(resources) > 1:
            # TODO(yfried): replace with a better exception
            raise Exception("Found multiple matches for resource {s}".
                            format(service))

        resource = resources.pop()
        [node] = resource.getElementsByTagName("node")
        return node.getAttribute("name")

    def get_vip_dest(self, vip):
        vip_prefix = "ip-"
        vips = self.find_resource(vip, exact_match=False)
        vip_resource = vips.pop()
        [node] = vip_resource.getElementsByTagName("node")
        return node.getAttribute("name")

    @staticmethod
    def strip_node_name(name):
        prefix = "pcmk-"
        assert name.startswith(prefix)
        return name[len(prefix):]

    @staticmethod
    def _find_in_tree(root, tag, id, exact=True):
        match = "__eq__" if exact else "__contains__"
        return [r for r in root.getElementsByTagName(tag)
                if getattr(r.getAttribute("id"), match)(id)]

    def find_clone(self, service):
        TAG = "clone"
        service = "%s-clone" % service
        x_list = self._find_in_tree(self.cluster, TAG, service)
        if len(x_list) > 1:
            # TODO(yfried): replace with a better exception
            raise Exception("Found multiple matches for clone {s}".
                            format(service))
        return x_list

    def find_resource(self, resource_id, exact_match=True):
        """

        :param resource_id: name of the resource
        :param exact_match: if False - return any resource whose name
        contains the :resource_id
        :return:
        """
        TAG = "resource"
        x_list = self._find_in_tree(self.cluster, TAG, resource_id,
                                    exact=exact_match)
        return x_list

    def cluster_nodes(self):
        out = self.cluster.get("nodes")["node"]
        print json.dumps(out)


# class HAProxy(object):
#     def __init__(self, raw_file):
#         super(HAProxy, self).__init__()
#         self._services = {}
#         for block in raw_file.split('\n\n'):
#             if not block.startswith("listen"):
#                 continue
#             lines = block.splitlines()
#             _listen, service = lines.pop(0).split(" ", 1)
#             assert service not in self._services
#             serv = {}
#             splitlines = [l.strip().split() for l in lines]
#             serv["vips"] = [a[1].split(":", 1)[0] for a in splitlines
#                             if a[0] == "bind"]
#             serv["hosts"] = [a[1].rsplit('-', 1)[-1] for a in splitlines
#                              if a[0] == "server"]
#             self._services[service] = serv
#
#     def __getitem__(self, item):
#         try:
#             return self._services[item]
#         except KeyError as err:
#             if not err.args:
#                 err.args = ('',)
#             err.args = (err.args[0] + "service {s} not in ha_proxy".
#                         format(s=item),) + err.args[1:]
#             raise

