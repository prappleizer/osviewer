from observing_suite import Target, OSViewerSetup
import astropy.units as u 

m82 = Target('M82')
m82.add_configuration(config_name='primary',
                      obstype='spectroscopy',
                      slit_length=128*u.arcsec,
                      slit_width=1.5*u.arcsec,
                      PA=60*u.deg)
m82.add_configuration(config_name='secondary',
                      obstype='spectroscopy',
                      slit_length=128*u.arcsec,
                      slit_width=4*u.arcsec,
                      PA=120*u.deg)
m82.set_survey('legacy')
m101 = Target('M101')
m101.add_configuration(config_name='on-target',
                    obstype='spectroscopy',
                    PA = -120*u.deg,
                    slit_length=128*u.arcsec,
                    slit_width=2*u.arcsec)
m101.set_survey('legacy')

plan = OSViewerSetup([m82,m101],
                     observatory='Palomar')



