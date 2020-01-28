function [TotalImagesSize, TotalNumberOfSnapShots, TotalNumberOfOperationalModePhotos] = XML_ImageAnalyzer(File,viewAngle,zenithAngle)
% XMLImageAnalyzer Goes through an XML, line by line, and estimates the amount of Images
% taken and their combined size.
% 
% An atmospheric and gravitation wave model creates a single limb radiance matrix which is used 
% to estimate the values of the CCDs whenever JPEG compression is applied.
% Note that only a single scene is generated for the CCDs, and is only applicable to
% pointing altitude of about 92500 km, meaning that
% JPEG compression estimation for other pointing altitudes and the nadir CCD is not accurate.
% The same scene is though still used to estimate JPEG compression for pointing
% altitudes up to 120 km. For other pointing altitudes and the nadir CCD a
% matrix just containing noise is used instead.
% 
%
% Input:
%   File: The XML file, as a file, using fopen.
%   viewAngle: The viewangle (degrees) of the atmospheric waves, implemented in the
%   Atmospheric model to generate a radiance scene for the instrument.
%   zenithAngle: The solar angle (degrees). Determines if the Atmospheric
%   model will use dayglow or nightglow. <=100.6 gives dayglow. >100.6
%   gives nightglow. Nightglow is recommended as nightglow gives a larger
%   compression ratio (from testing).
%   
% Output:
%   TotalImagesSize: The combined size of all taken images in bytes.
%   TotalNumberOfSnapShots: The total number of snapshots taken.
%   TotalNumberOfOperationalModePhotos: An estimated amount of images taken
%   while the payload is in operational mode. 

%%
MODE = 2; %Keeps track of the current mode used
OperationTime = 0; %Keeps track of how long the instrument was in operation mode
relativeTime = 0; 
TotalImagesSize = 0;
TotalNumberOfOperationalModePhotos = 0;


noise = 0.01; %Maximum possible signal/noise ratio which is added to each element in the limb radiance array
[LimbRadianceMatrix, noise_radianceUpscaled] = LimbMatrixCalculator(viewAngle, zenithAngle, noise);


CCDs = [1,2,4,8,16,32,64];
CCD_settings = containers.Map('KeyType', 'uint32', 'ValueType', 'any');

%%
for x = 1:length(CCDs)
    CCD_settings(CCDs(x)) = containers.Map(["PWR", "WDW", "JPEGQ", "SYNC", "TEXPMS", "GAIN", "NFLUSH", ...
                                "NRSKIP", "NRBIN", "NROW", "NCSKIP", "NCBIN", "NCOL", "NCBINFPGA", "SIGMODE"], ...
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]);
end
    

CurrentCMD = "None"; %Keeps track of the current CMD in the XML
TotalNumberOfSnapShots = 0;
CurrentMode = 2;
pointing_altitude = 92500;
OperationModeRelativeTime = "None";
CCDArguments = ["PWR"; "WDW"; "JPEGQ"; "SYNC"; "TEXPIMS"; "TEXPMS"; "GAIN"; "NFLUSH"; "NRSKIP"; "NRBIN"; "NROW"; "NCSKIP"; 
                "NRBIN"; "NROW"; "NCSKIP"; "NRBIN"; "NROW"; "NCSKIP"; "NCBIN"; "NCOL"; "NCBINFPGA"; "SIGMODE"];
dimension = size(CCDArguments);
NumberOfCCDArguments = dimension(1);

