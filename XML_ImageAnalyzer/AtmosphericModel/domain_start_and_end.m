function [y_rad_start, y_rad_end, x_rad] = domain_start_and_end(r_bot, ...
    r_top, r_tan, r_sat, h_field)
%calculates the minimum horizontal span of the atmospheric grid in radius  
d = sqrt(r_sat^2 - r_tan^2);
theta_1 = atan(d/(r_tan-r_bot));
theta_2 = asin(r_bot/r_top*sin(theta_1));
theta_3 = pi - theta_1;
theta = acos(r_tan/r_sat);

beta = pi - theta_2 - theta_3;
alpha = theta - beta;
gamma = pi - theta_1- theta_2;

y_rad_start = alpha;
y_rad_end = theta + gamma;

a = h_field^2 + d^2 + (r_bot - r_tan)^2;
b = 2*r_tan*(r_bot - r_tan) - 2*d^2;
c = d^2 + r_tan^2 - r_top^2;
k = -b/2/a + sqrt(b^2 - 4*a*c)/2/a;
x_rad = atan(k*h_field/(r_tan + k*(r_bot-r_tan)));



