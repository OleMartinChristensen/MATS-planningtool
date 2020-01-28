%% Minor gas Density perturbation
%density: bulk density[molecule/cm3]
%t: time [s]
%x,y: hosrizontal distance [km]
%z: altitude [km]
%temp: vertical (or horizontal) temperature profile [K]
%omega: wave frequency [s-1]
%k_y, k_z: horizontal and vertical wavenumber [km-1]
%A: reduced amplitude [km*s2]
%Aw: wave amplitude

function nXp = MinorPertur(nX, t, x, y, z, omega, k_x, k_y, k_z, Aw, u_x, u_y)

% ==== constants ====
g = 9.8e-3; %gravitational acceleration [km/s2]
gamma = 1.4; %ratio of specific heats (c_p/c_v)
C = 340.29e-3; %speed of sound [km/s]
H = 5.38 * ones(size(z)); %Scale hight [km]
% ===================
theta = -(omega + u_x*k_x + u_y*k_y) * t + k_x * x + k_y * y + k_z * z; 
k_hor = sqrt(k_x^2 + k_y^2);

ddensity_dz = diff(nX,1,3)./diff(z,1,3);
ddensity_dz(:,:,end+1,:) = ddensity_dz(:,:,end,:);
E1 = ddensity_dz./ nX;
C1 = omega^2 * k_z;
C2 = (1 - gamma/2) .* k_hor^2 .* g;
C3 = omega^2 - k_hor^2 * C.^2;

nX_dash = nX .* Aw .* (C1 * cos(theta) - (C2 - C3 * (E1 + 1./(2*H))).*sin(theta));
nX_dash(nX == 0) = 0; 

nXp = nX + nX_dash;
end