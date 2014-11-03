#! /usr/bin/env python
#
# Reco.py
#
# This module will perform the smearing of the true event rates, with
# the reconstructed parameters, using the detector response
# resolutions, in energy and coszen.
#
# The MC-based approach will take the pdf of the true_energy,
# true_coszen directly from simulations to be reconstructed at
# reco_energy, reco_coszen, and will apply these pdfs to the true
# event rates, ending with the expected reconstructed event rate
# templates for each flavor CC and an overall NC template.
#
# author: Timothy C. Arlen
#         tca3@psu.edu
#
# date:   April 9, 2014
#

from argparse import ArgumentParser, RawTextHelpFormatter
from pisa.utils.log import logging, physics, set_verbosity
from pisa.utils.utils import check_binning, get_binning
from pisa.utils.jsons import from_json,to_json
from pisa.utils.proc import report_params, get_params, add_params
from pisa.reco.MCRecoService import MCRecoService
from pisa.reco.ParamRecoService import ParamRecoService
from pisa.reco.KernelFileRecoService import KernelFileRecoService
import numpy as np


if __name__ == '__main__':

    parser = ArgumentParser(description='Takes a (true, triggered) event rate file '
                            'as input and produces a set of reconstructed templates '
                            'of nue CC, numu CC, nutau CC, and NC events.',
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('event_rate_maps',metavar='JSON',type=from_json,
                        help='''JSON event rate input file with following parameters:
      {"nue": {'cc':{'czbins':[], 'ebins':[], 'map':[]},'nc':...}, 
       "numu": {...},
       "nutau": {...},
       "nue_bar": {...},
       "numu_bar": {...},
       "nutau_bar": {...} }''')
    parser.add_argument('-m', '--mode', type=str, choices=['MC', 'param', 'stored'],
                        default='MC', help='Reco service to use (default: MC)')
    parser.add_argument('--mc_file',metavar='HDF5',type=str,
                        default='events/V15_weighted_aeff.hdf5',
                        help='''HDF5 File containing data from all flavours for a particular instumental geometry. 
Expects the file format to be:
      {
        'nue': {
           'cc': {
               ...
               'true_energy': np.array,
               'true_coszen': np.array,
               'reco_energy': np.array,
               'reco_coszen': np.array
            },
            'nc': {...
             }
         },
         'nue_bar' {...},...
      } ''')
    parser.add_argument('--param_file', metavar='JSON', 
                        type=str, default='reco_params/V15.json',
                        help='''JSON file holding the parametrization''')
    parser.add_argument('--kernel_file', metavar='JSON', 
                        type=str, default=None,
                        help='''JSON file holding the pre-calculated kernels''')
    parser.add_argument('--e_reco_scale',type=float,default=1.0,
                        help='''Reconstructed energy scaling.''')
    parser.add_argument('--cz_reco_scale',type=float,default=1.0,
                        help='''Reconstructed coszen scaling.''')
    parser.add_argument('-o', '--outfile', dest='outfile', metavar='JSON', 
                        type=str, action='store',default="reco.json",
                        help='''file to store the output''')
    parser.add_argument('-v', '--verbose', action='count', default=None,
                        help='''set verbosity level''')
    args = parser.parse_args()

    #Set verbosity level
    set_verbosity(args.verbose)

    #Check binning
    ebins, czbins = check_binning(args.event_rate_maps)

    logging.info("Defining RecoService...")
    if args.mode=='MC':
        reco_service = MCRecoService(ebins, czbins, 
                                     simfile=args.mc_file,
                                     **vars(args))
    elif args.mode=='param':
        reco_service = ParamRecoService(ebins,czbins, 
                                        paramfile=args.param_file,
                                        **vars(args))
    elif args.mode=='stored':
        reco_service = KernelFileRecoService(ebins, czbins,
                                             kernelfile=args.kernel_file, 
                                             **vars(args))

    event_rate_reco_maps = reco_service.get_reco_maps(args.event_rate_maps)

    logging.info("Saving output to: %s"%args.outfile)
    to_json(event_rate_reco_maps,args.outfile)


