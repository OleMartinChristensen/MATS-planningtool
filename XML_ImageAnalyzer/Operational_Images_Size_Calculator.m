function [SizeOfImages, TotalNumberOfImages] = Operational_Images_Size_Calculator(CCD_settings,duration, CCDs, LimbRadianceMatrix)
%Operational_Images_Size_Calculator Calculates the number of Images taken
%and their size.
%   
SizeOfImages = 0;
TotalNumberOfImages = 0;
%BytesPerPixel = 1.5 #Bytes


%disregarded, disregarded, disregarded, TEXPIMS = _Library.SyncArgCalculator(CCD_settings, ExtraOffset, ExtraIntervalTime)


for x = 1:length(CCDs)
    CCDSEL = CCDs(x);
    CCDSEL_settings = CCD_settings(CCDSEL);
    
    if( CCDSEL_settings('TEXPMS') == 0 | CCDSEL_settings('PWR') == 0 )
        continue
    %Nadir Camera uses are very rough estimation of the Image size without
    %using a limb radiance array.
    elseif( CCDSEL == 64)
        %Check if either 12bit or 16bit images are readout (which depends on
        %the value of JPEGQ)
        if( CCDSEL_settings('JPEGQ') <= 100 )

            Compression = 0.67; %Rough JPEG compression value taken from tests
            BytesPerPixel = 1.5 * Compression;
        else
            BytesPerPixel = 2;
        end
        NumberOfImages = duration/CCDSEL_settings('TEXPIMS');
        SizeOfImages = SizeOfImages + round(CCDSEL_settings('NCOL') * CCDSEL_settings('NROW') * BytesPerPixel * NumberOfImages, 0);
    %The rest of the CCDs
    else
        NumberOfImages = duration/CCDSEL_settings('TEXPIMS');
        SizeOfImages = SizeOfImages + round(ImageSizeCalculator(CCDSEL_settings,LimbRadianceMatrix) * NumberOfImages, 0);
    end
    TotalNumberOfImages = TotalNumberOfImages + NumberOfImages;
    
end
end

