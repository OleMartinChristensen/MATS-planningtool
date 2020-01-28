%This function uses 1D vertical profiles to calculate J factors in n-D

function [Jhart,Jsrc,Jlya,J3,J2] = Jfactors(O_v, O2_v, O3_v, N2_v, zenitangle, z)

load sigma.mat
pathl = pathleng(z, zenitangle) * 1e5;  %[km -> cm]
% O2_v(end) = O2_v(end) * 15.7;%1e2; %to account for O2 above 110km
% N2_v(end) = N2_v(end) * 15.7;
% O_v(end) = O_v(end);% * 16.9;
tau = (O_v*sO' + O2_v*sO2' + O3_v*sO3' + N2_v*sN2')' * pathl';

JO3 = irrad.*sO3 * ones(1,length(z)) .* exp(-tau);
JO2 = irrad.*sO2 * ones(1,length(z)) .* exp(-tau);
JO3(tau==0) = 0;
JO2(tau==0) = 0;

hartrange = wave>210 & wave<310;
srcrange = wave>122 & wave<175;
lyarange = 28; % wavelength = 121.567 nm
Jhart = sum(JO3(hartrange,:));
Jsrc = sum(JO2(srcrange,:));
Jlya = JO2(lyarange,:);

J3 = sum(JO3);
J2 = sum(JO2);

% [~,~,Jhart,~] = ndgrid(x,y,Jhart,t);
% [~,~,Jsrc,~] = ndgrid(x,y,Jsrc,t);
% [~,~,Jlya,~] = ndgrid(x,y,Jlya,t);
% [~,~,J3,~] = ndgrid(x,y,J3,t);
% [~,~,J2,~] = ndgrid(x,y,J2,t);


end
