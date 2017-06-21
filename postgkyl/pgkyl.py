#!/usr/bin/env python
import click
import numpy

import postgkyl.commands as cmd
from postgkyl.tools.stack import pushStack, peakStack, popStack
from postgkyl.tools.stack import loadFrame, loadHist

@click.group(chain=True)
@click.option('--filename', '-f', multiple=True,
              help='Specify one or more file(s) to work with.')
@click.pass_context
def cli(ctx, filename):
    ctx.obj = {}

    ctx.obj['files'] = filename
    numSets = len(filename)
    ctx.obj['numSets'] = numSets
    ctx.obj['sets'] = range(numSets)
    ctx.obj['setIds'] = []

    ctx.obj['data'] = []
    ctx.obj['labels'] = []

    ctx.obj['coords'] = []
    ctx.obj['values'] = []
    ctx.obj['type'] = []

    for s in ctx.obj['sets']:
        if filename[s][-2:] == 'h5' or filename[s][-2:] == 'bp':
            loadFrame(ctx, s, str(filename[s]))
        else:
            loadHist(ctx, s, str(filename[s]))

    ctx.obj['hold'] = 'off'
    ctx.obj['fig'] = ''
    ctx.obj['ax'] = ''

cli.add_command(cmd.euler.euler)
cli.add_command(cmd.output.hold)
cli.add_command(cmd.output.info)
cli.add_command(cmd.output.plot)
cli.add_command(cmd.output.write)
cli.add_command(cmd.select.comp)
cli.add_command(cmd.select.fix)
cli.add_command(cmd.select.pop)
cli.add_command(cmd.select.dataset)
cli.add_command(cmd.transform.mask)
cli.add_command(cmd.transform.mult)
cli.add_command(cmd.transform.norm)
cli.add_command(cmd.transform.project)
cli.add_command(cmd.transform.integrate)

if __name__ == '__main__':
    cli()

