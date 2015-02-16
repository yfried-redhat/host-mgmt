import functools
import argparse
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
        LOG.info(self.out_format.format(pre='ouptut', prnt=out,
                                        allign=self.allign))
        # LOG.info(json.dumps(cmd_dict))
        # LOG.info(str(cmd_dict))
        return out
    return execute_and_parse


def cli_choice(parser, handler=None):
    if handler:
        parsers.PARSERS.setdefault(parser, {})
        parsers.PARSERS[parser].setdefault(handler, [])
    
    def decorator(f):
        if handler:
            name = f.func_name
            parsers.PARSERS[parser][handler].append(name)
    
        @functools.wraps(f)
        def func(self, *args, **kwargs):
            return f(self, *args, **kwargs)
        return func
    return decorator


# TODO(yfried): name this better
class tmp_cmd(object):
    allign = 20
    out_format = '{pre:<10}:{prnt:>{allign}}'

    def __init__(self, ssh):
        super(tmp_cmd, self).__init__()
        self.executor = ssh.execute

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
    _parser = "raw"

    @command_decorator
    def raw_cmd(self, cmd):
        return cmd, None