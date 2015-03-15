import argparse
import sys

import yaml

from eventool import logger
from eventool import ha_manage
from eventool import hosts
from eventool import pcs
from eventool import ssh_cmds
from eventool import servicemgmt
from eventool import version
from eventool import parsers
from eventool.parsers import hosts_parser


LOG = logger.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser()
    # parser.add_argument("target",
    #                     help="remote host: ip, FQDN, or alias for a "
    #                          "single host. host_role is also possible to "
    #                          "work on "
    #                          "multiple matching hosts")
    parser.add_argument("--version", action='version',
                        version=version.version_string())
    parser.add_argument('--debug', '-d', action='store_true',
                        default=False,
                        help='print debug messages to stderr')
    # parser.set_defaults(func=lambda: version.version_string())
    subparse = parser.add_subparsers(title="Parsers", metavar="PARSER")
    raw = subparse.add_parser("raw",
                              help="send the command directly to host(s)")
    system = subparse.add_parser('system', help="preform op on system service")
    pcs = subparse.add_parser('pcs', help="TBA")
    hosts_parser = subparse.add_parser("hosts", help="get host info")

    for _parser_name, p in subparse.choices.iteritems():
        p.add_argument("target",
                       help="remote host: ip, FQDN, or alias for a "
                            "single host. host_role is also possible to "
                            "work on "
                            "multiple matching hosts")

    # HA needs different details for TARGET
    ha = subparse.add_parser('ha_manage', help="HA related operations")

    # raw
    add_subparsers(raw, parsers.PARSERS["raw"])
    raw.set_defaults(func=raw_exec)

    # system
    add_subparsers(system, parsers.PARSERS["system"])
    system.set_defaults(func=system_exec)

    # pcs
    add_subparsers(pcs, parsers.PARSERS["pcs"])
    pcs.set_defaults(func=pcs_exec)

    # HA
    ha.add_argument("target", metavar="HA-ROLE",
                    help="Role of HA nodes")
    add_subparsers(ha, parsers.PARSERS["ha"])
    ha.set_defaults(func=ha_exec)

    # hosts
    add_subparsers(hosts_parser, parsers.PARSERS["hosts"])
    hosts_parser.set_defaults(func=hosts_exec)



    # TODO(yfried): add this option to parse lists
    # parser.add_argument("--hosts",
    #                     help="a list of remote hosts. ip, FQDN, aliases, "
    #                          "and/or types are possible",
    #                     host_role=list,
    #                     default=None)

    return parser.parse_args()


def add_subparsers(parser, parsers_dict):
    for pname, pdict in parsers_dict.iteritems():
        subparse = parser.add_subparsers(title=pname, metavar=pname.upper(),
                                         dest=pname)
        for name, details in pdict.iteritems():
            p = subparse.add_parser(name, help=details["help"])
            for argument in details.get("arguments", []):
                p.add_argument(**argument)


def system_exec(args):
    target = args.target
    service = args.service
    print getattr(servicemgmt.ServiceMgmt(target.ssh), args.op)(
        service)


def pcs_exec(args):
    target = args.target
    to_args = []
    # if args.service:
    #     to_args.append(args.service)
    print getattr(pcs.PCSMgmt(target.ssh), args.op)(*to_args)


def ha_exec(args):
    service = args.service
    ha_hosts = args.target
    print getattr(ha_manage.HAmanager(ha_hosts,
                                      args.conf.fully_active_services),
                  args.op)(service)


def raw_exec(args):
    target = args.target
    arg_names = [a["dest"] for a in
                 parsers.PARSERS["raw"]["op"][args.op]["arguments"]]
    kwargs = dict((n, getattr(args, n)) for n in arg_names)
    print getattr(ssh_cmds.RAWcmd(target.ssh), args.op)(**kwargs)


def hosts_exec(args):
    target = args.target
    h = getattr(hosts_parser.HostsParser(), args.op)(target)
    print yaml.safe_dump(h, default_flow_style=False)


def main():
    logger.hideTrace(LOG)
    args = parse_arguments()
    if args.debug:
        logger.console.setLevel(logger.logging.DEBUG)
    hosts_from_conf = hosts.Hosts()
    args.conf = hosts_from_conf
    args.target = args.conf.find_hosts(args.target)
    args.func(args)

if __name__ == "__main__":
#     hosts_from_conf = load_conf_file()
#     args = parse_arguments()
#     target = hosts_from_conf.find_hosts(args.target)
    sys.exit(main())
