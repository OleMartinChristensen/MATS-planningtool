# -*- coding: utf-8 -*
"""Contains functions used by the Operational Planning Tool .
"""

import ephem, importlib, time, logging, os, sys
from pylab import cos, sin, sqrt, array, arccos, pi, floor, around

from Operational_Planning_Tool import _Globals

OPT_Config_File = importlib.import_module(_Globals.Config_File)

def rot_arbit(angle, u_v):
    """Takes an angle in radians and a unit vector and outputs a rotation matrix around that vector"
    
    Arguments:
        angle (int): Angle in radians.
        u_v (list): Unit vector
        
    Returns:
        (array): Rotation matrix
    
    """
    
    rot_mat = array([(cos(angle)+u_v[0]**2*(1-cos(angle)), \
    u_v[0]*u_v[1]*(1-cos(angle))-u_v[2]*sin(angle), \
    u_v[0]*u_v[2]*(1-cos(angle))+u_v[1]*sin(angle)), \
    \
    (u_v[1]*u_v[0]*(1-cos(angle))+u_v[2]*sin(angle), \
    cos(angle)+u_v[1]**2*(1-cos(angle)), \
    u_v[1]*u_v[2]*(1-cos(angle))-u_v[0]*sin(angle)), \
    \
    (u_v[2]*u_v[0]*(1-cos(angle))-u_v[1]*sin(angle), \
    u_v[2]*u_v[1]*(1-cos(angle))+u_v[0]*sin(angle), \
    cos(angle)+u_v[2]**2*(1-cos(angle)))])
    
    return rot_mat

def deg2HMS(ra='', dec='', roundOf=False):
    """Takes a declination or a RAAN angle in degrees and converts it to DMS or HMS format respectively
    
    Only one (and only one!) of the inputs (ra or dec) shall be provided.
    
    Arguments:
        ra (str): RAAN angle in degrees.
        dec (str): Declination angle in degrees.
        roundOf (bool): True for rounding of seconds to nearest integer. False for seconds with decimals.
        
    Returns:
        (str): RAAN or Declination angle in HMS format.
        
    """
    
    RA, DEC, rs, ds = '', '', '', ''
    
    if dec:
        if str(dec)[0] == '-':
            ds, dec = '-', abs(dec)
        deg = int(dec)
        decM = abs(int((dec-deg)*60))
        if roundOf:
            decS = int((abs((dec-deg)*60)-decM)*60)
        else:
            decS = (abs((dec-deg)*60)-decM)*60
        DEC = '{0}{1} {2} {3}'.format(ds, deg, decM, decS)
        
    elif ra:
        if str(ra)[0] == '-':
            rs, ra = '-', abs(ra)
        raH = int(ra/15)
        raM = int(((ra/15)-raH)*60)
        if roundOf:
            raS = int(((((ra/15)-raH)*60)-raM)*60)
        else:
            raS = ((((ra/15)-raH)*60)-raM)*60
        RA = '{0}{1} {2} {3}'.format(rs, raH, raM, raS)
        
    return RA or DEC


def lat_2_R( lat ):
    """Takes a geocentric latitude in radians and puts out the distance from the center of a spheroid Earth to the surface
    
    Arguments:
        lat (float): Latitude angle in radians
        
    Returns:
        (float): Geocentric distance [km]
        
    """
    
    R_polar = 6356.752314245
    R_eq = 6378.137
    
    R = sqrt( ( (R_eq**2*cos(lat))**2 + (R_polar**2*sin(lat))**2 ) / ( (R_eq*cos(lat))**2 + (R_polar*sin(lat))**2 ) )
    
    return R

