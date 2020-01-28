function Vat = nightglow(O, O2, N2, T)

M = O + O2 + N2;
k1 = 4.7e-33 * (300./T).^2;
k2_O2 = 4e-17;% *1e-6; %[cm3s-1]
k2_N2 = 2.2e-15;% *1e-6; %[cm3s-1]
k2_O = 8e-14;% *1e-6; %[cm3s-1]
A1 =  0.079; %[s-1]  HITRAN 1987 
A2 = 0.083 * ones(size(M)); %[s-1] O2(1sig) 
%========Barth type reaction===================
O2star = k1 .* O .* O .* M; %O + O + M => Ostar + M
C_O = 19; % =33 when k2_O=0  (interpolated [O] with MSIS-83)
C_O2 = 6.6; %=7.5 when k2_O=0
Q = A2 + k2_O2 * O2 + k2_N2 * N2 + k2_O * O;
O21sig_barth =  O2star .* O2 ./ (Q .* (C_O * O + C_O2 * O2)); 
%============================================

Vat = A1 * O21sig_barth;

end