%% Loops through the lines in the XML and first checks when a CMD is scheduled
% if a CMD is scheduled the loop then checks for the row where the argument is
% given.
while(true)
    myline = fgetl(File);  % For each line, read it to a string 
    if( myline == -1 )
        break
    end
        
        if( contains(myline, '<scenarioDuration>') )
            Timeline_duration = ArgumentExtracter(myline);
        
        elseif(contains(myline, 'mnemonic="TC_pafMODE"'))
            CurrentCMD = "TC_pafMODE";
        
        
        
        elseif(contains(myline, 'mnemonic="TC_pafCCDSNAPSHOT"'))
            CurrentCMD = "TC_pafCCDSNAPSHOT";
        % MAKE SURE TC_pafCCD is checked last as TC_pafCCD is also part of many other CMDs #######
        elseif(contains(myline, 'mnemonic="TC_pafCCD"'))
            if( CurrentMode == 1 )
                error('Error in XML. Changing CCD settings in Operation Mode is not acceptable\n');
                %break
            else
                CurrentCMD = "TC_pafCCD";
            end
            
        % End of XML Timeline, check if in Operation Mode ####
        elseif( contains(myline, '</InnoSatTimeline>'))
            if( CurrentMode == 1 )
                DurationOfOperation = Timeline_duration - OperationModeRelativeTime;
                
                if( pointing_altitude < 120000 )
                [ImagesSize, NumberOfOperationalModePhotos] = ...
                    Operational_Images_Size_Calculator(CCD_settings, ...
                    DurationOfOperation*1000, ...
                    CCDs, LimbRadianceMatrix );
                else
                    [ImagesSize, NumberOfOperationalModePhotos] = Operational_Images_Size_Calculator(CCD_settings, ...
                    DurationOfOperation*1000, ...
                    CCDs, noise_radianceUpscaled );
                end
                
                TotalNumberOfOperationalModePhotos = TotalNumberOfOperationalModePhotos + ...
                    NumberOfOperationalModePhotos;
                TotalImagesSize = TotalImagesSize + ImagesSize;
            end
         elseif(contains(myline, 'mnemonic="TC_acfLimbPointingAltitudeOffset"'))
            CurrentCMD = "TC_acfLimbPointingAltitudeOffset";
            
            
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        %%%% After checking for CMDs, check for arguments for the current CMD %%
        
        elseif( CurrentCMD == "TC_acfLimbPointingAltitudeOffset")
            if( contains(myline, '<Final>' ))
                pointing_altitude = ArgumentExtracter(myline);
            end
        elseif( CurrentCMD == "TC_pafMODE")
            if( contains(myline, '<relativeTime>' ))
                relativeTime = ArgumentExtracter(myline);
            elseif( contains(myline, 'mnemonic="MODE"'))
                MODE = ArgumentExtracter(myline);
                
                %% Start of Operation Mode ##
                if( CurrentMode == 2 && MODE == 1)
                    OperationModeRelativeTime = relativeTime;
                    
                %% End of Operation Mode ##
                elseif( CurrentMode == 1 && MODE == 2)
                    IdleModeRelativeTime = relativeTime;
                    DurationOfOperation = IdleModeRelativeTime - OperationModeRelativeTime;
                    
                    if( pointing_altitude < 120000 )
                        [ImagesSize, NumberOfOperationalModePhotos] = Operational_Images_Size_Calculator(CCD_settings, ...
                        DurationOfOperation*1000, ...
                        CCDs, LimbRadianceMatrix );
                    else
                        [ImagesSize, NumberOfOperationalModePhotos] = Operational_Images_Size_Calculator(CCD_settings, ...
                        DurationOfOperation*1000, ...
                        CCDs, noise_radianceUpscaled );
                    end

                    TotalNumberOfOperationalModePhotos = TotalNumberOfOperationalModePhotos + ...
                        NumberOfOperationalModePhotos;
                    TotalImagesSize = TotalImagesSize + ImagesSize;
                end
                CurrentMode = MODE;
            end
                
        elseif( CurrentCMD == "TC_pafCCD" )
            if( contains(myline, 'CCDSEL'))
                ExtractedCCDSEL = ArgumentExtracter(myline);
                IndividualCCDSEL = CCDSELExtracter(ExtractedCCDSEL);
                
            else
                for x = 1:NumberOfCCDArguments
                %for argument in CCDArguments:
                    argument = CCDArguments(x,:);
                    if( contains(myline, 'mnemonic="'+argument+'"') )
                        argumentValue = ArgumentExtracter(myline);
                        for y = 1:length(IndividualCCDSEL)
                            CCDSEL = IndividualCCDSEL(y);
                            CCDSEL_settings = CCD_settings(CCDSEL);
                            CCDSEL_settings(argument) = argumentValue;
                            
                        end
                    end
                end
            end
                
        elseif( CurrentCMD == "TC_pafCCDSNAPSHOT" )
            
            if( contains(myline,'mnemonic="CCDSEL"') )
                CCDSEL = ArgumentExtracter(myline);
                IndividualCCDSEL = CCDSELExtracter(CCDSEL);
                
                for y = 1:length(IndividualCCDSEL)
                    CCDSEL = IndividualCCDSEL(y);
                    CCDSEL_settings = CCD_settings(CCDSEL);
                    if( CCDSEL_settings('WDW') == 127 )
                        BytesPerPixel = 2;
                        TotalImagesSize = TotalImagesSize + CCDSEL_settings('NCOL') * CCDSEL_settings('NROW') * BytesPerPixel;
                    else
                        if( pointing_altitude < 120000 )
                            TotalImagesSize = TotalImagesSize + ImageSizeCalculator(CCDSEL_settings,LimbRadianceMatrix);
                        else
                            TotalImagesSize = TotalImagesSize + ImageSizeCalculator(CCDSEL_settings,noise_radianceUpscaled);
                        end
                    TotalNumberOfSnapShots = TotalNumberOfSnapShots + 1;
                    end
                end
            end
        end
end
