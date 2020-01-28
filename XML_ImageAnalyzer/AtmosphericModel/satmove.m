function [Int_pic] = satmove(Vol_ch, x, y, z, ts, v_field, h_field, v_pix_num, h_pix_num, r_bot, r_top, r_tan, r_sat)
%x, y, z: atmospheric grid in km
%ts: time step
%v_field, h_field: field of view vertical/horizontal span in km
%v_pix_num, h_pix_num: number of pixels in the field of view 
%r_bot, r_tan, r_top, r_sat: distance from center of the earth to the
%bottom of atmosphere, tangent point, top of atmosphere and satellite in km

G = 6.673e-20; %km3/(s2*kg2)
Mearth = 5.98e24; %kg
R = 6370; %km earth radius
angular_speed = sqrt(G*Mearth/r_sat^3); %radians/s
theta = acos(r_tan/r_sat);
[y_rad_start, y_rad_end] = domain_start_and_end(r_bot, r_top, r_tan, r_sat, h_field);
Sat = [0, 0, r_sat]; % initial satellite location in ecef coordinate (u,v,w) 
inter_num = 300; %number of interval points along the LOS

%points on the FOV plane
Pu = linspace(-h_field, h_field, h_pix_num);
Pv = linspace((r_tan-v_field)*sin(theta), (r_tan+v_field)*sin(theta), v_pix_num);
Pw = linspace((r_tan-v_field)*cos(theta), (r_tan+v_field)*cos(theta), v_pix_num);

%point interval along the LOS
k_start = (r_sat*sin(theta) - r_top*sin(theta-y_rad_start))/(r_sat*sin(theta)); 
k_end = (r_sat*sin(theta) + r_top*sin(y_rad_end-theta))/(r_sat*sin(theta));
k = linspace(k_start, k_end, inter_num); 

%define all points along the LOS
lu = repmat(Sat(1) + k' * (Pu-Sat(1)), [1 1 v_pix_num]);
lv = repmat(reshape(Sat(2) + k' * (Pv-Sat(2)),[inter_num, 1, v_pix_num]), [1 h_pix_num 1]);
lw = repmat(reshape(Sat(3) + k' * (Pw-Sat(3)),[inter_num, 1, v_pix_num]), [1 h_pix_num 1]);

dlu = lu(2:end,:)-lu(1:end-1,:);
dlv = lv(2:end,:)-lv(1:end-1,:);
dlw = lw(2:end,:)-lw(1:end-1,:);
dl = sqrt((dlu).^2 + (dlv).^2 + (dlw).^2); 
dl(end+1,:) = dl(end,:); %pathlength in km

%=== change coordinate system of rays ecef to geodetic(u,v,w)->(alpha,beta,rho) ===
alpha = atan(lu(:,:) ./ lw(:,:));
beta = atan(lv(:,:) ./ lw(:,:));
rho = sqrt(lu(:,:).^2 + lv(:,:).^2 + lw(:,:).^2);

%=== Create coordinates of the query points(xq,yq,zq) === 
% for ts = 0:400:3600
xq = alpha .* r_tan;
yq = beta .* r_tan + ts * angular_speed * r_tan;
zq = rho - R * ones(size(rho));

Vq = interpn(x,y',z, Vol_ch, xq,yq,zq, 'nearest', 0);
V_int = sum(Vq.*dl,1);
Int_pic = (reshape(V_int, [length(Pu),length(Pw)]))';

end

