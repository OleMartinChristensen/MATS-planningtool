# -*- coding: utf-8 -*-
##########################################

"""Library for handling coordinate system tranforms for the MATS mission

Created 17.07.27 Ole Martin Christensen.
Slightly edited by David Skånberg during 2019.
"""


#

#

# Output

#

import pylab

# from scipy.spatial.transform import Rotation

from astropy.coordinates import (
    EarthLocation,
    GCRS,
    CartesianRepresentation,
    ITRS,
    get_sun,
    AltAz,
)

from astropy import units as units

from astropy import time as time


from astroquery.vizier import Vizier

import astropy.coordinates as coord


from astropy.utils import iers

try:
    iers.IERS_A.open(iers.IERS_A_URL)
    iers.conf.auto_download = True
except:
    iers.conf.auto_download = False


# iers.conf.auto_max_age=60


def ecef2tanpoint(x, y, z, dx, dy, dz):
    """
    This function takes a position and look vector in ECEF system and returns the tangent point
    (point closest to the ellipsiod) for the WGS-84 ellipsiod in ECEF coordinates.
    
    The algorithm used is derived by Nick Lloyd at University of Saskatchewan, 
    Canada (nick.lloyd@usask.ca), and is part of
    the operational code for both OSIRIS and SMR on-board- the Odin satellite.
    
    
        Arguments:
            x (float): ECEF X-coordinate (m)
            
            y (float): ECEF Y-coordinate (m)
            
            z (float): ECEF Z-coordinate (m)
            
            dx (float): ECEF look vector X-coordinate (m)
            
            dy (float): ECEF look vector Y-coordinate (m)
            
            dz (float): ECEF look vector Z-coordinate (m
    
        Returns:
            (tuple): tuple containing:
                
            **tx** (*float*): ECEF X-coordinate of tangentpoint (m)
            
            **ty** (*float*): ECEF Y-coordinate of tangentpoint (m)
            
            **tz** (*float*): ECEF Z-coordinate of tangentpoint (m)
    
    """

    # FIXME check normalization of dx,dy,dz!

    # WGS-84 semi-major axis and eccentricity

    a = 6378137

    e = 0.081819190842621

    a2 = a ** 2

    b2 = a2 * (1 - e ** 2)

    X = pylab.array([x, y, z])

    xunit = pylab.array([dx, dy, dz])

    zunit = pylab.cross(xunit, X)

    zunit = zunit / pylab.linalg.norm(zunit)

    yunit = pylab.cross(zunit, xunit)

    yunit = yunit / pylab.linalg.norm(yunit)

    w11 = xunit[0]

    w12 = yunit[0]

    w21 = xunit[1]

    w22 = yunit[1]

    w31 = xunit[2]

    w32 = yunit[2]

    yr = pylab.dot(X, yunit)

    xr = pylab.dot(X, xunit)

    A = (w11 * w11 + w21 * w21) / a2 + w31 * w31 / b2

    B = 2.0 * ((w11 * w12 + w21 * w22) / a2 + (w31 * w32) / b2)

    C = (w12 * w12 + w22 * w22) / a2 + w32 * w32 / b2

    if B == 0.0:

        xx = 0.0

    else:

        K = -2.0 * A / B

        factor = 1.0 / (A + (B + C * K) * K)

        xx = pylab.sqrt(factor)

        yy = K * x

    dist1 = (xr - xx) * (xr - xx) + (yr - yy) * (yr - yy)

    dist2 = (xr + xx) * (xr + xx) + (yr + yy) * (yr + yy)

    if dist1 > dist2:

        xx = -xx

    tx = w11 * xx + w12 * yr

    ty = w21 * xx + w22 * yr

    tz = w31 * xx + w32 * yr

    return tx, ty, tz


'''
def quaternion2ECEF(q):
    """This function takes a quaternion look vector in ECEF system and converts 
    to a unit look vector in the same system.
    
    Arguments:
        q = Quaternion in ECEF system
    
    Returns:
        dx = unit look vector
        dy = unit look vector
        dz = unit look vector
    """
    
    R = Rotation.from_quat((q))
    
    Unit_Look_Vector_basis_ECEF = R.apply([ [1,0,0], [0,1,0], [0,0,1] ])
    
    
    M = tp.quaternion_matrix(q)
    
    dx = M[0][2]
    
    dy = M[0][1]
    
    dz = -M[0][0]
    
    return dx,dy,dz
'''


def ECEF2lla(x, y, z):

    # This function takes a position in ECEF and converts to geodetic position

    # (lon,lat,alt above ellipsiod)

    #

    # Input

    # x = Position in ECEF (m)

    # y = Position in ECEF (m)

    # z = Position in ECEF (m)

    # Output

    # lon = geodetic latitude (WGS-84)

    # lat = geodetic latitude (WGS-84)

    # alt = altitude above ellipsoid (m)

    # FIXME: check if obstime is needed

    el = EarthLocation.from_geocentric(x, y, z, unit=units.m)

    geo = el.to_geodetic()

    lat = geo[1]

    lon = geo[0]

    alt = geo[2]

    return lat, lon, alt


