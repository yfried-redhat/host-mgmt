import argparse
import os
import sys
import yaml

from eventool import logger
from eventool import ha_manage
from eventool import hosts
from eventool import pcs
from eventool import ssh_cmds
from eventool import servicemgmt


HOSTS_CONF = os.environ.get("HOSTS_CONF", "/etc/eventool/hosts_conf.yaml")
LOG = logger.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("target",
                        help="remote host: ip, FQDN, or alias for a "
                             "single host. host_role is also possible to "
                             "work on "
                             "multiple matching hosts")
    subparse = parser.add_subparsers()

    # scripts
    script = subparse.add_parser("script", help="run script on host using "
                                                "interpreter")
    script.add_argument("interpreter",
                        help="program to execute script with")
    script.add_argument("script",
                        help="Path to script")
    script.set_defaults(func=script_exec)

    raw = subparse.add_parser("raw",
                              help="send the command directly to host(s)")

    raw.add_argument("command", nargs='*',
                     help="send the command directly to host(s)",
                     default=None)
    raw.set_defaults(func=raw_exec)

    service = subparse.add_parser('service', help="service help")
    service.add_argument("op",
                         help="operation to execute on service")
    service.add_argument("service",
                         help="service to work on")
    service.set_defaults(func=service_exec)

    pcs = subparse.add_parser('pcs', help="service help")
    pcs.add_argument("op",
                         help="operation to execute on service")
    pcs.add_argument("service", nargs='?',
                     help="service to work on")
    pcs.set_defaults(func=pcs_exec)
    ha = subparse.add_parser('ha_manage', help="service help")
    ha.add_argument("op",
                         help="operation to execute on service")
    ha.add_argument("service", nargs='?',
                     help="service to work on")
    ha.set_defaults(func=ha_exec)



    # TODO(yfried): add this option to parse lists
    # parser.add_argument("--hosts",
    #                     help="a list of remote hosts. ip, FQDN, aliases, "
    #                          "and/or types are possible",
    #                     host_role=list,
    #                     default=None)

    return parser.parse_args()


def load_conf_file(path=HOSTS_CONF):
    with open(path) as conf_data:
        json_conf = yaml.load(conf_data)

    return hosts.Hosts(json_conf)


def service_exec(args):
    target = args.target
    service = args.service
    print getattr(servicemgmt.ServiceMgmt(target.ssh), args.op)(
        service)


def pcs_exec(args):
    target = args.target
    to_args = []
    if args.service:
        to_args.append(args.service)
    print getattr(pcs.PCSMgmt(target.ssh), args.op)(*to_args)


def ha_exec(args):
    service = args.service
    ha_hosts = args.target
    vips = args.conf.find_hosts("vip")
    print getattr(ha_manage.HAmanager(ha_hosts, vips), args.op)(service)


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


def main():
    hosts_from_conf = load_conf_file()
    args = parse_arguments()
    args.conf = hosts_from_conf
    args.target = args.conf.find_hosts(args.target)
    args.func(args)

if __name__ == "__main__":
#     hosts_from_conf = load_conf_file()
#     args = parse_arguments()
#     target = hosts_from_conf.find_hosts(args.target)
    sys.exit(main())