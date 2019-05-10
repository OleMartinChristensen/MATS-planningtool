# -*- coding: utf-8 -*-
##########################################

#Library for handling coordinate system tranforms for the MATS mission

##########################################



#Created 17.07.27 Ole Martin Christensen





#

#

# Output 

#

import numpy as np

#import numpy.transformations as tp

from astropy.coordinates import EarthLocation, GCRS, CartesianRepresentation, ITRS, get_sun, AltAz

from astropy import units as units

from astropy import time as time



from astroquery.vizier import Vizier

import astropy.coordinates as coord





def ecef2tanpoint(x,y,z,dx,dy,dz):

    

#This function takes a position and look vector in ECEF system and returns the tangent point

#(point closest to the ellipsiod) for the WGS-84 ellipsiod in ECEF coordinates.

#The algorithm used is derived by Nick Lloyd at University of Saskatchewan, 

#Canada (nick.lloyd@usask.ca), and is part of

#the operational code for both OSIRIS and SMR on-board- the Odin satellite.

#

# Input

# x = ECEF X-coordinate (m)

# y = ECEF Y-coordinate (m)

# z = ECEF Z-coordinate (m)

# dx = ECEF look vector X-coordinate (m)

# dy = ECEF look vector Y-coordinate (m)

# dz = ECEF look vector Z-coordinate (m



# Output

# tx = ECEF X-coordinate of tangentpoint (m)

# ty = ECEF Y-coordinate of tangentpoint (m)

# tz = ECEF Z-coordinate of tangentpoint (m)



#FIXME check normalization of dx,dy,dz!





     #WGS-84 semi-major axis and eccentricity

     a=6378137

     e=0.081819190842621

     

     a2 = a**2

     b2 = a2 * ( 1 - e**2 )

     X = np.array([x,y,z])

  

     xunit = np.array([dx,dy,dz])

  

     zunit = np.cross( xunit, X )

     zunit = zunit / np.linalg.norm(zunit)

 	

     yunit = np.cross( zunit, xunit )

     yunit = yunit / np.linalg.norm(yunit)

  

     w11 = xunit[0]

     w12 = yunit[0]

     w21 = xunit[1]

     w22 = yunit[1]

     w31 = xunit[2]

     w32 = yunit[2]

     yr  = np.dot( X, yunit )

     xr  = np.dot( X, xunit )

 	   

     A = (w11*w11 + w21*w21)/a2 + w31*w31/b2

     B = 2.0*((w11*w12 + w21*w22)/a2 + (w31*w32)/b2)

     C = (w12*w12 + w22*w22)/a2 + w32*w32/b2

 	

     if B == 0.0:

         xx = 0.0

     else: 

        K = -2.0*A/B

        factor = 1.0/(A+(B+C*K)*K)

        xx = np.sqrt(factor)

        yy = K*x

      

     dist1 = (xr-xx)*(xr-xx) + (yr-yy)*(yr-yy)

     dist2 = (xr+xx)*(xr+xx) + (yr+yy)*(yr+yy)

 	

     if dist1 > dist2:

        xx = -xx

     

     tx = w11*xx + w12*yr

     ty = w21*xx + w22*yr

     tz = w31*xx + w32*yr

     

     return tx,ty,tz

 

def quaternion2ECEF(q):

    

#This function takes a quaternion look vector in ECEF system and converts 

#to a unit look vector in the same system

#

# Input

# q = Quaternion in ECEF system



# Output

# dx = unit look vector

# dy = unit look vector

# dz = unit look vector



    M = tp.quaternion_matrix(q)

    dx = M[0][2]

    dy = M[0][1]

    dz = -M[0][0]

    return dx,dy,dz



def ECEF2lla(x,y,z):

#This function takes a position in ECEF and converts to geodetic position

#(lon,lat,alt above ellipsiod)

#

# Input

# x = Position in ECEF (m)

# y = Position in ECEF (m)

# z = Position in ECEF (m)



# Output

# lon = geodetic latitude (WGS-84)

# lat = geodetic latitude (WGS-84)

# alt = altitude above ellipsoid (m)



