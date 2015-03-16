from eventool import parsers


@parsers.cli_command("hosts", subparser="action")
class HostsParser(object):

    @parsers.cli_choice(parser="hosts", subparser="action")
    def alias(self, target):
        if not isinstance(target, list):
            return target.alias
        return dict((t.address, t.alias) for t in target)



