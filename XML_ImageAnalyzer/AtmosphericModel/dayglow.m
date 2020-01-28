% This version can take n-D matrix for O, O2, O3, N2, T, J, g
function [Vat, Vat_from_O3, Vat_from_O2, Vat_from_barth, Vat_from_gA] ...
    = dayglow(O, O2, O3, N2, T, Jhart, Jsrc, Jlya, gA)

M = O + O2 + N2;
k1 = 4.7e-33 * (300./T).^2;
k2_O2 = 4e-17;% *1e-6; %[cm3s-1]
k2_N2 = 2.2e-15;% *1e-6; %[cm3s-1]
k2_O = 8e-14;% *1e-6; %[cm3s-1]
kc = 1.8e-11 * exp(110./T);
kd = 3.2e-11 * exp(70./T);
A1 =  0.079; %[s-1]  
A2 = 0.083 * ones(size(M)); %[s-1] O2(1sig) 
A4 = 6.81e-3 * ones(size(M)); %O(1D) lifetime A coefficient [s-1] 

prodO1D_O3 = 0.9 * Jhart .* O3;
prodO1D_O2 = (Jsrc + Jlya) .* O2;
prodO1D = prodO1D_O3 + prodO1D_O2;
lossO1D = kc .* N2 + kd .* O2 + A4; 
O1D = prodO1D./lossO1D; %[molecule/cm3]

% gA = gfactor(T,z,zenitangle,O2);
prodO21sig_O1D = 0.77*kd.*O2.*O1D;
prodO21sig_gA = gA .* O2;
lossO21sig = k2_N2 * N2 + k2_O2 * O2 + k2_O * O + A2;
O21sig_O1D = prodO21sig_O1D ./ lossO21sig; %[molecule/cm3]
O21sig_gA = prodO21sig_gA ./ lossO21sig;
%========Barth type reaction===================
O2star = k1 .* O .* O .* M; %O + O + M => Ostar + M
C_O = 19; % =33 when k2_O=0  (interpolated [O] with MSIS-83)
C_O2 = 6.6; %=7.5 when k2_O=0
Q = A2 + k2_O2 * O2 + k2_N2 * N2 + k2_O * O;
O21sig_barth =  O2star .* O2 ./ (Q .* (C_O * O + C_O2 * O2)); 
%============================================

O21sig = O21sig_O1D + O21sig_gA + O21sig_barth;
Vat = A1 * O21sig;

Vat_from_O3 = A1 * O21sig_O1D .* prodO1D_O3 ./ (prodO1D);
Vat_from_O2 = A1 * O21sig_O1D .* prodO1D_O2 ./ (prodO1D);
Vat_from_barth = A1 * O21sig_barth;
Vat_from_gA = A1 * O21sig_gA;


end