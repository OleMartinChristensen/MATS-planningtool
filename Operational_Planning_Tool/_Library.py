# -*- coding: utf-8 -*
"""Contains functions used by the Operational Planning Tool .
"""

import ephem, importlib, time, logging, os, sys
from pylab import cos, sin, sqrt, array, arccos, pi, floor, around

from Operational_Planning_Tool import _Globals, _MATS_coordinates

OPT_Config_File = importlib.import_module(_Globals.Config_File)
Logger = logging.getLogger(OPT_Config_File.Logger_name())

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
    """Takes a geocentric or geodetic latitude in radians and puts out the distance from the center of a ellipsoid Earth to the surface
    
    If a geocentic latitude is given, an error of up to 70 m will occur.
    
    Arguments:
        lat (float): Latitude angle in radians
        
    Returns:
        (float): Geocentric distance [km]
        
    """
    
    
    R_polar = 6356.752314245
    R_eq = 6378.137
    
    
    
    R = sqrt( ( (R_eq**2*cos(lat))**2 + (R_polar**2*sin(lat))**2 ) / ( (R_eq*cos(lat))**2 + (R_polar*sin(lat))**2 ) )

    #e = sqrt(1-R_polar**2/R_eq**2)
    #R = R_eq/sqrt(1-e**2*sin(lat/180*pi)**2)
    #R = sqrt( ( (R_eq**2*cos(lat))**2 + (R_polar**2*sin(lat))**2 ) / ( (R_eq*cos(lat))**2 + (R_polar*sin(lat))**2 ) )
    
    return R



def lat_MATS_calculator( date ):
    ''' Function that calculates the latitude of a satellite defined by TLE.
    
    Mainly used to approximated the latitude of a LP as the LP is close to being in the same orbital plane.
    
    Arguments:
        date (:obj:`ephem.Date`): The scheduled startdate of the current Mode.
    
    Returns: 
        lat_MATS (float): Latitude given in radians.
    '''
    
    TLE1 = OPT_Config_File.getTLE()[0]
    TLE2 = OPT_Config_File.getTLE()[1]
        
    
    MATS = ephem.readtle('MATS',TLE1,TLE2)
    
    MATS.compute(ephem.Date(date), epoch = '2000/01/01 11:58:55.816')
    
    (lat_MATS,long_MATS,alt_MATS,a_ra_MATS,a_dec_MATS)= (
            MATS.sublat, MATS.sublong, MATS.elevation/1000, MATS.a_ra, MATS.a_dec)
    
    R_earth_MATS = lat_2_R(lat_MATS) #WGS84 radius from latitude of MATS
    
    z_MATS = sin(a_dec_MATS)*(alt_MATS+R_earth_MATS)
    x_MATS = cos(a_dec_MATS)*(alt_MATS+R_earth_MATS)* cos(a_ra_MATS)
    y_MATS = cos(a_dec_MATS)*(alt_MATS+R_earth_MATS)* sin(a_ra_MATS)
    r_MATS = array((x_MATS, y_MATS, z_MATS))
    
    
    r_MATS_ECEF_x, r_MATS_ECEF_y, r_MATS_ECEF_z = _MATS_coordinates.eci2ecef(
            r_MATS[0], r_MATS[1], r_MATS[2], ephem.Date(date).datetime())
    
    
    lat_MATS, long_MATS, alt_MATS  = _MATS_coordinates.ECEF2lla(r_MATS_ECEF_x*1000, r_MATS_ECEF_y*1000, r_MATS_ECEF_z*1000)
    
    lat_MATS = lat_MATS / 180*pi
    
    return lat_MATS

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
    
    Logger.debug('params from Science Mode List: '+str(dict1))
    
    "Check if optional params were given"
    if( dict1 != dict2):
        dict_new = dict2
        "Loop through parameters given and exchange the settings ones"
        for key in dict1.keys():
            dict_new[key] = dict1[key]
    else:
        dict_new = dict1
    
    Logger.debug('params after params_checker function: '+str(dict_new))
    Logger.info('params used: '+str(dict_new))
    
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
    
    Arguments:
        NCOL (int): Number of columns
        NCBIN (int): Number of columns to bin
        NCBINFPGA (int): Binning with FPGA
        NRSKIP (int): Number of rows to skip
        NROW (int): Number of rows
        NRBIN (int): Number of rows to bin
        NFLUSH (int): Number of pre-exposure flushes
    
    Returns:
        (float): Readout time in ms. 
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
    T_row_extra = (T_row_read + T_row_shift*nrowbin)   
    
    return T_readout/1e6, T_delay/1e6, T_row_extra/1e6


