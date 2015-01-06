import functools
import time

from eventool import logger


LOG = logger.getLogger(__name__)

CMD = "systemctl {op} {service}"


def log_cmd(op, no_ouput=False):
    def _decorator(f):
        @functools.wraps(f)
        def logged_cmd(*args, **kwargs):
            service = kwargs.get('service') or args[-1]
            cmd = CMD.format(service=service, op=op)
            LOG.info('executing cmd: %s' % cmd)
            out = f(*args, **kwargs)
            if no_ouput:
                out = True
            LOG.info(out)
        return logged_cmd
    return _decorator


def exec_cmd(exc, op, service):
    code, out, err = exc(CMD.format(op=op, service=service))
    if code != 0:
        # TODO(yfried): add a better exception
        raise Exception('failure %d running systemctl show for %r: %s'
                        % (code, service, err))
    else:
        LOG.debug(out)
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


# no @log_cmd because we are executing another command
def status(exc, service):
    return state(exc, service)


@log_cmd(op='show')
def state(exc, service):
    """Sends "systemctl show <service>"

    Evaluates the status of the service based on the "ActiveState" field

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


@log_cmd(op='stop', no_ouput=True)
def stop(exc, service):
    return exec_cmd(exc, 'stop', service)


@log_cmd(op='start', no_ouput=True)
def start(exc, service):
    return exec_cmd(exc, 'start', service)


def restart(exc, service, timeout=10):
    stop(exc, service)
    time.sleep(timeout)
    return start(exc, service)