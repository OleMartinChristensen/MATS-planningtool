function ImageSize = ImageSizeCalculator(CCDSEL_settings, LimbRadianceMatrix)
%Calculates the size of the Image after JPEG compression depending on a
%limb radiance matrix and the binning settings. The brightest element of
%the matrix is assumed to saturate the CCD on the instrument, and the
%matrix is scaled to represent this. JPEG
%compression is performed by saving the 12 bit matrix to a file.
%
%Input:
%   CCDSEL_settings: Map object mapping towards another map object.
%   Contain the settings of each individual
%   CCD. The first keys represent the CCDSEL value of each CCD as a double.
%   The second keys represent each CCD setting, as string.
%   LimbRadianceMatrix: A matrix representing the limb radiance of each
%   pixel on the instrument.



NROWlist = CCDSEL_settings('NROW');
NCOLlist = CCDSEL_settings('NCOL');
JPEGQlist = CCDSEL_settings('JPEGQ');
NRSKIP = CCDSEL_settings('NRSKIP');
NRBIN = CCDSEL_settings('NRBIN');
NCSKIP = CCDSEL_settings('NCSKIP');
NCBIN = CCDSEL_settings('NCBIN');
WDW = CCDSEL_settings('WDW');


Matrix = eye(length(NROWlist), length(NCOLlist));
Matrix3Dimension = Matrix;
for i = 1:length(JPEGQlist)-1
    Matrix3Dimension = cat(3,Matrix3Dimension,Matrix);
end

bytesCompressed = Matrix3Dimension;
bytesUncompressed = Matrix3Dimension;
CR = Matrix3Dimension;


viewAngle = 35; %viewAngle of 35 (29?) gives the least amount of compression
zenithangle = 110; %NightGlow gives the least amount of compression
viewindex = 0;
for viewAngle = viewAngle
    viewindex = viewindex +1;
    
    %% Calculate image size and compression rate for different values of NCOL, NROW, JPEGQ
    x=0;
    ImageNumber = 0;
    qualityIndex = 0;
    for JPEGQ = JPEGQlist
        qualityIndex = qualityIndex +1;
        %%%%%%%%%%%%%%%%%%%
        %JPEGQ = 85;
        %%%%%%%%%%%%%%%%%%%
        row = 0;
        for NROW = NROWlist
            row = row + 1;
            NROW;
            col = 0;
            for NCOL = NCOLlist
                col = col +1;
                
                ImageNumber = ImageNumber + 1;
                
                limb_radianceBinned = Binning(NRSKIP,NRBIN,NROW,NCSKIP,NCBIN,NCOL,LimbRadianceMatrix);
                
                %Scale the image to fit 16 bit assuming the maximum value to have been a
                %saturated value
                limb_radianceBinned_rescaled16bit=rescale(limb_radianceBinned,0,2^16-1,'inputMin',0);
                limb_radianceBinned_16bit = uint16(limb_radianceBinned_rescaled16bit);
                imwrite(limb_radianceBinned_16bit,'limbBinned16bit.pgm')
                waitfor('imwrite')
                stats=dir('limbBinned16bit.pgm');
                bytesUncompressed2(row,col,qualityIndex) = stats.bytes;
                
                if( WDW ~= 7)
                    if( WDW == 128 ) %If WDW mode is set to automatic, assume WDW mode.
                        WDW = 4
                    end
                    dimension = size(limb_radianceBinned);
                    WDWindex = 0;
                    for WDW = WDW
                        WDWindex = WDWindex +1;
                        for i = 1:dimension(1)
                            for j = 1:dimension(2)
                                limb_radianceBinned_12bit(i,j,WDWindex) = bitshift(limb_radianceBinned_16bit(i,j),-WDW);
                                for bit = 13:16
                                    limb_radianceBinned_12bit(i,j,WDWindex) = bitset(limb_radianceBinned_12bit(i,j,WDWindex),bit,0);
                                end
                                
                            end
                        end
                    end
                    imwrite(limb_radianceBinned_12bit(:,:,1), 'limbBinned12bit.jpeg','bitdepth',12, 'quality',JPEGQ, 'mode', 'lossy')
                    waitfor('imwrite')
                    stats=dir('limbBinned12bit.jpeg');
                    bytesCompressed2(row,col,qualityIndex) = stats.bytes;
                    ImageSize = stats.bytes;
                    CR2(row,col,qualityIndex,viewindex) = bytesCompressed2(row,col,qualityIndex) / bytesUncompressed2(row,col,qualityIndex);
                    
                elseif( WDW == 7 )
                    ImageSize = stats.bytes;
                end
                
                
                
                
                
                %CR(row,col,qualityIndex) = bytesCompressed(row,col,qualityIndex) / (NROW * NCOL * 2)
                
                
                
                
                %             %Scale the image to fit 16 bit assuming the maximum value to have been a
                %             %saturated value
                %             limb_radiance_rescaled16bit=rescale(limb_radiance,0,2^16-1,'inputMin',0);
                %             limb_radiance_16bit = uint16(limb_radiance_rescaled16bit);
                %
                %             dimension = size(limb_radiance);
                %             WDW = 4;
                %             for i = 1:dimension(1)
                %                 for j = 1:dimension(2)
                %                     limb_radiance_12bit(i,j) = bitshift(limb_radiance_16bit(i,j),-WDW);
                %                     for bit = 13:16
                %                         limb_radiance_12bit(i,j) = bitset(limb_radiance_12bit(i,j),bit,0);
                %                     end
                %
                %
                %                 end
                %
                %             end
                %
                %             %
                %             imwrite(limb_radiance_12bit, 'limb12bit.jpeg','bitdepth',12, 'quality',JPEGQ, 'mode', 'lossy')
                %             imwrite(limb_radiance_16bit,'limb16bit.jpeg','bitdepth',16, 'quality',JPEGQ)
                %             %imwrite(limb_radiance_16bit,'limb16bit.png','bitdepth',16)
                %             imwrite(limb_radiance_16bit,'limb16bit.tif', 'Compression', 'none')
                %             imwrite(limb_radiance_16bit,'limb16bit.pgm')
                %             %imwrite(limb_radiance_16bit,'limb.bmp')
                %
                %             stats=dir('limb12bit.jpeg');
                %             bytesCompressed(row,col,qualityIndex) = stats.bytes;
                %             stats=dir('limb16bit.pgm');
                %             bytesUncompressed(row,col,qualityIndex) = stats.bytes;
                %             %CR(row,col,qualityIndex) = bytesCompressed(row,col,qualityIndex) / (NROW * NCOL * 2)
                %             CR(row,col,qualityIndex) = bytesCompressed(row,col,qualityIndex) / bytesUncompressed(row,col,qualityIndex);
            end
        end
    end
    