def SyncArgCalculator(CCD_settings):
    """Calculates appropriate arguments for the CCD Synchonize CMD.
    
    The offset calculations depend on the Readout Time, which depends on the binning settings of the CCDs.
    The Exposure Interval Time depends on the longest Combined Readout Time and ExposureTime aswell as the 
    leading CCDs Exposure Time (which means it is also the short Exposure Time) to prevent collision between
    Readout of the leading CCD and the final CCD.
    
        Arguments:
            CCD_settings (dict of dict of int): Dictionary containing settings for the CCDs.
            
        Returns:
            CCDSEL (int): Calculated CCDSEL argument for the CCD Synchronize CMD.
            NCCD (int): Calculated NCCD argument for the CCD Synchronize CMD.
            TEXPIOFS (list of int): Calculated TEXPIOFS argument for the CCD Synchronize CMD.
            TEXPIMS: Calculated minimum Exposure Interval Time.
    
    """
    
    CCD_48 = CCD_settings['CCD_48']
    CCD_9 = CCD_settings['CCD_9']
    CCD_6 = CCD_settings['CCD_6']
    CCD_64 = CCD_settings['CCD_64']
    
    ReadOutTime = []
    
    T_readout, T_delay, T_Extra = calculate_time_per_row(NCOL = CCD_48['NCOL'], NCBIN = CCD_48['NCBIN'], NCBINFPGA = CCD_48['NCBINFPGA'], 
                                                         NRSKIP = CCD_48['NRSKIP'], NROW = CCD_48['NROW'], 
                                                         NRBIN = CCD_48['NRBIN'], NFLUSH = CCD_48['NFLUSH'])
    ReadOutTime_48 = T_readout + T_delay + T_Extra
    ReadOutTime.append(int(ReadOutTime_48))
    
    T_readout, T_delay, T_Extra = calculate_time_per_row(NCOL = CCD_9['NCOL'], NCBIN = CCD_9['NCBIN'], NCBINFPGA = CCD_9['NCBINFPGA'], 
                                                         NRSKIP = CCD_9['NRSKIP'], NROW = CCD_9['NROW'], 
                                                         NRBIN = CCD_9['NRBIN'], NFLUSH = CCD_9['NFLUSH'])
    ReadOutTime_9 = T_readout + T_delay + T_Extra
    ReadOutTime.append(int(ReadOutTime_9))
    
    T_readout, T_delay, T_Extra = calculate_time_per_row(NCOL = CCD_6['NCOL'], NCBIN = CCD_6['NCBIN'], NCBINFPGA = CCD_6['NCBINFPGA'], 
                                                         NRSKIP = CCD_6['NRSKIP'], NROW = CCD_6['NROW'], 
                                                         NRBIN = CCD_6['NRBIN'], NFLUSH = CCD_6['NFLUSH'])
    ReadOutTime_6 = T_readout + T_delay + T_Extra
    ReadOutTime.append(int(ReadOutTime_6))
    
    T_readout, T_delay, T_Extra = calculate_time_per_row(NCOL = CCD_64['NCOL'], NCBIN = CCD_64['NCBIN'], NCBINFPGA = CCD_64['NCBINFPGA'], 
                                                         NRSKIP = CCD_64['NRSKIP'], NROW = CCD_64['NROW'], 
                                                         NRBIN = CCD_64['NRBIN'], NFLUSH = CCD_64['NFLUSH'])
    ReadOutTime_64 = T_readout + T_delay + T_Extra
    ReadOutTime.append(int(ReadOutTime_64))
    
    
    #print('ReadoutTime: '+str(ReadOutTime))
    
    ExpTimes = [CCD_48['TEXPMS'], CCD_9['TEXPMS'], CCD_6['TEXPMS'], CCD_64['TEXPMS']]
    ExpTimes.sort()
    #print('ExpTimes: '+str(ExpTimes))
    
    TEXPIOFS = [-1,-1,-1,-1,-1,-1,-1]
    ExpIntervals = []
    x= 0
    ExtraOffset = 150
    CCDSEL = 0
    
    Flag_48 = False
    Flag_9 = False
    Flag_6 = False
    Flag_64 = False
    
    OffsetTime = 0
    
    for ExpTime in ExpTimes:
        if( ExpTime == 0):
            continue
        elif( ExpTime == CCD_48['TEXPMS'] and Flag_48 == False):
            Flag_48 = True
            #TEXPIOFS.insert(4, (ReadOutTime_max+ExtraOffset)*x)
            #x += 1
            #TEXPIOFS.insert(5, (ReadOutTime_max+ExtraOffset)*x)
            #ExpIntervals.append( (ReadOutTime_max+ExtraOffset)*x + ExpTime_48)
            
            TEXPIOFS.insert(4, int(round(OffsetTime/10,0)*10))
            OffsetTime = OffsetTime + (ReadOutTime_48+ExtraOffset)
            
            TEXPIOFS.insert(5, int(round(OffsetTime/10,0)*10))
            
            OffsetTime = OffsetTime + (ReadOutTime_48+ExtraOffset)
            
            ExpIntervals.append(ReadOutTime_48 + CCD_48['TEXPMS'] + ExtraOffset)
            CCDSEL += 48
            
        elif( ExpTime == CCD_9['TEXPMS'] and Flag_9 == False):
            Flag_9 = True
            #TEXPIOFS.insert(0, (ReadOutTime_max+ExtraOffset)*x)
            #x += 1
            #TEXPIOFS.insert(3, (ReadOutTime_max+ExtraOffset)*x)
            #ExpIntervals.append( (ReadOutTime_max+ExtraOffset)*x + ExpTime_9)
            
            TEXPIOFS.insert(0, int(round(OffsetTime/10,0)*10))
            OffsetTime = OffsetTime + (ReadOutTime_9+ExtraOffset)
            
            TEXPIOFS.insert(3, int(round(OffsetTime/10,0)*10))
            
            OffsetTime = OffsetTime + (ReadOutTime_9+ExtraOffset)
            
            ExpIntervals.append(ReadOutTime_9 + CCD_9['TEXPMS'] + ExtraOffset)
            CCDSEL += 9
            
        elif( ExpTime == CCD_6['TEXPMS'] and Flag_6 == False):
            Flag_6 = True
            #TEXPIOFS.insert(1, (ReadOutTime_max+ExtraOffset)*x)
            #x += 1
            #TEXPIOFS.insert(2, (ReadOutTime_max+ExtraOffset)*x)
            #ExpIntervals.append( (ReadOutTime_max+ExtraOffset)*x + ExpTime_6)
            
            TEXPIOFS.insert(1, int(round(OffsetTime/10,0)*10))
            OffsetTime = OffsetTime + (ReadOutTime_6+ExtraOffset)
            
            TEXPIOFS.insert(2, int(round(OffsetTime/10,0)*10))
            
            OffsetTime = OffsetTime + (ReadOutTime_6+ExtraOffset)
            
            ExpIntervals.append(ReadOutTime_6 + CCD_6['TEXPMS'] + ExtraOffset)
            CCDSEL += 6
            
        elif( ExpTime == CCD_64['TEXPMS'] and Flag_64 == False):
            Flag_64 = True
            #TEXPIOFS.insert(6, (ReadOutTime_max+ExtraOffset)*x)
            #ExpIntervals.append( (ReadOutTime_max+ExtraOffset)*x + ExpTime_64)
            
            TEXPIOFS.insert(6, int(round(OffsetTime/10,0)*10))
            
            OffsetTime = OffsetTime + (ReadOutTime_64+ExtraOffset)
            
            ExpIntervals.append(ReadOutTime_64 + CCD_64['TEXPMS'] + ExtraOffset)
            CCDSEL += 64
            
        x += 1
        #print('TEXPIOFS: '+str(TEXPIOFS))
    
    
    
    for x in range(TEXPIOFS.count(-1)):
        TEXPIOFS.remove(-1)
        
    #print('TEXPIOFS: '+str(TEXPIOFS))
    
    
    ExpIntervals
    ExpInterval = max(ExpIntervals)
    
    for FirstExpTime in ExpTimes:
        if( FirstExpTime != 0 ):
            break
    
    if( FirstExpTime <= max(TEXPIOFS) ):
        ExpInterval = ExpInterval + (max(TEXPIOFS) - FirstExpTime)
    
    TEXPIMS = int(round(ExpInterval,-2))
    #ExpInterval = ExpIntervals[len(ExpIntervals)-1] - int(FirstExpTime*3/4)
    
    
    #ExpInterval = int(ExpInterval - int(FirstExpTime*3/4))
    #print('TEXPIMS: '+str(TEXPIMS))
    NCCD = bin(CCDSEL).count('1')
    #print('NCCD: '+str(NCCD))
    
    return CCDSEL, NCCD, TEXPIOFS, TEXPIMS