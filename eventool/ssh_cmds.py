import argparse
import functools

from eventool import logger
from eventool import parsers


LOG = logger.getLogger(__name__)


def command_decorator(f):
    @functools.wraps(f)
    def execute_and_parse(self, *args, **kwargs):
        cmd, parser = f(self, *args, **kwargs)
        out = self.exec_command(cmd)
        out = parser(out) if parser else out
        # cmd_dict = dict(cmd=cmd, out=out)
        # LOG.info(self.out_format.format(pre='ouptut', prnt=out,
        #                                 allign=self.allign))
        # LOG.info(json.dumps(cmd_dict))
        # LOG.info(str(cmd_dict))
        return out
    return execute_and_parse


# TODO(yfried): name this better
class tmp_cmd(object):
    allign = 20
    out_format = '{pre:<10}:{prnt:>{allign}}'

    def __init__(self, ssh):
        super(tmp_cmd, self).__init__()
        self.executor = ssh.execute

    def exec_command(self, cmd):
        code, out, err = self.executor(cmd)
        if code != 0:
            # TODO(yfried): add a better exception
            raise Exception('failure {code:d} running: {cmd} '
                            '{err}'.format(code=code, cmd=cmd, err=err))
        return out

    @staticmethod
    def _empty_parser(output):
        """ verifies output is empty string and generates output for logging

        :param output:
        :return:
        """
        assert output == ""
        return True

    @staticmethod
    def _noop_parser(out):
        """don't parse """
        return out


# def parser_exec(parser):
#     main.PARSERS[parser]["func"]
#     def decorator(c):
#         @functools.wraps(c)
#         def class_dec(*args, **kwargs):
#             return c(*args, **kwargs)
#         return class_dec
#     return decorator


class RAWcmd(tmp_cmd):
    @parsers.add_argument(dest="input", nargs="*", default=None)
    @parsers.cli_choice(parser="raw", subparser="op")
    @command_decorator
    def command(self, input):
        """Execute a single command from input via SSH

        :param input: input to send via ssh
        :return:
        """
        if not isinstance(input, str):
            input = " ".join(input)
        return input, None

    @parsers.add_argument("path", type=argparse.FileType("rb"))
    @parsers.add_argument("interpreter")
    @parsers.cli_choice(parser="raw", subparser="op")
    def script(self, interpreter, path):
        """Execute a script on host

        :param interpreter: program that execute the script on remote host.
            examples: "bash", "python", "/bin/bash", "/user/bin/python26"
        :param path: Path to script file on local system
        :return: stdout, stderr of script execution
        """
        code, out, err = self.executor(interpreter, stdin=path)
        if code:
            LOG.warn("cmd: '{cmd}' Returned with error code: {code}. msg: {msg}".
                     format(cmd="%s %s" % (interpreter, path),
                            code=code, msg=err))
        return out, err
