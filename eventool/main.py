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
    script = subparse.add_parser("script", help="run script on host using "
                                                "interpreter")
    raw = subparse.add_parser("raw",
                              help="send the command directly to host(s)")
    service = subparse.add_parser('service', help="preform op on service")
    pcs = subparse.add_parser('pcs', help="TBA")
    hosts_parser = subparse.add_parser("hosts", help="get host info")

    # parsers = [script, raw, service, pcs]

    for _parser_name, p in subparse.choices.iteritems():
        p.add_argument("target",
                       help="remote host: ip, FQDN, or alias for a "
                            "single host. host_role is also possible to "
                            "work on "
                            "multiple matching hosts")

    # HA needs different details for TARGET
    ha = subparse.add_parser('ha_manage', help="HA related operations")

    # scripts
    script.add_argument("interpreter",
                        help="program to execute script with")
    script.add_argument("script",
                        help="Path to script")
    script.set_defaults(func=script_exec)

    # raw
    raw.add_argument("command", nargs='*',
                     help="send the command directly to host(s)",
                     default=None)
    raw.set_defaults(func=raw_exec)

    # service
    service.add_argument("op",
                         help="operation to execute on service",
                         choices=parsers.PARSERS["service"]["op"])
    service.add_argument("service",
                         help="service to work on")
    service.set_defaults(func=service_exec)

    # pcs
    pcs.add_argument("op",
                     help="operation to execute on service",
                     choices=parsers.PARSERS["pcs"]["op"])
    # pcs.add_argument("service", nargs='?',
    #                  help="service to work on")
    pcs.set_defaults(func=pcs_exec)

    # HA
    ha.add_argument("target", metavar="HA-ROLE",
                    help="Role of HA nodes")
    ha.add_argument("op",
                    help="operation to execute on service",
                     choices=parsers.PARSERS["ha"]["op"])
    ha.add_argument("service",
                    help="service to work on")
    ha.set_defaults(func=ha_exec)

    # hosts
    hosts_parser.add_argument("op",
                    help="operation to execute on host",
                     choices=parsers.PARSERS["hosts"]["op"])

    hosts_parser.set_defaults(func=hosts_exec)



    # TODO(yfried): add this option to parse lists
    # parser.add_argument("--hosts",
    #                     help="a list of remote hosts. ip, FQDN, aliases, "
    #                          "and/or types are possible",
    #                     host_role=list,
    #                     default=None)

    return parser.parse_args()




def service_exec(args):
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
    cmd = " ".join(args.command)
    print ssh_cmds.RAWcmd(target.ssh).raw_cmd(cmd)


def script_exec(args):
    interpreter = args.interpreter
    script = args.script
    target = args.target
    code, out, err = target.ssh.execute(interpreter, stdin=open(script, "rb"))
    if code:
        LOG.warn("cmd: '{cmd}' Returned with error code: {code}. msg: {msg}".
                 format(cmd="%s %s" % (interpreter, script),
                        code=code, msg=err))
    LOG.info(out)
    return out, err


def hosts_exec(args):
    target = args.target
    h = getattr(hosts_parser.HostsParser(), args.op)(target)
    print yaml.safe_dump(h, default_flow_style=False)

def main():
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
