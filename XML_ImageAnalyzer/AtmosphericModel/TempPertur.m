%% Perturbed temperature in [K] and critical altitudes [index]
%temp: temperature [K]
%t: time [s]
%x,y: hosrizontal distance [km]
%z: altitude [km]
%omega: wave frequency [s-1]
%k_y, k_z: horizontal and vertical wavenumber [km-1]
%A: reduced amplitude [km*s2]
%M: density field [cm-3]
%M_s: density field for wave amplitutde calculation

function [Tp, M_s, z_saturated] = TempPertur(T, t, x, y, z, omega, k_x, k_y, k_z, const, M, u_x, u_y)
% ==== constants ====
g = 9.8e-3; %gravitational acceleration [km/s2]
gamma = 1.4; %ratio of specific heats (c_p/c_v)
C = 340.29e-3; %speed of sound [km/s]
% ===================

theta = -(omega + u_x*k_x + u_y*k_y) * t + k_x * x + k_y * y + k_z * z;
k_hor = sqrt(k_x^2 + k_y^2);

% const = A .* sqrt(2.5e+19); %sqrt(M(z=0))) density Prof must be in unit [cm-3]
E2 = const ./ sqrt(M);
C1 = omega^2 * k_z;
C2 = g * (gamma * omega^2 / C^2 - k_hor^2);

T_dash = T .* E2 .* (gamma-1) .* (C1 .* cos(theta) + C2 * sin(theta));
T_dash(M == 0) = 0; % because of [k./sqrt(density)]
Tp = T + T_dash;

dT_dz = diff(Tp,1,3)./diff(z,1,3);
dT_dz(:,:,end+1,:) = dT_dz(:,:,end,:);
ELR = -dT_dz;
z_saturated = zeros(size(x,1),size(y,2),1,size(t,4));
for n_x = 1:size(x,1)
    for n_y = 1:size(y,2)
        for n_t = 1:size(t,4)
           z_s = find(ELR(n_x,n_y,:,n_t)>=10,1); %critical altitude (index) as a scalar
           if isempty(z_s) == 1
               z_s = size(z,3);
           end
           z_saturated(n_x,n_y,1,n_t) = z_s; %critical altitude (index) as a matrix
           M(n_x,n_y,z_s:end,n_t) = M(n_x,n_y,z_s,n_t); 
        end
    end
end
M_s = M;
E2 = const ./ sqrt(M_s);
T_dash = T .* E2 .* (gamma-1) .* (C1 .* cos(theta) - C2 * sin(theta));
T_dash(M == 0) = 0; % because of [k./sqrt(density)]
Tp = T + T_dash;


end
