import json
import argparse

import hosts
import logger
import servicemgmt


HOSTS_CONF = "conf.json"
LOG = logger.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser()
    # first = parser.add_argument_group()
    parser.add_argument("target",
                        help="remote host: ip, FQDN, or alias for a "
                             "single host. host_role is also possible to work on "
                             "multiple matching hosts")
    subparse = parser.add_subparsers()

    # raw
    # raw = subparse.add_parser('raw')
    # # raw = parser.add_argument_group('raw').add_mutually_exclusive_group()
    # raw.add_argument("--script", nargs=2,
    #                     help="run script on host",
    #                     default=None)
    # raw.add_argument("--raw", nargs='*',
    #                     help="send the command directly to host(s)",
    #                     default=None)

    service = subparse.add_parser('service', help="service help")
    service.add_argument("op",
                         help="operation to execute on service")
    service.add_argument("service",
                         help="service to work on")
    service.set_defaults(func=service_exec)

    # TODO(yfried): add this option to parse lists
    # parser.add_argument("--hosts",
    #                     help="a list of remote hosts. ip, FQDN, aliases, "
    #                          "and/or types are possible",
    #                     host_role=list,
    #                     default=None)

    args = parser.parse_args()
    return args


def load_conf(path=HOSTS_CONF):
    with open(path) as json_data:
        json_conf = json.load(json_data)

    return hosts.Hosts(json_conf)


def service_exec(args):
    # global hosts_from_conf
    output = getattr(servicemgmt, args.op)(target.ssh.execute,
                                           args.service)
    pass

# def cmd(target, *args, **kwargs):
#     host=None
#     try:
#         host = ipaddr.IPAddress(target)
#     except ValueError:
#         host = target
#
#     if host in


def send_cmd(target, cmd=""):
    code, out, err = target.ssh.execute(cmd)
    if code:
        LOG.warn("cmd: '{cmd}' Returned with error code: {code}. msg: {msg}".
                 format(cmd=cmd, code=code, msg=err))
    LOG.debug(out)
    return out, err


def send_script(target, interpreter, script):
    code, out, err = target.ssh.execute(interpreter, stdin=open(script, "rb"))
    if code:
        LOG.warn("cmd: '{cmd}' Returned with error code: {code}. msg: {msg}".
                 format(cmd="%s %s" % (interpreter, script),
                        code=code, msg=err))
    LOG.debug(out)
    return out, err


# def main():
#     args = parse_arguments()
#     target = hosts_from_conf.find_hosts(args.target)
#     if args.raw:
#         cmd = " ".join(args.raw)
#         send_cmd(target, cmd)
#     elif args.script:
#         send_script(target, *args.script)


if __name__ == "__main__":
    # global hosts_from_conf
    hosts_from_conf = load_conf()
    args = parse_arguments()
    target = hosts_from_conf.find_hosts(args.target)
    args.func(args)