function [limb_radianceUpscaled, noise_radianceUpscaled] = LimbMatrixCalculator(viewAngle, zenithAngle, noise)
%LimbMatrixCalculator Creates a matrix respresenting the Limb radiance.
%   Uses Main_hwind_v11 to simulate limb_radiance as a 171x683 matrix. Then
%   increases the number of elements by 9 by adding random noise to each
%   element. The allows each element in the matrix (513x to be viewed as a single
%   pixel on the instrument which has 511x2047 pixels. 


f = 0.261; %focal length in m
heightCCDarea = 0.0069; %m
widthCCDarea = 0.0276; %m
FullVFOV_of_FullCCD = 2 * atan( heightCCDarea/2 / f); %radians
FullHFOV_of_FullCCD = 2 * atan( widthCCDarea/2 / f); %radians

VFOVofInterestedArea = 0.91; %degrees
HFOVofInterestedArea = 5.67; %degrees



NumberOfCCDsPerROW = 171; %1/3 of the total numbers of pixels per row. Each pixel will be increased to 9 pixels with rand values added
NumberOfCCDsPerCOL = 683; %1/3 of the total numbers of pixels per column. Each pixel will be increased to 9 pixels with rand values added


limb_radiance=Main_hwind_v11(NumberOfCCDsPerROW, NumberOfCCDsPerCOL, viewAngle, zenithAngle, FullVFOV_of_FullCCD, FullHFOV_of_FullCCD);

%% Make 9 times more pixels to correspond to the whole instrument sensor (511x2047 pixels)
% The new pixels will have normal distribution noise values added to them.
%noise = 0.01; % The magnitude of the added noise, expressed as a part of the actual value (0.01=1%)
for ROW = 1:NumberOfCCDsPerROW
    
    for COL = 1:NumberOfCCDsPerCOL
        
        for UpScaledROW = (ROW-1)*3+1:(ROW-1)*3+3
            for UpScaledCOL = (COL-1)*3+1:(COL-1)*3+3
                limb_radianceUpscaled(UpScaledROW, UpScaledCOL) = limb_radiance(ROW,COL)*(1+randn()*noise);
                
            end
        end
        
    end
end

noise_radianceUpscaled = limb_radianceUpscaled./limb_radianceUpscaled .* randn();
save('limb_radianceUpscaled.mat','limb_radianceUpscaled');

end

