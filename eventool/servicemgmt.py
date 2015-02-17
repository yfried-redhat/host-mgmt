import time

from eventool import logger
from eventool import ssh_cmds
from eventool import parsers


LOG = logger.getLogger(__name__)


class ServiceMgmt(ssh_cmds.tmp_cmd):
    CMD = "systemctl {op} {service}"

    @parsers.add_argument(dest="service")
    @parsers.cli_choice(parser="service", subparser="op")
    @ssh_cmds.command_decorator
    def stop(self, service):
        """Stops service on node

        :param service: service to stop
        """
        return self.CMD.format(op='stop', service=service), self._empty_parser

    @parsers.add_argument(dest="service")
    @parsers.cli_choice(parser="service", subparser="op")
    @ssh_cmds.command_decorator
    def start(self, service):
        """Starts service on node

        :param service: service to start
        """
        return self.CMD.format(op='start', service=service), self._empty_parser

    # TODO(yfried): add cli decorators
    def restart(self, service, timeout=10):
        """Restarts service on node

        :param service: service to restart
        :param timeout: timeout to wait for service
        """   
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

    @ssh_cmds.command_decorator
    def state(self, service):
        """Sends "systemctl show <service>"

        Evaluates the status of the service based on the "ActiveState" field

        :param service: service to query
        :return: status: Known values ['active', 'failed', 'inactive']
        """

        cmd = self.CMD.format(op='show', service=service)
        return cmd, self._status_parser

    # no @command_decorator because we are executing another command
    @parsers.add_argument(dest="service")
    @parsers.cli_choice(parser="service", subparser="op")
    def status(self, service):
        """Evaluates the status of the service based on the "ActiveState" field

        :param service: service to query
        :return: status: Known values ['active', 'failed', 'inactive']
        """
        return self.state(service)
