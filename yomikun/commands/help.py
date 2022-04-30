import click


def make_help_command(cli):
    @click.command()
    @click.argument('subcommand')
    @click.pass_context
    def help(ctx, subcommand):
        """
        Return help for any subcommand

        This is an alternative to calling 'yomikun <subcommand> --help'
        """
        subcommand_obj = cli.get_command(ctx, subcommand)
        if subcommand_obj is None:
            click.echo(f"No such subcommand: {subcommand}")
        else:
            ctx.info_name = subcommand
            click.echo(subcommand_obj.get_help(ctx))

    return help