def scheduler(Occupied_Timeline, date, endDate):
    ''' Function that checks if the scheduled time is available and postpones it otherwise. 
    
    If scheduled time is occupied, it gets postponed with mode_separation*2 seconds (defined in Config_File.Timeline_settings) until available.
    
    Arguments:
        Occupied_Timeline (dict): A dictionary of all planned Modes (except 1-4) containing lists with their scheduled times ([startDate, endDate]) as ephem.Date class.
        date (:obj:`ephem.Date`): The scheduled startdate of the current Mode.
        endDate (:obj:`ephem.Date`): The scheduled end-date of the current Mode.
    
    Returns: 
        (tuple): tuple containing:
        date (ephem.Date): The scheduled startdate (potentially postponed) of the current Mode as a ephem.Date object. \n
        endDate (ephem.Date): The scheduled end-date (potentially postponed) of the current Mode as a ephem.Date object. \n
        iterations (int): The number of times the scheduled date got postponed. (int)
        
    '''
    
    Timeline_settings = OPT_Config_File.Timeline_settings()
    
    iterations = 0
    restart = True
    ## Checks if date is available and postpones starting date of mode until available
    while( restart == True):
        restart = False
        
        "Extract the start and end dates of scheduled mode"
        for busy_dates in Occupied_Timeline.values():
            if( busy_dates == []):
                continue
            else:
                
                "Extract the start and end date of each instance of a scheduled mode"
                for busy_date in busy_dates:
                    
                    "If the planned date collides with any already scheduled ones -> post-pone and restart loop"
                    if( busy_date[0] <= date < busy_date[1] or 
                           busy_date[0] < endDate <= busy_date[1] or
                           (date < busy_date[0] and endDate > busy_date[1])):
                        
                        date = ephem.Date(date + ephem.second*Timeline_settings['mode_separation']*2)
                        endDate = ephem.Date(endDate + ephem.second*Timeline_settings['mode_separation']*2)
                        
                        iterations = iterations + 1
                        restart = True
                        break
                
    return date, endDate, iterations


def params_checker(dict1, dict2):
    """Function which compares the keys of two dictionaries and outputs a new dictionary. 
    
    A dict_new will be created containing all the keys and values of dict2. Then for any keys that 
    exist in both dict1 and dict_new, dict_new's keys will have their values replaced by the ones in dict1.
    
    WARNING! All keys in dict1 must also exist in dict2.
    
    Arguments:
        dict1 (dict): 
        dict2 (dict): 
    
    Returns:
        (dict): 
        
    """
    
    
    "Check if optional params were given"
    if( dict1 != dict2):
        dict_new = dict2
        "Loop through parameters given and exchange the settings ones"
        for key in dict1.keys():
            dict_new[key] = dict1[key]
    else:
        dict_new = dict1
        
    return dict_new

def utc_to_onboardTime(utc_date):
    """Function which converts a date in utc into onboard time in seconds.
    
    Arguments:
        utc_date (:obj:`ephem.Date`): The date as a ephem.Date class.
    
    Returns:
        (int): Onboard Time in seconds
        
    """
    Timeline_settings = OPT_Config_File.Timeline_settings()
    
    GPS_epoch = ephem.Date(Timeline_settings['GPS_epoch'])
    leapSeconds = ephem.second*Timeline_settings['leap_seconds']
    
    GPS_date = utc_date+leapSeconds-GPS_epoch
    
    onboardTime = around(GPS_date / ephem.second, 1)
    '''
    GPS_week = floor(GPS_date/7)
    
    onboardTime = around( (GPS_date/7 - GPS_week) / ephem.second, 1 )
    '''
    return onboardTime

def SetupLogger():
    """Removes previous handlers and sets up a logger with both a file handler and a stream handler.
    
    """
    
    Logger = logging.getLogger(OPT_Config_File.Logger_name())
    name = sys._getframe(1).f_code.co_name
    ######## Try to Create a directory for storage of Logs #######
    try:
        os.mkdir('Logs_'+name)
    except:
        pass
    
    "Remove all previous handlers of the logger"
    for handler in Logger.handlers[:]:
        Logger.removeHandler(handler)
    
    
    
    #logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    logstring = os.path.join('Logs_'+name, name+'__'+_Globals.Config_File+'__'+timestr+'.log')
    Handler = logging.FileHandler(logstring, mode='a')
    formatter = logging.Formatter("%(levelname)6s : %(message)-80s :: %(module)s :: %(funcName)s")
    Handler.setFormatter(formatter)
    Logger.addHandler(Handler)
    Logger.setLevel(logging.DEBUG)
    
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.INFO)
    streamHandler.setFormatter(formatter)
    Logger.addHandler(streamHandler)
    


