import json
import argparse

import hosts
import logger


HOSTS_CONF = "conf.json"
LOG = logger.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser()
    first = parser.add_argument_group()
    first.add_argument("target",
                        help="remote host: ip, FQDN, or alias for a "
                             "single host. host_role is also possible to work on "
                             "multiple matching hosts")
    raw = parser.add_argument_group('raw').add_mutually_exclusive_group()
    raw.add_argument("--script", nargs=2,
                        help="run script on host",
                        default=None)
    raw.add_argument("--raw", nargs='*',
                        help="send the command directly to host(s)",
                        default=None)
    service = parser.add_subparsers()
    # parser.add_argument("command", )
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


def main():
    hosts_from_conf = load_conf()
    args = parse_arguments()
    target = hosts_from_conf.find_hosts(args.target)
    if args.raw:
        cmd = " ".join(args.raw)
        send_cmd(target, cmd)
    elif args.script:
        send_script(target, *args.script)



if __name__ == "__main__":
    main()