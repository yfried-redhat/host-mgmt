import functools
import json
import time

from eventool import logger


LOG = logger.getLogger(__name__)


def command_decorator(f):
    @functools.wraps(f)
    def execute_and_parse(self, *args, **kwargs):
        cmd, parser = f(self, *args, **kwargs)
        out = self.exec_command(cmd)
        out = parser(out)
        # cmd_dict = dict(cmd=cmd, out=out)
        LOG.info(self.out_format.format(pre='ouptut', prnt=out,
                                        allign=self.allign))
        # LOG.info(json.dumps(cmd_dict))
        # LOG.info(str(cmd_dict))
        return out
    return execute_and_parse


class ServiceMgmt(object):
    CMD = "systemctl {op} {service}"
    allign = 20
    out_format = '{pre:<10}:{prnt:>{allign}}'

    def __init__(self, executor):
        super(ServiceMgmt, self).__init__()
        self.executor = executor

    def exec_command(self, cmd):
        # log command?

        code, out, err = self.executor(cmd)
        if code != 0:
            # TODO(yfried): add a better exception
            raise Exception('failure {code:d} running: {cmd} '
                            '{err}'.format(code=code, cmd=cmd, err=err))
        LOG.debug(out)
        return out

    @staticmethod
    def _empty_parser(output):
        assert output == ""
        return True

    @command_decorator
    def stop(self, service):
        return self.CMD.format(op='stop', service=service), self._empty_parser

    @command_decorator
    def start(self, service):
        return self.CMD.format(op='start', service=service), self._empty_parser

    def restart(self, service, timeout=10):
        self.stop(service)
        time.sleep(timeout)
        self.start(service)

    @staticmethod
    def _status_parser(out):
    # copied from:
    # ansible-modules-core/system/service.py:get_systemd_status_dict

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

        if status_dict.get("ActiveState"):
            return status_dict.get("ActiveState")
        else:
            # TODO(yfried): add a better exception
            raise Exception('No ActiveState value in systemctl show '
                            'output: {d}'.format(status_dict))



    @command_decorator
    def state(self, service):
        """Sends "systemctl show <service>"

        Evaluates the status of the service based on the "ActiveState" field

        :param service: service to query
        :return: status: Known values ['active', 'failed', 'inactive']
        """

        cmd = self.CMD.format(op='show', service=service)
        return cmd, self._status_parser

    # no @command_decorator because we are executing another command
    def status(self, service):
        return self.state(service)
