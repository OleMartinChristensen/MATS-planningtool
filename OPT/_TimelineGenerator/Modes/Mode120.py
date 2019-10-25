# -*- coding: utf-8 -*-
"""Schedules the active Mode and saves the result in the Occupied_Timeline dictionary.

Part of Timeline_generator, as part of OPT.

"""

import logging, sys, csv, os, importlib
import ephem
from pylab import array, ceil, cos, sin, cross, dot, zeros, norm, pi, arccos, floor
from astroquery.vizier import Vizier
import skyfield.api


from OPT._Library import deg2HMS, Satellite_Simulator
from OPT import _Globals
from .Mode12X import UserProvidedDateScheduler

OPT_Config_File = importlib.import_module(_Globals.Config_File)
Logger = logging.getLogger(OPT_Config_File.Logger_name())


def Mode120(Occupied_Timeline):
    """Core function for the scheduling of Mode120.
    
    Determines if the scheduled date should be determined by simulating MATS or be user provided.
    
    Arguments:
        Occupied_Timeline (:obj:`dict` of :obj:`list`): Dictionary with keys equal to planned and scheduled Modes/CMDs with entries equal to their start and end time as a list.
        
    Returns:
        (tuple): tuple containing:
            (:obj:`dict` of :obj:`list`): Occupied_Timeline (updated with the result from the scheduled Mode). \n
            (str): Comment regarding the result of scheduling of the mode.
    
    """
    
    Settings = OPT_Config_File.Mode120_settings()
    
    if( Settings['automatic'] == False ):
        Occupied_Timeline, comment = UserProvidedDateScheduler(Occupied_Timeline, Settings)
    elif( Settings['automatic'] == True ):
        star_list = Mode120_date_calculator()
        
        Occupied_Timeline, comment = Mode120_date_select(Occupied_Timeline, star_list)
    
    return Occupied_Timeline, comment



#########################################################################################
#####################################################################################################



