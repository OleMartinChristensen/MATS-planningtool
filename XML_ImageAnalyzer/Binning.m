function Matrix_Binned = Binning(NRSKIP, NRBIN, NROW, NCSKIP, NCBIN, NCOL, Matrix)
% Takes a limb radiance matrix representing the FOV of the limb instrument
% (511x2047 pixels). Binning is applied to each element depending on the
% input. Outputs the binned limb radiance matrix. 

%%
binnedROWS = NROW;
binnedCOLS = NCOL;
%binnedROWS = 50;
%binnedCOLS = 10;

ROWindexStep = NRBIN;
COLindexStep = NCBIN;
%ROWindexStep = dimension(1) / binnedROWS;
%COLindexStep = dimension(2) / binnedCOLS;

dimension = size(Matrix);

%% ROW Binning %%
for COLindex = 1:dimension(2)
    ROWindexNew = 0;
    for ROWindex = NRSKIP+1:ROWindexStep:NRSKIP+NROW*NRBIN
        ROWindexNew = ROWindexNew + 1;
        
        Matrix_ROWBinned(ROWindexNew,COLindex) = sum(Matrix(ROWindex:ROWindex+(ROWindexStep-1), COLindex));
        
    end
end

%dimensionROWBinned = size(limb_radiance_ROWBinned);

%% COL Binning %%
for ROWindex = 1:binnedROWS
    COLindexNew = 0;
    for COLindex = NCSKIP+1:COLindexStep:NCSKIP+NCBIN*NCOL
        COLindexNew = COLindexNew + 1;
        
        Matrix_Binned(ROWindex,COLindexNew) = sum(Matrix_ROWBinned(ROWindex, COLindex:COLindex+(COLindexStep-1)));
        
    end
end


end
