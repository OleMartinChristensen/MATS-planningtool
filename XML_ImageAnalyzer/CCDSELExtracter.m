function [IndividualCCDSEL] = CCDSELExtracter(CCDSEL)
%CCDSELExtracter 
%   Extract the individual CCDSEL (64, 32, 16, 8, 4, 2, 1) arguments 
%   from a CCDSEL argument (1-127) assuming the CCDSEL argument is valid.
%   Return an array containing the individual CCDSEL arguments as numbers.

CCDSELs = [64, 32, 16, 8, 4, 2, 1];
index = 0;
%IndividualCCDSEL = []

for x = 1:length(CCDSELs)
CCD = CCDSELs(x);
    if( CCDSEL ~= 0 )
        rest = CCDSEL; % CCD
    
        if( ismember(rest,CCDSELs) )
            index = index + 1;
            IndividualCCDSEL(index) = rest;
            CCDSEL = CCDSEL - rest;
            if( CCD <= CCDSEL )
                index = index + 1;
                IndividualCCDSEL(index) = CCD;
                CCDSEL = CCDSEL - CCD
            end
        else
        %elif( rest == 0 ):
            %IndividualCCDSEL.append(CCD)
            %CCDSEL -= CCD
            if( CCD <= CCDSEL)
                index = index + 1;
                IndividualCCDSEL(index) = CCD;
                CCDSEL = CCDSEL - CCD;

            end
            
        end
    end
end
end

