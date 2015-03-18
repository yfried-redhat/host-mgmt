import functools
import inspect
import re

PARSERS = {}


def cli_choice(parser, subparser=None):
    def decorator(f):
        if subparser:
            name = f.func_name
            help = f.func_doc.strip().split("\n")[0] if f.func_doc else None
            inspec = inspect.getargspec(f)
            # optional_args = []
            # if inspec.defaults:
            #     optional_args = zip(reversed(inspec.args),
            #                         reversed(inspec.defaults))
            #     optional_args.reverse()
            # positional_args = []
            f._parser_dict = {"help": help}
            PARSERS[parser][subparser]['subparser_args'][name] = f._parser_dict

        @functools.wraps(f)
        def func(self, *args, **kwargs):
            return f(self, *args, **kwargs)
        return func
    return decorator


def cli_command(parser, subparser=None, **kwargs):
    if subparser:
        PARSERS.setdefault(parser, {})
        kwargs.setdefault("title",
                          subparser[:1].upper() + subparser[1:] + "s")
        kwargs.setdefault("metavar", subparser.upper())
        PARSERS[parser].setdefault(subparser, {'subparser_def': kwargs,
                                               'subparser_args': {}})

    # def class_decorator(cls):
    #     return cls
    # return class_decorator
    return lambda cls: cls


def add_argument(dest, **kwargs):
    def decorator(f):
        if not hasattr(f, "_parser_dict"):
            # TODO(yfried): add a better exception
            raise Exception("method {name}:{func} not in PARSERS".
                            format(name=f.func_name, func=f))
        f._parser_dict.setdefault("arguments", [])
        if not kwargs.get("help") and f.func_doc:
            # get help from func_doc
            help_regex = re.compile(r'^\s*'
                                    r':param %s: '
                                    r'(.*)'
                                    r'\s*(:(param|return|raise))?' % dest,
                                    flags=re.MULTILINE)
            help_match = help_regex.search(f.func_doc)
            if help_match:
                kwargs["help"] = help_match.group(1)

        f._parser_dict["arguments"].append(dict(dest=dest, **kwargs))

        @functools.wraps(f)
        def func(self, *args, **kwargs):
            return f(self, *args, **kwargs)
        return func
    return decorator
