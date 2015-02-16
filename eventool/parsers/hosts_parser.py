from eventool import ssh_cmds


class HostsParser(object):

    @ssh_cmds.cli_choice(parser="hosts", handler="op")
    def alias(self, target):
        if not isinstance(target, list):
            return target.alias
        return dict((t.address, t.alias) for t in target)