def lla2ECEF(lat, lon, alt):
    """This function takes a position geodetic position (lon,lat,alt above ellipsiod)
    and converts into ECEF coodinates [m]."""

    #

    # Input

    # lon = geodetic latitude (WGS-84)

    # lat = geodetic latitude (WGS-84)

    # alt = altitude above ellipsoid (m)

    # Output

    # x = Position in ECEF (m)

    # y = Position in ECEF (m)

    # z = Position in ECEF (m)

    # FIXME: check if obstime is needed

    el = EarthLocation.from_geodetic(lon, lat, alt)

    ecef = el.get_itrs()

    x = ecef.cartesian.x.value

    y = ecef.cartesian.y.value

    z = ecef.cartesian.z.value

    return x, y, z


def ecef2eci(x, y, z, dt):
    """This function takes a position in the ECEF coordinate system [m] and datetime.object [utc] and returns it 
    in ECI-J2000 [m]."""

    #

    # Input

    # x = ECEF X-coordinate (m)

    # y = ECEF Y-coordinate (m)

    # z = ECEF Z-coordinate (m)

    # dt = UTC time (datetime object)

    #

    #

    # Output

    #

    # convert datetime object to astropy time object

    tt = time.Time(dt, format="datetime")

    # Read the coordinates in the Earth-fixed frame

    itrs = ITRS(
        CartesianRepresentation(x=x * units.m, y=y * units.m, z=z * units.m), obstime=tt
    )

    # Convert it to  Geocentric Celestial Reference System

    # gcrs = itrs.transform_to(itrs(obstime=tt))
    gcrs = itrs.transform_to(GCRS(obstime=tt))

    x = gcrs.cartesian.x.to_value()

    y = gcrs.cartesian.y.to_value()

    z = gcrs.cartesian.z.to_value()

    return x, y, z


def eci2ecef(x, y, z, dt):
    """This function takes a position in the ECI-J2000 coordinate system [m] and datetime.object [utc] and returns it 
    in ECEF."""

    #

    # Input

    # x = ECI X-coordinate (m)

    # y = ECI Y-coordinate (m)

    # z = ECI Z-coordinate (m)

    # dt = UTC time (datetime object)

    #

    #

    # Output

    #

    # convert datetime object to astropy time object

    tt = time.Time(dt, format="datetime")

    # Read the coordinates in the Geocentric Celestial Reference System

    gcrs = GCRS(CartesianRepresentation(x=x, y=y, z=z, unit="m"), obstime=tt)

    # Convert it to an Earth-fixed frame

    itrs = gcrs.transform_to(ITRS(obstime=tt))

    x = itrs.cartesian.x.to_value()

    y = itrs.cartesian.y.to_value()

    z = itrs.cartesian.z.to_value()

    return x, y, z


def SZAfromlla(lat, lon, alt, dt):

    # This function takes a geodetic position and calculates the solar zenith

    # angle from this

    #

    # Input

    # lon = geodetic latitude (WGS-84)

    # lat = geodetic latitude (WGS-84)

    # alt = altitude above ellipsoid (m)

    # dt = datetime object

    #

    #

    # Output

    #

    # sza = solar zenith angle (deg)

    # convert datetime object to astropy time object

    tt = time.Time(dt, format="datetime")

    # get position of point

    el = EarthLocation.from_geodetic(lon, lat, alt)

    # get position of sun

    sun = get_sun(tt)

    # convert posion to skyangle

    sun_ang = sun.transform_to(AltAz(obstime=tt, location=el))

    # get SZA

    SZA = sun_ang.zen.value

    return SZA


def find_orbit_plane(satpos1_eci_1, satpos2_eci):

    n = pylab.cross(satpos1_eci_1, satpos2_eci)

    n_norm = pylab.linalg.norm(n)

    return n_norm


def los_from_tanpoint_spherical(satpos1_eci_1, satpos2_eci):

    n = pylab.cross(satpos1_eci_1, satpos2_eci)

    n_norm = pylab.linalg.norm(n)

    return n_norm


def starlist_from_ra_dec(ra_in, dec_in, width_in, height_in, Vmag):

    # This function takes a pointing in right acencion, declination (J2000) and give a

    # list of stars with magnitude > Vmag in the region specified by width and height.

    # It uses the I/332A (UCAC4) database.

    #

    # Input

    # ra_in = Right-Acencion (J2000)

    # dec_in = Declination (J2000)

    # width_in = width of FoV (degrees)

    # height_in = height of FoV (degrees)

    # Vmag = Vmag of brightest star to return

    #

    #

    # Output

    #

    # star_table = table of stars

    v = Vizier(
        columns=["_RAJ2000", "_DEJ2000", "Vmag"],
        column_filters={"Vmag": "<" + str(Vmag)},
    )

    star_catalog = ["I/322A"]

    width_instrument = coord.Angle(width_in, unit=units.deg)

    height_instrument = coord.Angle(height_in, unit=units.deg)

    star_table = v.query_region(
        coord.SkyCoord(ra=ra_in, dec=dec_in, unit=(units.deg, units.deg), frame="icrs"),
        width_instrument,
        height_instrument,
        catalog=star_catalog,
    )

    return star_table
