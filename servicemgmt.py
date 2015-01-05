import time
import logger
#
# import abc
#
LOG = logger.getLogger(__name__)
#
#
# # class CMDMgmt(object):
#
# @staticmethod
#     def cmd(self, *args, **kwargs):
#         pass
#
#     @staticmethod
#     def parse(self, cmd, code, out, err, *args, **kwargs):
#         if code:
#             LOG.warn("cmd: '{cmd}' Returned with error code: {code}. "
#                      "msg: {msg}".
#                      format(cmd=cmd, code=code, msg=err))
#         LOG.info(out)
#         return out, err
#
#
#
#
#
# # class ServiceMgmt(object):
#
#     def __init__(self, ssh_client):
#         super(ServiceMgmt, self).__init__()
#
#     # def __getattr__(self, name):
#     #     service_cmds = ["start", "stop", "status", "disable", "enable"]
#     #     if name in service_cmds:
#     #         # TODO(yfried): implement commands
#     #         return self.build_cmd(name)
#     #     raise AttributeError(name)
#
#     # def gen_method(self, name):
#     #     def self.build_cmd(*args, **kwargs)
#     #         pass
#     #     return
#
#     @abc.abstractmethod
#     def build_cmd(self, cmd, service):
#         pass
#
#     def send_cmd
#
#
# # class ServiceMgmtRHEL(ServiceMgmt):
# #     CMD = None
# #
# #     def build_cmd(self, cmd, service):
# #         return self.CMD.format(cmd=cmd, service=service)
# #
# #
# # class Systemd(ServiceMgmtRHEL):
# #     CMD = "systemclt {cmd} {service}"
# #
# #
# # class Sysvinit(ServiceMgmtRHEL):
# #     CMD = "service {service} {cmd}"

CMD = "systemctl {op} {service}"


def exec_cmd(exc, op, service):
    code, out, err = exc(CMD.format(op=op, service=service))
    if code != 0:
        # TODO(yfried): add a better exception
        raise Exception('failure %d running systemctl show for %r: %s'
                        % (code, service, err))
    else:
        LOG.info(out)
        return out


# copied ansible-modules-core/system/service.py
def get_systemd_status_dict(out):
    key = None
    value_buffer = []
    status_dict = {}
    for line in out.splitlines():
        if not key:
            key, value = line.split('=', 1)
            # systemd fields that are shell commands can be multi-line
            # We take a value that begins with a "{" as the start of
            # a shell command and a line that ends with "}" as the end of
            # the command
            if value.lstrip().startswith('{'):
                if value.rstrip().endswith('}'):
                    status_dict[key] = value
                    key = None
                else:
                    value_buffer.append(value)
            else:
                status_dict[key] = value
                key = None
        else:
            if line.rstrip().endswith('}'):
                status_dict[key] = '\n'.join(value_buffer)
                key = None
            else:
                value_buffer.append(value)

    return status_dict


def status(exc, service):
    return state(exc, service)


def state(exc, service):
    """Sends "systemctl show <service>" and evaluates the status of the
    service based on the "ActiveState" field

    :param exc: execution method
    :param service: service to query
    :return: status: Known values ['active', 'failed', 'inactive']
    """
    out = exec_cmd(exc, 'show', service)
    d = get_systemd_status_dict(out)
    if d.get("ActiveState"):
        return d.get("ActiveState")
    else:
        # TODO(yfried): add a better exception
        raise Exception('No ActiveState value in systemctl show output for %r'
                        % service)


def stop(exc, service):
    return exec_cmd(exc, 'stop', service)


def start(exc, service):
    return exec_cmd(exc, 'start', service)


def restart(exc, service, timeout=10):
    stop(exc, service)
    time.sleep(timeout)
    return start(exc, service)