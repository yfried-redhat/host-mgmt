import collections
import json
from eventool import ssh_cmds
from eventool import logger
import xmltodict
from lxml import etree as xml_parser
# from xml.dom import minidom as xml_parser

LOG = logger.getLogger(__name__)


class PCSMgmt(ssh_cmds.tmp_cmd):

    def __init__(self, executor):
        super(PCSMgmt, self).__init__(executor)
        self.dict_xml = None
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


    @ssh_cmds.command_decorator
    def status(self):
        cmd = "pcs status"
        return cmd, self._noop_parser

    @ssh_cmds.command_decorator
    def status_xml(self):
        cmd = "crm_mon -X"
        return cmd, self._parse_xml

    def _parse_xml(self, raw_xml):
        self.dict_xml = xmltodict.parse(raw_xml)
        # return xml_parser.parseString(raw_xml)
        return xml_parser.fromstring(raw_xml)

    def find_service(self, service):
        resource = self.find_resource(self.cluster, service)
        node = resource.find("node")
        return node.attrib["name"]

    @staticmethod
    def strip_node_name(name):
        prefix = "pcmk-"
        assert name.startswith(prefix)
        return name[len(prefix):]

    def find_resource(self, root, resource):

        x = root.xpath("//resource[@id='%s']" % resource)
        if len(x) > 1:
            # TODO(yfried): replace with a better exception
            raise Exception("Found multiple matches for resource {s} in {r}".
                            format(s=resource, r=root.att))
        if not x:
            # TODO(yfried): replace with a better exception
            raise Exception("resource {s} NotFound in {r}".
                            format(s=resource, r=root.att))
        return x.pop()

    # def __getattr__(self, name):
    #     if name.startswith("cluster_"):
    #         key = name.split("_", 1)[-1]
    #     return super(PCSMgmt, self).__getattribute__(name)

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

