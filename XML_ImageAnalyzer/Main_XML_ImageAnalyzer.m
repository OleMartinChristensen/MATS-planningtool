
clear variables, close all

File = fopen('XML_TIMELINE__FROM__Output_Science_Mode_Timeline__OPT_Config_File.xml');

%View angle and zenith angle for the Limb radiance generation program.
%Zenith angle only toggles either night or day time at at a breakpoint of 100.6 degrees
viewAngle = 35; %viewAngle of 35 (29?) gives the least amount of compression
zenithAngle = 110; %NightGlow gives the least amount of compression

[Total_ImagesSize, TotalNumberOfSnapShots, TotalNumberOfOperationalModePhotos] = ...
    XML_ImageAnalyzer(File, viewAngle, zenithAngle);

fclose('all');