#FIXME: check if obstime is needed



    el = EarthLocation.from_geocentric(x,y,z,unit=units.m)

    geo = el.to_geodetic()

    lat = geo[1]

    lon = geo[0]

    alt = geo[2]

    return lat,lon,alt



    

def lla2ECEF(lat,lon,alt):

#This function takes a position geodetic position (lon,lat,alt above ellipsiod)

#and converts into ECEF coodinates

#



# Input

# lon = geodetic latitude (WGS-84)

# lat = geodetic latitude (WGS-84)

# alt = altitude above ellipsoid (m)



# Output

# x = Position in ECEF (m)

# y = Position in ECEF (m)

# z = Position in ECEF (m)





#FIXME: check if obstime is needed



    el = EarthLocation.from_geodetic(lon,lat,alt)

    ecef = el.get_itrs()

    x = ecef.cartesian.x.value 

    y = ecef.cartesian.y.value

    z = ecef.cartesian.z.value 

    

    return x,y,z



def ecef2eci(x,y,z,dt):

    

#This function takes a position in the ECI-J2000 corrdinate system and returns it 

#in ECEF.

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

    tt=time.Time(dt,format='datetime')



    # Read the coordinates in the Geocentric Celestial Reference System

    itrs = ITRS(CartesianRepresentation(x=x*units.km,y=y*units.km,z=z*units.km), obstime=tt)



    # Convert it to an Earth-fixed frame

    gcrs = itrs.transform_to(GCRS(obstime=tt))

    x = gcrs.cartesian.x

    y = gcrs.cartesian.y

    z = gcrs.cartesian.z

    

    return x,y,z





def eci2ecef(x,y,z,dt):

    

#This function takes a position in the ECI-J2000 corrdinate system and returns it 

#in ECEF.

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

    tt=time.Time(dt,format='datetime')



    # Read the coordinates in the Geocentric Celestial Reference System

    gcrs = GCRS(CartesianRepresentation(x=x*units.km,y=y*units.km,z=z*units.km), obstime=tt)



    # Convert it to an Earth-fixed frame

    itrs = gcrs.transform_to(ITRS(obstime=tt))

    x = itrs.cartesian.x

    y = itrs.cartesian.y

    z = itrs.cartesian.z

    

    return x,y,z





def SZAfromlla(lat,lon,alt,dt):

    

#This function takes a geodetic position and calculates the solar zenith 

#angle from this

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

    tt=time.Time(dt,format='datetime')

    

    #get position of point

    el = EarthLocation.from_geodetic(lon,lat,alt)    

    #get position of sun

    sun = get_sun(tt)

    #convert posion to skyangle

    sun_ang = sun.transform_to(AltAz(obstime=tt,location=el))

    #get SZA

    SZA = sun_ang.zen.value

    

    return SZA



def find_orbit_plane(satpos1_eci_1,satpos2_eci):

    

    n = np.cross(satpos1_eci_1,satpos2_eci)

    n_norm = np.linalg.norm(n)

    

    return n_norm



def los_from_tanpoint_spherical(satpos1_eci_1,satpos2_eci):

    

    n = np.cross(satpos1_eci_1,satpos2_eci)

    n_norm = np.linalg.norm(n)

    

    return n_norm





def starlist_from_ra_dec(ra_in,dec_in,width_in,height_in,Vmag):

    

#This function takes a pointing in right acencion, declination (J2000) and give a 

#list of stars with magnitude > Vmag in the region specified by width and height. 

#It uses the I/332A (UCAC4) database.

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



    v = Vizier(columns=['_RAJ2000', '_DEJ2000', 'Vmag'], column_filters={"Vmag":"<"+str(Vmag)})



    star_catalog = ["I/322A"]

    width_instrument = coord.Angle(width_in, unit=units.deg)

    height_instrument = coord.Angle(height_in, unit=units.deg)

    star_table = v.query_region(coord.SkyCoord(ra=ra_in, dec=dec_in,

                                            unit=(units.deg, units.deg),frame='icrs'),

                            width_instrument,height_instrument,catalog=star_catalog)

    return star_table