#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A collection of functions for doing common processing tasks."""

import numpy as np
from astropy import log
from astroML.density_estimation import scotts_bin_width, freedman_bin_width,\
        knuth_bin_width, bayesian_blocks

__author__ = 'Simon Mutch'
__email__ = 'smutch.astro@gmail.com'
__version__ = '0.1.0'

def mass_function(mass, volume, bins, range=None, return_edges=False, **kwargs):
    """Generate a mass function.
   
    Args:
        mass (array):  an array of 'masses'
        volume (float):  volume of simulation cube / subset
        bins (int or list or str):
            If bins is a string, then it must be one of:
                'blocks'   : use bayesian blocks for dynamic bin widths
                'knuth'    : use Knuth's rule to determine bins
                'scott'    : use Scott's rule to determine bins
                'freedman' : use the Freedman-diaconis rule to determine bins

    Kwargs:
        range (len=2 list or array): range of data to be used for mass function
        return_edges (bool): return the bin_edges (default: False)
        **kwargs: passed to np.histogram call

    Returns:
        array of [bin centers, mass function vals]
        If return_edges=True then the bin edges are also returned.

    Notes:
        The code to generate the bin_widths is taken from astroML.hist
    """

    if "normed" in kwargs:
        kwargs["normed"] = False
        log.warn("Turned of normed kwarg in mass_function()")

    if (range is not None and (bins in ['blocks',
                                        'knuth', 'knuths',
                                        'scott', 'scotts',
                                        'freedman', 'freedmans'])):
        mass = mass[(mass >= range[0]) & (mass <= range[1])]

    if isinstance(bins, str):
        log.info("Calculating bin widths using `%s' method..." % bins)
        if bins in ['blocks']:
            bins = bayesian_blocks(mass)
        elif bins in ['knuth', 'knuths']:
            dm, bins = knuth_bin_width(mass, True)
        elif bins in ['scott', 'scotts']:
            dm, bins = scotts_bin_width(mass, True)
        elif bins in ['freedman', 'freedmans']:
            dm, bins = freedman_bin_width(mass, True)
        else:
            raise ValueError("unrecognized bin code: '%s'" % bins)
        log.info("...done")

    vals, edges = np.histogram(mass, bins, range, **kwargs)
    width = edges[1]-edges[0]
    radius = width/2.0
    centers = edges[:-1]+radius
    vals = vals.astype(float) / (volume * width)

    mf = np.dstack((centers, vals)).squeeze()

    if not return_edges:
        return mf
    else:
        return mf, edges
