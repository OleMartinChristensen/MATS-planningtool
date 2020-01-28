%% Dispersion relation 
function k_y = DR(omega, k_z)

g = 9.8e-3; %gravitational acceleration [km/s2]
C = 340.29e-3; %speed of sound [km/s]
gamma = 1.4; %ratio of specific heats (c_p/c_v)

C1 = omega^4 * ones(size(k_z));
C2 = omega^2*C^2 * k_z.^2;
C3 = gamma^2*g^2*omega^2/4/C^2 * ones(size(k_z));
C4 = (1-gamma)*g^2 + omega^2*C^2;
k_y = sqrt((C1 - C2 - C3) ./ C4);
end