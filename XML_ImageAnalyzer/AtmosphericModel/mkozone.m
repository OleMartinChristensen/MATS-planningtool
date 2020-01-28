%This version take 1D and output as 1D
function O3_v = mkozone(O_v, O2_v, N2_v, T_v, z, zenitangle)

ka = 6e-34 * exp(300./T_v).^2.3;
kb = 8e-12 * exp(-2060./T_v);
M_v = O2_v + N2_v;

load sigma.mat
pathl = pathleng(z, zenitangle) * 1e5;  %[km -> cm]
    
%iter 1
tau = (O_v*sO' + O2_v*sO2' + N2_v*sN2')' * pathl';
JO3 = sum(irrad.*sO3 * ones(1,length(z)) .* exp(-tau))';
O3_v_a = ka .* M_v .* O2_v .* O_v ./ (JO3 + kb.*O_v);
%iter 2
tau = (O_v*sO' + O2_v*sO2'+ O3_v_a*sO3' + N2_v*sN2')' * pathl';
JO3 = sum(irrad.*sO3 * ones(1,length(z)) .* exp(-tau))';
O3_v_b = ka .* M_v .* O2_v .* O_v ./ (JO3 + kb.*O_v);
%iter 3
tau = (O_v*sO' + O2_v*sO2'+ O3_v_b*sO3' + N2_v*sN2')' * pathl';
JO3 = sum(irrad.*sO3 * ones(1,length(z)) .* exp(-tau))';
O3_v = ka .* M_v .* O2_v .* O_v ./ (JO3 + kb.*O_v);
