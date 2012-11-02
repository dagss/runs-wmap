from __future__ import division
import numpy as np

import commander as cm
from matplotlib import pyplot as plt

# Mask udgrade'd from WMAP

#from cmb.maps import pixel_sphere_map
#from commander import resourceloaders

#mask = resourceloaders.map_from_fits(('mask_Vband_n512.fits', 1, 0), 'raw', 'healpix.ring')
#mask = pixel_sphere_map(mask).change_resolution(128).view(np.ndarray)
#mask[mask != 1] = 0

from cPickle import load
with file('mask.pickle') as f:
    mask = load(f)

nside = 128
lmax = 2 * nside

#
# Data
#

observations = []
nu_list = []
for name, nu, rmsprefix in [
    ('044', 44.1, 'dx9_adjrms'),
#    ('V', 60.94, 'wmap7_rms'),
    ('070', 70.3, 'dx9_adjrms'),
#    ('W', 93.47, 'wmap7_rms'),
    ('100', 102.08, 'dx9_adjrms'),
    ('143', 143.08, 'dx9_adjrms'),
    ('217', 221.381, 'dx9_adjrms'),
    ('353', 358.541, 'dx9_adjrms')
    ]:
    obs = cm.SkyObservation(
        name=name,
        T_map=('ffp6/n128/ffp6_Imap_%s_ns128_uK.fits' % name, 1, 0, 'force uK'),
        TT_rms_map=('ffp6/n128/%s_%s.fits' % (rmsprefix, name), 1, 0, 'force uK'),
        beam_transfer='ffp6/n128/beam_60arcmin.fits',
        mask_map=mask,
        bandpass=(nu, nu),
        lmax_beam=lmax)
    observations.append(obs)
    nu_list.append(nu)
#
# Model
#

cmb = cm.IsotropicGaussianCmbSignal(
    name='cmb',
    # Specify degrees for a flat initial power spectrum, or a filename
    # to a text file such as 'wmap_lcdm_sz_lens_wmap7_cl_v4.dat' to start
    # a particular place
    power_spectrum='wmap_lcdm_sz_lens_wmap5_cl_v3.fits',
    lmax=lmax
    )

dust = cm.MixingMatrixSignal(
    name='dust',
    lmax=lmax,
    power_spectrum='cls_synch.fits',
    mixing_maps=[(nu, ('mixmat/mixmat_comp01_band%02d_k01799.fits' % (i + 1), 1, 0))
                 for i, nu in enumerate(nu_list)]
    )

synchrotron = cm.MixingMatrixSignal(
    name='synch',
    lmax=lmax,
    power_spectrum='cls_synch.fits',
    mixing_maps=[(nu, ('mixmat/mixmat_comp02_band%02d_k01799.fits' % (i + 1), 1, 0))
                 for i, nu in enumerate(nu_list)]
    )

components = [cmb, synchrotron, dust]

# cached: 35, 
lprecond = 60


ctx, signals = cm.app.constrained_realization_command_line(
    observations,
    components,
    lprecond=lprecond,
    cache_path='cache',
    eps=1e-7)


for signal, comp in zip(signals, components):
    if isinstance(comp, cm.SphericalHarmonicSignal):
        plt.figure()
        if signal is signals[1]:
            opts = dict(vmax=3000)
        else:
            opts = {}
        cm.plot.plot_sh_map(ctx, signal, nside, 0, lmax, title=comp.name, mask=mask,
                            **opts)

    

plt.show()