def Mode120_date_calculator():
    """Subfunction, Simulates MATS FOV and stars.
    
    Determines when stars are entering the FOV at an vertical offset-angle equal to *#V-offset*, and also being 
    located at a horizontal off-set angle equal to less than *#H-offset*, when pointing at the LP located at an altitude equal to *#pointing_altitude*. 
    Also determines when the optical axis is pointing towards a LP located at an altitude equal to *#LP_pointing_altitude* during the hypothetical attitude freeze. \n
    
    (# as defined in the *Configuration File*). \n
    
    Saves the date and parameters regarding the spotting of a star.
    Also saves relevant data to an .csv file located in Output/.
    
    Arguments:
        
    Returns:
        star_list ((:obj:`list` of :obj:`dict`)) or (str): A list containing dictionaries containing parameters for each time a star is spotted. Or just a date depending on 'automatic' in *Mode124_settings*.
    
    """
    
    Timeline_settings = OPT_Config_File.Timeline_settings()
    Mode120_settings = OPT_Config_File.Mode120_settings()
    
    
    "Simulation length and timestep"
    log_timestep = Mode120_settings['log_timestep']
    Logger.debug('log_timestep: '+str(log_timestep))

    timestep = Mode120_settings['timestep'] #In seconds
    Logger.info('timestep set to: '+str(timestep)+' s')
    
    duration = Timeline_settings['duration']
    Logger.info('Duration set to: '+str(duration)+' s')
    
    timesteps = int(ceil(duration / timestep)) + 2
    Logger.info('Total number of timesteps set to: '+str(timesteps)+' s')
    
    timeline_start = ephem.Date(Timeline_settings['start_date'])
    initial_time = ephem.Date( timeline_start + ephem.second*Mode120_settings['freeze_start'] )
    
    Logger.info('Initial simulation date set to: '+str(initial_time))
    
    
    "Get relevant stars"
    result = Vizier(columns=['all'], row_limit=200).query_constraints(catalog='I/239/hip_main',Vmag=Mode120_settings['Vmag'])
    star_cat = result[0]
    ROWS = star_cat[0][:].count()
    stars = []
    stars_dec = zeros((ROWS,1))
    stars_ra = zeros((ROWS,1))
    
    "Insert stars into Pyephem"
    for t in range(ROWS):
        s = "{},f|M|F7,{},{},{},2000/01/01 11:58:55.816"
        s = s.format(star_cat[t]['HIP'], deg2HMS(ra=star_cat[t]['_RA.icrs']), deg2HMS(dec=star_cat[t]['_DE.icrs']), star_cat[t]['Vmag'])
        stars.append(ephem.readdb(s))
        stars[t].compute(epoch='2000/01/01 11:58:55.816')
        stars_dec[t] = stars[t].dec
        stars_ra[t] = stars[t].ra
    
    Logger.debug('')
    Logger.debug('List of stars used: '+str(star_cat))
    Logger.debug('')
    
    "Calculate unit-vectors of stars"
    stars_x = cos(stars_dec)* cos(stars_ra)
    stars_y = cos(stars_dec)* sin(stars_ra)
    stars_z = sin(stars_dec)
    stars_r = array([stars_x,stars_y,stars_z])
    stars_r = stars_r.transpose()
    
    "Prepare the excel file output"
    star_list_excel = []
    star_list_excel.append(['Name'])
    star_list_excel.append(['t1'])
    star_list_excel.append(['long'])
    star_list_excel.append(['lat'])
    star_list_excel.append(['mag'])
    star_list_excel.append(['H_offset'])
    star_list_excel.append(['V_offset'])
    star_list_excel.append(['e_Hpmag'])
    star_list_excel.append(['Hpscat'])
    star_list_excel.append(['o_Hpmag'])
    star_list_excel.append(['Classification'])
    star_list_excel.append(['Optical Axis Dec (ICRS J2000, eq)'])
    star_list_excel.append(['Optical Axis RA (ICRS J2000, eq)'])
    star_list_excel.append(['Star Dec (ICRS J2000, eq)'])
    star_list_excel.append(['Star RA (ICRS J2000, eq)'])
    
    "Prepare the output"
    star_list = []
    
    "Pre-allocate space"
    lat_MATS = zeros((timesteps,1))
    long_MATS = zeros((timesteps,1))
    optical_axis = zeros((timesteps,3))
    stars_r_V_offset_plane = zeros((ROWS,3))
    stars_r_H_offset_plane = zeros((ROWS,3))
    stars_vert_offset = zeros((timesteps,ROWS))
    stars_hori_offset = zeros((timesteps,ROWS))
    stars_offset = zeros((timesteps,ROWS))
    r_V_offset_normal = zeros((timesteps,3))
    r_H_offset_normal = zeros((timesteps,3))
    star_counter = 0
    spotted_star_name = []
    spotted_star_timestamp = []
    spotted_star_timecounter = []
    skip_star_list = []
    MATS_P = zeros((timesteps,1))
    
    Dec_optical_axis = zeros((timesteps,1))
    RA_optical_axis = zeros((timesteps,1))
    
    angle_between_orbital_plane_and_star = zeros((timesteps,ROWS))
    
    "Constants"
    pointing_altitude = Mode120_settings['pointing_altitude']/1000 
    
    V_offset = Mode120_settings['V_offset']
    H_offset = Mode120_settings['H_offset']
    
    
    yaw_correction = Timeline_settings['yaw_correction']
    
    Logger.debug('H_offset set to [degrees]: '+str(H_offset))
    Logger.debug('V_offset set to [degrees]: '+str(V_offset))
    Logger.debug('yaw_correction set to: '+str(yaw_correction))
    
    TLE = OPT_Config_File.getTLE()
    Logger.debug('TLE used: '+TLE[0]+TLE[1])
    #MATS = ephem.readtle('MATS',TLE[0],TLE[1])
    
    #date = initial_time
    current_time = initial_time
    
    TimeSkips = 0
    Timeskip = Mode120_settings['TimeSkip']
    
    MATS_skyfield = skyfield.api.EarthSatellite(TLE[0], TLE[1])
    
    t = -1
    
    Logger.info('')
    Logger.info('Start of simulation of MATS for Mode120')
    ################## Start of Simulation ########################################
    "Loop and calculate the relevant angle of each star to each direction of MATS's FOV"
    #for t in range(timesteps):
    while( current_time-initial_time < ephem.second*duration):
        
        t += 1
        
        if( t != 0 ):
            if( t*timestep >= MATS_P[t-1]*(TimeSkips+1) ):
                current_time = ephem.Date(current_time+ephem.second*Timeskip)
                TimeSkips += 1
            else:
                current_time = ephem.Date(current_time+ephem.second*timestep)
            
        #current_time = ephem.Date(date+ephem.second*timestep*t)
        
        if( t*timestep % log_timestep == 0):
            LogFlag = True
        else:
            LogFlag = False
        
        Satellite_dict = Satellite_Simulator( 
                MATS_skyfield, current_time, Timeline_settings, pointing_altitude, LogFlag, Logger )
        
        MATS_P[t] = Satellite_dict['OrbitalPeriod [s]']
        lat_MATS[t] =  Satellite_dict['Latitude [degrees]']
        long_MATS[t] =  Satellite_dict['Longitude [degrees]']
        optical_axis[t] = Satellite_dict['OpticalAxis']
        Dec_optical_axis[t] = Satellite_dict['Dec_OpticalAxis [degrees]']
        RA_optical_axis[t] = Satellite_dict['RA_OpticalAxis [degrees]']
        r_H_offset_normal[t] = Satellite_dict['Normal2H_offset']
        r_V_offset_normal[t] = Satellite_dict['Normal2V_offset']
        
        
        ###################### Star-mapper ####################################
        
        if(t != 0):
            "Check position of stars relevant to pointing direction"
            for x in range(ROWS):
                
                "Skip star if it is not visible during this epoch"
                if(stars[x].name in skip_star_list):
                    continue
                
                "Check if a star has already been spotted during this orbit."
                if( stars[x].name in spotted_star_name ):
                    
                    time_until_far_outside_of_FOV = ephem.second*(180*MATS_P[t]/360)
                    
                    "If enough time has passed (half an orbit), the star can be removed from the exception list"
                    if((current_time - spotted_star_timestamp[spotted_star_name.index(stars[x].name)]) >= time_until_far_outside_of_FOV):
                        spotted_star_timestamp.pop(spotted_star_name.index(stars[x].name))
                        spotted_star_timecounter.pop(spotted_star_name.index(stars[x].name))
                        spotted_star_name.remove(stars[x].name)
                    continue
                
                
                
                "Total angle offset of the star compared to MATS's FOV"
                stars_offset[t][x] = arccos(dot(optical_axis[t],stars_r[0][x]) / (norm(optical_axis[t]) * norm(stars_r[0][x]))) /pi*180
                
                "Project 'star vectors' ontop pointing H-offset and V-offset plane"
                stars_r_V_offset_plane[x] = stars_r[0][x] - (dot(stars_r[0][x],r_V_offset_normal[t,0:3]) * r_V_offset_normal[t,0:3])
                
                stars_r_H_offset_plane[x] = stars_r[0][x] - (dot(stars_r[0][x],r_H_offset_normal[t]) * r_H_offset_normal[t]) 
                
                "Dot product to get the Vertical and Horizontal angle offset of the star in the FOV"
                stars_vert_offset[t][x] = arccos(dot(optical_axis[t],stars_r_V_offset_plane[x]) / (norm(optical_axis[t]) * norm(stars_r_V_offset_plane[x]))) /pi*180
                stars_hori_offset[t][x] = arccos(dot(optical_axis[t],stars_r_H_offset_plane[x]) / (norm(optical_axis[t]) * norm(stars_r_H_offset_plane[x]))) /pi*180
                
                "Determine sign of off-set angle where positive V-offset angle is when looking at higher altitude"
                if( dot(cross(optical_axis[t],stars_r_V_offset_plane[x]),r_V_offset_normal[t,0:3]) > 0 ):
                    stars_vert_offset[t][x] = -stars_vert_offset[t][x]
                if( dot(cross(optical_axis[t],stars_r_H_offset_plane[x]),r_H_offset_normal[t]) > 0 ):
                    stars_hori_offset[t][x] = -stars_hori_offset[t][x]
                
                
                "To be able to skip stars far outside the orbital plane of MATS"
                if( t == 1 ):
                    "For first loop of stars, calculate angle between stars and orbital plane"
                    angle_between_orbital_plane_and_star[t][x] = arccos( dot(stars_r[0][x], stars_r_V_offset_plane[x]) / norm(stars_r_V_offset_plane[x])) /pi*180
                    
                    "Make exception list for stars not visible during this epoch (relativiely far outside of orbital plane)"
                    if( ( abs(angle_between_orbital_plane_and_star[t][x]) > H_offset+(duration)/(365*24*3600)*360 and yaw_correction == False ) or 
                       ( abs(angle_between_orbital_plane_and_star[t][x]) > H_offset + abs(Timeline_settings['yaw_amplitude']) + (duration)/(365*24*3600)*360 and yaw_correction == True )):
                        
                        Logger.debug('Skip star: '+stars[x].name+', with angle_between_orbital_plane_and_star of: '+str(angle_between_orbital_plane_and_star[t][x])+' degrees')
                        skip_star_list.append(stars[x].name)
                        continue
                
                
                "Check that the star is entering at V-offset degrees and within the H-offset angle"
                if( stars_vert_offset[t][x] <= V_offset and stars_vert_offset[t-1][x] > V_offset and abs(stars_hori_offset[t][x]) < H_offset):
                    
                    if( t % log_timestep == 0):
                        Logger.debug('Star: '+stars[x].name+', with H-offset: '+str(stars_hori_offset[t][x])+' V-offset: '+str(stars_vert_offset[t][x])+' in degrees is available')
                    
                    "Add the spotted star to the exception list and timestamp it"
                    spotted_star_name.append(stars[x].name)
                    spotted_star_timestamp.append(current_time)
                    spotted_star_timecounter.append(t) 
                    
                    
                    "Log all relevent data for the star"
                    star_list_excel[0].append(stars[x].name)
                    star_list_excel[1].append(str(current_time))
                    star_list_excel[2].append(str(float(long_MATS[t])))
                    star_list_excel[3].append(str(float(lat_MATS[t])))
                    star_list_excel[4].append(str(stars[x].mag))
                    star_list_excel[5].append(str(stars_hori_offset[t][x]))
                    star_list_excel[6].append(str(stars_vert_offset[t][x]))
                    star_list_excel[7].append(str(star_cat[x]['e_Hpmag']))
                    star_list_excel[8].append(str(star_cat[x]['Hpscat']))
                    star_list_excel[9].append(str(star_cat[x]['o_Hpmag']))
                    star_list_excel[10].append(str(star_cat[x]['SpType']))
                    star_list_excel[11].append(str(Dec_optical_axis[t]))
                    star_list_excel[12].append(str(RA_optical_axis[t]))
                    star_list_excel[13].append(str(stars_dec[x]/pi*180))
                    star_list_excel[14].append(str(stars_ra[x]/pi*180))
                    
                    "Log data of star relevant to filtering process"
                    star_list.append({ 'Date': str(current_time), 'V-offset': stars_vert_offset[t][x], 'H-offset': stars_hori_offset[t][x], 
                                      'long_MATS': float(long_MATS[t]), 'lat_MATS': float(lat_MATS[t]), 
                                      'Dec_optical_axis': Dec_optical_axis[t], 'RA_optical_axis': RA_optical_axis[t], 
                                      'Vmag': stars[x].mag, 'Name': stars[x].name, 'Dec': stars_dec[x]/pi*180, 'RA': stars_ra[x]/pi*180 })
                    
                    star_counter = star_counter + 1
                    
            ######################### End of star_mapper #############################
        
    
    
    Logger.info('End of simulation for Mode120')
    
    
    "Write spotted stars to file"
    try:
        os.mkdir('Output')
    except:
        pass
    
    while(True):
        try:
            file_directory = os.path.join('Output',sys._getframe(1).f_code.co_name+'_Visible_Stars_'+_Globals.Config_File+'.csv')
            with open(file_directory, 'w', newline='') as write_file:
                writer = csv.writer(write_file, dialect='excel-tab')
                writer.writerows(star_list_excel)
            Logger.info('Available Stars data saved to: '+file_directory)
            #print('Available Stars data saved to: '+file_directory)
            break
        except PermissionError:
            Logger.error(file_directory+' cannot be overwritten. Please close it')
            data = input('Enter anything to try again or 1 to exit')
            if( data == '1'):
                sys.exit()
    
    Logger.debug('Visible star list to be filtered:')
    for x in range(len(star_list)):
        Logger.debug(str(star_list[x]))
    Logger.debug('')
    
    Logger.debug('Exit '+str(__name__))
    Logger.debug('')
    
    
    return(star_list)



