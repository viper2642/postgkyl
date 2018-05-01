import os
import click
import numpy as np
import matplotlib.pyplot as plt

from postgkyl.commands.util import vlog, pushChain

#---------------------------------------------------------------------
#-- Growth -----------------------------------------------------------
@click.command(help='Fit e^(2x) to the data')
@click.option('-g', '--guess', default=(1.0, 0.1),
              help='Specify initial guess')
@click.option('-p', '--plot', is_flag=True,
              help='Plot the data and fit')
@click.option('--minn', default=100, type=click.INT,
              help='Set minimal number of points to fit')
@click.option('--maxn', type=click.INT,
              help='Set maximal number of points to fit')
@click.pass_context
def growth(ctx, **inputs):
    vlog(ctx, 'Starting growth')
    pushChain( ctx, 'growth', **inputs) 

    from postgkyl.diagnostics.growth import fitGrowth, exp2

    for s in ctx.obj['sets']:
        time = ctx.obj['dataSets'][s].peakGrid()
        values = ctx.obj['dataSets'][s].peakValues()
        numDims = ctx.obj['dataSets'][s].getNumDims()
        if numDims > 1:
            click.echo(click.style("ERROR: 'growth' is available only for 1D data (used on {:d}D data)".format(numDims), fg='red'))
            ctx.exit()
        
        vlog(ctx, 'growth: Starting fit for data set #{:d}'.format(s))
        bestParams, bestR2, bestN = fitGrowth(time[0], values[..., 0],
                                              minN=inputs['minn'],
                                              maxN=inputs['maxn'],
                                              p0=inputs['guess'])

        if inputs['plot'] is True:
            vlog(ctx, 'growth: Plotting data and fit')
            plt.style.use(os.path.dirname(os.path.realpath(__file__)) \
                      + "/../output/postgkyl.mplstyle")
            fig, ax = plt.subplots()
            ax.plot(time[0], values[..., 0], '.')
            ax.set_autoscale_on(False)
            ax.plot(time[0], exp2(time[0], *bestParams))
            ax.grid(True)
            plt.show()
    vlog(ctx, 'Finishing growth')