end



% ImageCompressed = imread('limb16bit.jpeg');
% ImageUncompressed = imread('limb16bit.pgm');
% Image12bitCompressed = imread('limb12bit.jpeg');
%
% subplot(2,2,1), imshow(ImageCompressed)
% hold on
% subplot(2,2,2), imshow(ImageUncompressed)
% subplot(2,2,3), imshow(Image12bitCompressed, [0,2^12-1])
% hold off
%
%
% figure()
% ImageBinnedUncompressed = imread('limbBinned16bit.pgm');
% ImageBinned12bitCompressed = imread('limbBinned12bit.jpeg');
% subplot(2,1,1), imshow(ImageBinnedUncompressed)
% hold on
% subplot(2,1,2), imshow(ImageBinned12bitCompressed, [0,2^12-1])
% hold off
%
% save('ImageSizeMatrix.mat', 'bytesCompressed')
% save('CRMatrix.mat', 'CR')
%
% figure()
% subplot(2,3,1), imshow(limb_radianceBinned_12bit(:,:,1), [0,2^12-1])
% %title('WDW = 0')
% %hold on
% % subplot(2,3,2), imshow(limb_radianceBinned_12bit(:,:,2), [0,2^12-1])
% % title('WDW = 1')
% % %hold on
% % subplot(2,3,3), imshow(limb_radianceBinned_12bit(:,:,3), [0,2^12-1])
% % title('WDW = 2')
% % %hold on
% % subplot(2,3,4), imshow(limb_radianceBinned_12bit(:,:,4), [0,2^12-1])
% % title('WDW = 3')
% % %hold on
% % subplot(2,3,5), imshow(limb_radianceBinned_12bit(:,:,5), [0,2^12-1])
% % title('WDW = 4')
% % hold off
end