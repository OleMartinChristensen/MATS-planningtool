%% Poster Plots
load limb_radiance_t0.mat
limb_0 = limb_radiance_t;
load limb_radiance_t30.mat
limb_30 = limb_radiance_t;
load limb_radiance_t60.mat
limb_60 = limb_radiance_t;
load limb_radiance_t90.mat
limb_90 = limb_radiance_t;

load Vat_Pertur0.mat
Vat_Pertur_0 = Vat_Pertur_t;
load Vat_Pertur30.mat
Vat_Pertur_30 = Vat_Pertur_t;
load Vat_Pertur60.mat
Vat_Pertur_60 = Vat_Pertur_t;
load Vat_Pertur90.mat
Vat_Pertur_90 = Vat_Pertur_t;

fig=figure('Visible','on','Position',[0 0 1000 550]);   
colormap parula
ax112 = subplot(4,20,[2,6,22,26]);
ax122 = subplot(4,20,[8,12,28,32]);
ax132 = subplot(4,20,[14,19.2,34,39.2]);

imagesc(ax112, -h_field:h_field, z(z<=110), limb_0)
caxis(ax112,[0 15e5])
title(ax112, '\xi = 0');
set(ax112,'YDir', 'normal','color','none','FontSize',18,'YTickLabels',{})

imagesc(ax122, -h_field:h_field, z(z<=110), limb_30)
caxis(ax122,[0 15e5])
xlabel(ax122,'Across track [km]')
title(ax122, '\xi = \pi/6');
set(ax122,'YDir', 'normal','color','none','FontSize',18,'YTickLabels',{})

imagesc(ax132, -h_field:h_field, z(z<=110), limb_90)
caxis(ax132,[0 15e5])
set(ax132,'YDir', 'normal','color','none','FontSize',18,'YTickLabels',{})
c = colorbar(ax132, 'eastoutside');
title(ax132, '\xi = \pi/2');
ylabel(c,'Limb Radiance [cm^{-3} s^{-1}]','FontSize',18);

ax111 = subplot(4,20,[1,1,21,21]);
ax121 = subplot(4,20,[7,7,27,27]);
ax131 = subplot(4,20,[13,13,33,33]);

plot(ax111,limb_0(:,14), z(z<=110), 'k-', 'LineWidth', 2)
xlim(ax111,[0 15e5])
ylabel(ax111,'Tangent altitude [km]','FontSize',18)
set(ax111, 'FontSize',18, 'XTickLabels',{})

plot(ax121,limb_30(:,14), z(z<=110), 'k-', 'LineWidth', 2)
xlim(ax121,[0 15e5])
set(ax121,'XTickLabels',{}, 'YTickLabels',{})

plot(ax131,limb_90(:,14), z(z<=110), 'k-', 'LineWidth', 2)
xlim(ax131,[0 15e5])
set(ax131,'XTickLabels',{}, 'YTickLabels',{})

ax21 = subplot(3,10,[21,23]);
contourf(ax21, y_t(1,:), z(z<=110), squeeze(Vat_Pertur_0(round(length(x)/2),...
    :,(z<=110),1))',30, 'EdgeColor','none');
caxis(ax21,[0 3000])
hold on
plot(ax21,yq,zq,'w-','LineWidth',3);
hold off
ylim(ax21,[70 110]);
ylabel(ax21,'Altitude [km]');
set(ax21, 'color','none','FontSize',18)

ax22 = subplot(3,10,[24,26]);
contourf(ax22, y_t(1,:), z(z<=110), squeeze(Vat_Pertur_30(round(length(x)/2),...
    :,(z<=110),1))',30, 'EdgeColor','none');
caxis(ax22,[0 3000])
hold on
plot(ax22,yq,zq,'w-','LineWidth',3);
hold off
ylim(ax22,[70 110]);
xlabel(ax22, 'Along track [km]');
set(ax22, 'color','none','FontSize',18, 'YTickLabels',{})

ax23 = subplot(3,10,[27,29.8]);
contourf(ax23, y_t(1,:), z(z<=110), squeeze(Vat_Pertur_90(round(length(x)/2),...
    :,(z<=110),1))',30, 'EdgeColor','none');
caxis(ax23, [0 3000])
hold on
plot(ax23, yq,zq,'w-','LineWidth',3);
hold off
ylim(ax23,[70 110]);
set(ax23, 'color','none','FontSize',18, 'YTickLabels',{})
c = colorbar(ax23,'eastoutside');
ylabel(c,'VER [cm^{-3} s^{-1}]','FontSize',18);

filename = 'posterSatview.png';
set(gcf,'color',[1 1 1])
fig.InvertHardcopy = 'off';
frame = getframe(fig);
im = frame2im(frame);
[imind,cm] = rgb2ind(im,256);
imwrite(imind,cm,filename,'png')