def calculate_time_per_row(NCOL, NCBIN, NCBINFPGA, NRSKIP, NROW, NRBIN, NFLUSH):
    """This function provides an estimated amount of time for a CCD readout
    
    Note that minor "transition" states may have been omitted resulting in 
    somewhat shorter readout times (<0.1%).
    
    Default timing setting is:\n
    ccd_r_timing <= x"A4030206141D"&x"010303090313"
    
    All pixel timing setting is the final count of a counter that starts at 0,
    so the number of clock cycles exceeds the setting by 1
    
    Returns:
        (float): Readout time in ns. 
    """
    
    #image parameters
    ncol=int(NCOL)+1
    ncolbinC=int(NCBIN)
    if ncolbinC == 0:
        ncolbinC = 1
    ncolbinF=2**int(NCBINFPGA)
    
    nrow=int(NROW)
    nrowbin=int(NRBIN)
    if nrowbin == 0:
        nrowbin = 1
    nrowskip=int(NRSKIP)
    
    n_flush=int(NFLUSH)
    
    #timing settings
    full_timing = 0 #TODO <-- meaning?
    
    #full pixel readout timing
    time0 = 1 + 19 # x13%TODO
    time1 = 1 +  3 # x03%TODO
    time2 = 1 +  9 # x09%TODO
    time3 = 1 +  3 # x03%TODO
    time4 = 1 +  3 # x03%TODO
    time_ovl = 1 + 1 # x01%TODO
    
    # fast pixel readout timing
    timefast  = 1 + 2 # x02%TODO
    timefastr = 1 + 3 # x03%TODO
    
    #row shift timing
    row_step = 1 + 164 # xA4%TODO
    
    clock_period = 30.517 #master clock period, ns 32.768 MHz
    
    #there is one extra clock cycle, effectively adding to time 0
    Time_pixel_full = (1+ time0 + time1 + time2 + time3 + time4 + 3*time_ovl)*clock_period
    
    # this is the fast timing pixel period
    Time_pixel_fast = (1+ 4*timefast + 3*time_ovl + timefastr)*clock_period
    
    #here we calculate the number of fast and slow pixels
    #NOTE: the effect of bad pixels is disregarded here
    
    if full_timing == 1:
        n_pixels_full = 2148
        n_pixels_fast = 0
    else:
        if ncolbinC < 2: #no CCD binning
            n_pixels_full = ncol * ncolbinF
        else: #there are two "slow" pixels for one superpixel to be read out
            n_pixels_full = 2*ncol *ncolbinF
        n_pixels_fast = 2148 - n_pixels_full
    
    
    #time to read out one row
    T_row_read = n_pixels_full*Time_pixel_full + n_pixels_fast*Time_pixel_fast
    
    # shift time of a single row
    T_row_shift = (64 + row_step *10)*clock_period
    
    #time of the exposure start delay from the start_exp signal # n_flush=1023
    T_delay = T_row_shift * n_flush
    
    #total time of the readout
    T_readout = T_row_read*(nrow+nrowskip+1) + T_row_shift*(1+nrowbin*nrow)
    
    
    #"smearing time"
    #(this is the time that any pixel collects electrons in a wrong row, during the shifting.)
    #For smearing correction, this is the "extra exposure time" for each of the rows.
    T_row_extra = (T_row_read + T_row_shift*nrowbin) / 1e9    
    
    return T_readout