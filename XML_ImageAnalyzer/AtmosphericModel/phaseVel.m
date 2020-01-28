

Period = 1;
omega = 2*pi/(3600 * Period);
l_z = 5; %vertical wavelength [km] (Negative sign?)
k_z = 2*pi / l_z; %vertical wavenumber [km-1] (=2*pi/wavelength[km])
k_hor = DR(omega, k_z); %horizontal wavenumber [km-1]
l_hor = 2*pi / k_hor; %horizontal wavelength [km]
angle_xi = 0:90; %choose angle of horizontal direction
k_x = k_hor * cos(deg2rad(angle_xi));
k_y = k_hor * sin(deg2rad(angle_xi));
vp_x = omega./k_x; %phase velocity in x direction [km/s]
l_x = 2*pi ./ k_x;
l_y = 2*pi ./ k_y;

figure;
plot(angle_xi, vp_x)
xlabel('angle \xi')
ylabel('Phase velocity [km/s]')