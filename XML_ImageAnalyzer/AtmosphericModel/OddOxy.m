clear;close all;

z = 70:.5:150;
load msisdata.mat
month = 7;
lat = 10;
T = interp1(zMsis,TMsis(:,month,lat), z');
M = interp1(zMsis,NMsis(:,month,lat), z');
O2 = 0.2 * M;
N2 = 0.8 * M;
OMax = 3e11; %oxygen peak concentration [molecule/cm3]
S = 0.8; %scale factor
H = 5.38; %scale height [km]
zmax = 98; % peak concentration height [km]
O = OxyShape(z, OMax, S, H, zmax)'; %[molecule/cm3]
fig=figure('Name','Odd Oxygen');
semilogx(O,z, 'b--','LineWidth',4);
hold on
O(z<86) = O(z==86);
semilogx(O,z, 'b:','LineWidth',4);
O3 = mkozone(O, O2, N2, T, z, 60);
semilogx(O3,z,'k-','LineWidth',4);
xlabel('Concentration [cm-3]','FontSize',18);
ylabel('Altitude [km]','FontSize',18);
title('Odd Oxygen','FontSize',20);
lgd=legend('[O] Night','[O] Day', '[O_3] Day', 'Location','southeast');
% lgd.FontSize=18;
lgd.Box='on';
ylim([70 110])
xlim([1e6 1e12])
set(gca,'color','none','FontSize',18)
set(gcf,'color',[1 1 1])
fig.InvertHardcopy = 'off';
saveas(gcf, '/home/anqil/Documents/reportFigure/OddOxy.png')