#####################################################################################################
#####################################################################################################



def Mode120_date_select(Occupied_Timeline, star_list):
    """Subfunction, Schedules a simulated date.
    
    A date is selected for which the brightest star is visible at the minimum amount of H-offset in the FOV.
    If the date is occupied the same star will be selected with the 2nd least amount of H-offset and so on. Another star will be chosen in chronological
    order of availabilty if all the times the brightest star is available are occupied.
    
    Arguments:
        Occupied_Timeline (:obj:`dict` of :obj:`list`): Dictionary with keys equal to planned and scheduled Modes/CMDs with entries equal to their start and end time as a list.
        star_list ((:obj:`list` of :obj:`dict`)): A list containing dictionaries containing parameters for each time a star is spotted.
        
    Returns:
        (tuple): tuple containing:
            (:obj:`dict` of :obj:`list`): Occupied_Timeline (updated with the result from the scheduled Mode). \n
            (str): Comment regarding the result of scheduling of the mode.
    
    """
    
    Mode120_settings = OPT_Config_File.Mode120_settings()
    Timeline_settings = OPT_Config_File.Timeline_settings()
    
    
    Logger.info('Start of filtering function')
    
    
    if( len(star_list) == 0):
        Mode120_comment = 'Stars not visible (Empty star_list)'
        
        Logger.warning(Mode120_comment)
        #input('Enter anything to acknowledge and continue')
    
        return Occupied_Timeline, Mode120_comment
    
    star_min_mag_H_offset = []
    
    star_H_offset = [star_list[x]['H-offset'] for x in range(len(star_list))]
    #print('star_H_offset')
    #print(star_H_offset)
    star_V_offset = [star_list[x]['V-offset'] for x in range(len(star_list))]
    star_date = [star_list[x]['Date'] for x in range(len(star_list))]
    star_mag = [star_list[x]['Vmag'] for x in range(len(star_list))]
    star_name = [star_list[x]['Name'] for x in range(len(star_list))]
    long_MATS = [star_list[x]['long_MATS'] for x in range(len(star_list))]
    lat_MATS = [star_list[x]['lat_MATS'] for x in range(len(star_list))]
    Dec_optical_axis = [star_list[x]['Dec_optical_axis'] for x in range(len(star_list))]
    RA_optical_axis = [star_list[x]['RA_optical_axis'] for x in range(len(star_list))]
    
    star_mag_sorted = [abs(x) for x in star_mag]
    star_mag_sorted.sort()
    
    Logger.info('Brightest star magnitude: '+str(min(star_mag)))
    arbitraryLargeNumber = 1000
    
    "Extract all the H-offsets for the brightest star. Allows scheduling in order of rising H-offset for the brightest star"
    for x in range(len(star_list)):
        if( min(star_mag) == star_mag[x]):
            star_min_mag_H_offset.append( star_H_offset[x])
            
        #Just add an arbitrary large H-offset value for stars other than the brightest to keep the list the same length.
        #This will also allow all instances with the brightest star to be scheduled first. Then later in random magnitude order.
        else:
            star_min_mag_H_offset.append(arbitraryLargeNumber)
            "Increase the arbitraryLargeNumber to keep H-offsets different, which allow scheduling of stars with other magnitudes than the brightest if needed"
            arbitraryLargeNumber += 1
    
    
    
    "Extract and sort the H-offsets."
    star_H_offset_abs = [abs(x) for x in star_min_mag_H_offset]
    
    star_H_offset_sorted = [abs(x) for x in star_min_mag_H_offset]
    star_H_offset_sorted.sort()
    Logger.debug('star_H_offset_abs: '+str(star_H_offset_abs))
    Logger.debug('star_H_offset_sorted: '+str(star_H_offset_sorted))
    
    
    restart = True
    iterations = 0
    ## Selects date based on min H-offset, if occupied, select date for next min H-offset
    while( restart == True):
        
        ## If all available dates for the brightest star is occupied, no Mode120 will be schedueled
        if( len(star_min_mag_H_offset) == iterations):
            Mode120_comment = 'No available time for Mode120 using the brightest available star'
            Logger.warning(Mode120_comment)
            #input('Enter anything to ackknowledge and continue')
            return Occupied_Timeline, Mode120_comment
        
        restart = False
        
        #Extract index of  minimum H-offset for first iteration, 
        #then next smallest if 2nd iterations needed and so on. If all 
        x = star_H_offset_abs.index(star_H_offset_sorted[iterations])
        
        StartDate = star_date[x]
        
        StartDate = ephem.Date(ephem.Date(StartDate)-ephem.second*(Mode120_settings['freeze_start']))
        
        endDate = ephem.Date(StartDate+ephem.second* (Mode120_settings['freeze_start'] + Mode120_settings['freeze_duration'] + Timeline_settings['mode_separation']) )
        
        "Check that the scheduled date is not before the start of the timeline"
        if( StartDate < ephem.Date(OPT_Config_File.Timeline_settings()['start_date']) ):
            iterations = iterations + 1
            restart = True
            continue
        
        ## Extract Occupied dates and if they clash, restart loop and select new date
        for busy_dates in Occupied_Timeline.values():
            if( busy_dates == []):
                continue
            else:
                "Extract the start and end date of each instance of a scheduled mode"
                for busy_date in busy_dates:
                    if( busy_date[0] <= StartDate <= busy_date[1] or 
                           busy_date[0] <= endDate <= busy_date[1] or
                       (StartDate < busy_date[0] and endDate > busy_date[1])):
                        
                        iterations = iterations + 1
                        restart = True
                        break
    
    
    
    
    comment = ('Star name:'+star_name[x]+', V-offset: '+str(round(star_V_offset[x],2))+', H-offset: '+str(round(star_H_offset[x],2))+', V-mag: '+str(star_mag[x])+', Number of times date changed: '+str(iterations)
        +', MATS (long,lat) in degrees = ('+str(long_MATS[x])+', '+str(lat_MATS[x])+'), optical-axis Dec (J2000 ICRS): '+str(Dec_optical_axis[x])+'), optical-axis RA (J2000 ICRS): '+str(RA_optical_axis[x])+
    '), star Dec (J2000 ICRS): '+str(star_list[x]['Dec'])+', star RA (J2000 ICRS): '+str(star_list[x]['RA']))
    
    
    Occupied_Timeline['Mode120'].append( (StartDate, endDate) )
    
    return Occupied_Timeline, comment
    