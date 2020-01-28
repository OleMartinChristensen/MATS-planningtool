function [yq, zq] = los_2d(filename, Vat_Pertur_t, x, y_t, z, t, v_field, h_field,...
    r_bot, r_top, r_tan, r_sat)

G = 6.673e-20; %km3/(s2*kg2)
Mearth = 5.98e24; %kg
R = 6370; %km earth radius
angular_speed = sqrt(G*Mearth/r_sat^3); %radians/s
theta = acos(r_tan/r_sat);
[y_rad_start, y_rad_end] = domain_start_and_end(r_bot, r_top, r_tan, r_sat, h_field);
Sat = [0, 0, r_sat]; % initial satellite location (u,v,w) 
inter_num = 300;

Pv = linspace((r_tan-v_field)*sin(theta), (r_tan+v_field)*sin(theta), 5);
Pw = linspace((r_tan-v_field)*cos(theta), (r_tan+v_field)*cos(theta), 5);

k_start = (r_sat*sin(theta) - r_top*sin(theta-y_rad_start))/(r_sat*sin(theta)); 
k_end = (r_sat*sin(theta) + r_top*sin(y_rad_end-theta))/(r_sat*sin(theta));
k = linspace(k_start, k_end, inter_num); %interval points along the ray

lv = Sat(2) + k' * (Pv-Sat(2));
lw = Sat(3) + k' * (Pw-Sat(3));

%=== change coordinate system of rays(x,y,z)->(alpha,beta,rho) ===
beta = atan(lv(:,:) ./ lw(:,:));
rho = sqrt(lv(:,:).^2 + lw(:,:).^2);


%=== Create coordinates of the query points(xq,yq,zq) === 
nt = 1;
yq = beta .* r_tan + t(nt) * angular_speed * r_tan;
zq = rho - R * ones(size(rho));

%=== start ploting
fig = figure('Visible', 'off', 'Position',[0 0 1500 400], 'OuterPosition', [0 0 1500 420]);
colormap parula

contourf(y_t(nt,:), z(z<=110), squeeze(Vat_Pertur_t(round(length(x)/2),:,(z<=110),nt))',30, 'EdgeColor','none');
colorbar('eastoutside');
% xlim([y_t(1) y_t(end)]);
ylim([70 110]);
% title(['t = ', num2str(t(nt)), 's'],'FontSize',14)
ylabel('Altitude [km]');
xlabel('Along track distance [km]');
ylabel(colorbar,'VER [photons cm^{-3} s^{-1}]');

hold on
plot(yq,zq,'w-','LineWidth',3);
plot([theta*r_tan theta*r_tan], [70 110], 'k-', 'LineWidth', 3);

set(gca,'color','none','FontSize',18)
set(gcf,'color',[1 1 1])

fig.InvertHardcopy = 'off';
frame = getframe(fig);
im = frame2im(frame);
[imind,cm] = rgb2ind(im,256);
if nt == 1
    imwrite(imind,cm,filename,'gif', 'Loopcount',inf,'DelayTime',0.2);
else
    imwrite(imind,cm,filename,'gif','WriteMode','append','DelayTime',0.2);
end