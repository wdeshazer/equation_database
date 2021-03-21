import os
from uncertainties import unumpy

work_dir = '/home/deshaze/omfit/'
data_dir = os.path.join(work_dir, 'data')

shots = []  # 6 digit shot number
signals = ['AMINOR', 'R0', 'VOLUME', 'KAPPA', 'KAPPA0', 'TRITOP', 'TRIBOT', 'ZMAXIS',
           'IP', 'BT0', 'LI', 'Q0', 'Q95', 'BDOTAMPL', 'TAUE',
           'DENSITY',
           'PTOT', 'POH', 'PNBI', 'PBINJ', 'ECHPWR', 'ICHPWR',
           'GASA_CAL', 'GASB_CAL', 'GASC_CAL', 'GASD_CAL', 'GASE_CAL',
           'EDENSFIT', 'ETEMPFIT', 'ITEMPFIT', 'TROTFIT', 'ZDENSFIT']

for shot in shots:
    shot_dir = os.path.join(data_dir, str(shot))
    if not os.path.exists(shot_dir):
        os.makedirs(shot_dir)

    for signal in signals:
        mds = OMFITmdsValue(server='DIII-D', shot=shot, TDI=signal, treename=None)

        try:
            signal_data = mds.xarray()
        except:
            printe('#' + str(shot) + ' ' + signal + ': data missing')
            continue

        signal_data.values = unumpy.nominal_values(signal_data.values)
        signal_data.to_netcdf(os.path.join(shot_dir, signal.lower() + '.nc'), 'w')

path_zip = os.path.join(work_dir, 'data.zip')
if os.path.exists(path_zip):
    os.remove(path_zip)

os.system('cd ' + work_dir + '&& zip -r data.zip data')
root['data'] = OMFITpath(data_dir + '.zip')