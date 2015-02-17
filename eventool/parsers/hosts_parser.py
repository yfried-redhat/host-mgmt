from eventool import parsers


class HostsParser(object):

    @parsers.cli_choice(parser="hosts", subparser="op")
    def alias(self, target):
        if not isinstance(target, list):
            return target.alias
        return dict((t.address, t.alias) for t in target)



