from __future__ import division
import numpy as np
import os
import commander as cm
from commander.sphere import healpix, mmajor
from commander import matrices
import oomatrix as om

from matplotlib import pyplot as plt

#
# Parameters (just variables that are reused further down)\
#

output_filename = 'newmonodip-em7-%d.h5' % os.getpid()
lmax = 500
lprecond = 30
eps = 1e-7
cache_path = 'cache'
seed = None # integer, or None for getting random seed from OS

ctx = cm.CommanderContext(cache_path=cache_path, seed=seed)

nside = 512
lmax = 3 * nside - 1
npix = 12 * nside**2
monodip_templates = np.empty((npix, 4))
monodip_templates[:, 0] = 1
monodip_templates[:, 1:] = healpix.pix2vec_ring(nside, np.arange(npix, dtype=np.int32))


map = cm.load_ring_map(
    ( '$DATA/wmap_da_imap_r9_7yr_%s_v4.fits' % 'V1', 1, 'TEMPERATURE', 'mK'),
    'temperature')
cm.plot.plot_ring_map(map, vmax=300)

bl = cm.gaussian_beam_by_l(lmax, '1 deg')

#B = matrices.diagonal_matrix_by_l(bl, 0, lmax)
#YhW = ctx.sh_analysis_matrix(nside, 0, lmax)
#Y = ctx.sh_synthesis_matrix(nside, 0, lmax)
#smoothed_map = om.compute_array(
#    Y * B * YhW * map[:, None])[:, 0]

map_sh = ctx.sh_analysis(nside, 0, lmax, map)
map_sh *= mmajor.scatter_l_to_lm(0, lmax, bl)
smoothed_map = ctx.sh_synthesis(nside, 0, lmax, map_sh)

plt.figure()
cm.plot.plot_ring_map(smoothed_map, vmax=300)
plt.show()
1/0

#
# Data
#
observations = []
for name, da_list in [('K', [('K1', '1.437 mK')]),
                      ('Ka', [('Ka1', '1.470 mK')]),
                      ('Q', [('Q1', '2.254 mK'), ('Q2', '2.140 mK')]),
                      ('V', [('V1', '3.319 mK'), ('V2', '2.955 mK')]),
                      ('W', [('W1', '5.906 mK'), ('W2', '6.572 mK'),
                             ('W3', '6.941 mK'), ('W4', '6.778 mK')])]:

    T_maps = []
    for da_name, da_sigma0 in da_list:
        map = cm.load_ring_map(
            ( '$DATA/wmap/n512/wmap_da_imap_r9_7yr_%s_v4.fits' % da_name, 1, 'TEMPERATURE', 'mK'),
            'temperature')
        # subtract mono/dipole
        monodip = np.dot(monodip_templates, [0, 1, 2, 3])
        map -= monodip
        T_maps.append(map)
    
    obs = cm.AverageSkyObservations(name, [
        cm.SkyObservation(
            name=da_name,
            description='Raw WMAP r9 data, from http://lambda.gsfc.nasa.gov',
            T_map=T_maps[i],
            TT_nobs_map=('$DATA/wmap/n512/wmap_da_imap_r9_7yr_%s_v4.fits' % da_name, 1, 'N_OBS'),
            TT_sigma0=da_sigma0,
            beam_transfer='$DATA/wmap/n512/wmap_%s_ampl_bl_7yr_v4.txt' % da_name,
            mask_map=('$DATA/wmap/n512/wmap_processing_mask_r9_7yr_v4.fits', 1, 0),
            lmax_beam=lmax)
        for i, (da_name, da_sigma0) in enumerate(da_list)])
    observations.append(obs)

K, Ka, Q, V, W = observations


#
# Model
#

def get_mixing_maps(comp_num):
    # Create a mapping from observation to Commander 1 output file
    d = {}
    for idx, obs in enumerate(observations):
        fitsfile = '$DATA/wmap/mixing/mixmat_comp%02d_band%02d_k03999.fits' % (comp_num, idx + 1)
        d[obs] = (fitsfile, 1, 0)
    return d

# Priors for synch/dust
ls = np.arange(lmax + 1)
ls[0] = ls[1]

prior_synch = 3e5 * ls**-2.1
prior_dust = 1e3 * ls**-1.8

prior_synch[:2] = 0
prior_dust[:2] = 0

# Construct model

Cl = cm.l_array_from_fits('$DATA/wmap/wmap_lcdm_sz_lens_wmap5_cl_v3.fits')
Cl[0] = 100 * Cl[2]
Cl[1] = 100 * Cl[2]

cmb = cm.IsotropicGaussianCmbSignal(
    name='cmb',
    power_spectrum=Cl,
    lmax=lmax
    )

dust = cm.MixingMatrixSignal(
    name='dust',
    lmax=lmax,
    power_spectrum=prior_dust,
    mixing_maps=get_mixing_maps(1)
    )

synchrotron = cm.MixingMatrixSignal(
    name='synch',
    lmax=lmax,
    power_spectrum=prior_synch,
    mixing_maps=get_mixing_maps(2)
    )

#monodipole = cm.MonoAndDipoleSignal('monodipole', fix_at=[])

signal_components = [cmb, dust, synchrotron]

realizations = cm.app.constrained_realization(
    ctx,
    output_filename,
    observations,
    signal_components,
    wiener_only=False, # want samples
    lprecond=lprecond,
    eps=eps,
    filemode='w',
    write_info=False)

