from __future__ import division
import numpy as np

import commander as cm
from matplotlib import pyplot as plt

#
# Data
#

lmax = 1200

observations = {}
for name, sigma0 in [('K1', '1.437 mK')
                     ('Ka1', '1.470 mK'),
                     ('Q1', '2.254 mK'),
                     ('Q2', '2.140 mK'),
                     ('V1', '3.319 mK'),
                     ('V2', '2.955 mK'),
                     ('W1', '5.906 mK'),
                     ('W2', '6.572 mK'),
                     ('W3', '6.941 mK'),
                     ('W4', '6.778 mK')]:
    observations[name] = cm.SkyObservation(
        name=name,
        description='Raw WMAP r9 data with r10 mask, from http://lambda.gsfc.nasa.gov',
        T_map=('$DATA/wmap/n512/wmap_band_imap_r9_7yr_%s_v4.fits ' % name, 1, 'TEMPERATURE'),
        TT_nobs_map=('$DATA/wmap/n512/wmap_band_imap_r9_7yr_%s_v4.fits ' % name, 1, 'N_OBS'),
        TT_sigma0=sigma0,
        beam_transfer='$DATA/wmap/',
        mask_map=('wmap_temperature_analysis_mask_r10_7yr_v4.fits', 1, 0),
        bandpass=(nu, nu),
        lmax_beam=lmax)
    
#
# Model
#

# map nu to index of mixing matrix map to use
def get_mixing_maps(comp_num):
    obs_to_idx = {'K1' : 1,
                  'Ka1' : 2,
                  'Q1' : 3, 'Q2' : 3,
                  'V1' : 4, 'V2' : 4,
                  'W1' : 5, 'W2' : 5, 'W4' : 5, 'W4' : 5}
    return dict((observations[name], ('mixmat/mixmat_comp%02d_band%02d_k01799.fits' %
                                      (comp_num, obsidx), 1, 0))
                for name, obsidx in obs_to_idx.iteritems())

cmb = cm.IsotropicGaussianCmbSignal(
    name='cmb',
    power_spectrum='wmap_lcdm_sz_lens_wmap5_cl_v3.fits',
    lmax=lmax
    )

dust = cm.MixingMatrixSignal(
    name='dust',
    lmax=lmax,
    power_spectrum='cls_synch.fits',
    mixing_maps=get_mixing_maps(1)
    )

synchrotron = cm.MixingMatrixSignal(
    name='synch',
    lmax=lmax,
    power_spectrum='cls_synch.fits',
    mixing_maps=get_mixing_maps(2)
    )

components = [cmb, dust, synchrotron]

# cached: 35, 
lprecond = 40


ctx, signals = cm.app.constrained_realization_command_line(
    observations,
    components,
    lprecond=lprecond,
    cache_path='cache',
    eps=1e-7)


## for signal, comp in zip(signals, components):
##     if isinstance(comp, cm.SphericalHarmonicSignal):
##         plt.figure()
##         if signal is signals[1]:
##             opts = dict(vmax=3000)
##         else:
##             opts = {}
##         cm.plot.plot_sh_map(ctx, signal, nside, 0, lmax, title=comp.name, mask=mask,
##                             **opts)

    

## plt.show()



