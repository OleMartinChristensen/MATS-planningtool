function animation_1d_satview_los(filename, Vat_Pertur_t, limb_radiance_t,...
    limb_radiance_Mean, x, y_t, z, t, zenithangle, h_field, yq, zq)

fig=figure('Visible','off','Position',[0 0 1100 1100]);   
colormap parula
ax1 = subplot(3,10,[1,3,11,13]);
ax2 = subplot(3,10,[4,10,14,20]);
ax3 = subplot(3,10,[21,30]);

for nt = 1:length(t)
    subplot(ax1)
    plot(limb_radiance_t(:,14,nt), z(z<=110), 'k-', 'LineWidth', 2)
    hold on
    plot(limb_radiance_Mean(:,14), z(z<=110), 'b:', 'LineWidth', 2)
    xlabel('[cm^{-3} s^{-1}]');
    ylabel('Tangent Altitude [km]');
    if abs(zenithangle) <= 100.6
        xlim([0 20e7])
        %         title(['Dayglow t = ',num2str(t(nt)),'s'],'FontSize',20)
    else
        xlim([0 15e5])
        %         title(['Nightglow t = ',num2str(t(nt)),'s'],'FontSize',20)
    end
    set(gca,'color','none','FontSize',18)
    
    subplot(ax2)
    imagesc(-h_field:h_field, z(z<=110), limb_radiance_t(:,:,nt))
    set(gca, 'YDir', 'normal')
    xlabel('Across track distance [km]')
    colorbar('eastoutside');
    ylabel(colorbar,'Limb Radiance [cm^{-3} s^{-1}]');
    hold on
    plot(0*z(z<=110), z(z<=110), 'w-', 'LineWidth',3);
    hold off
    set(gca,'color','none','FontSize',18, 'YTickLabels',{})
    if abs(zenithangle) <= 100.6
        caxis([0 20e7])
%         title(['Dayglow t = ',num2str(t(nt)),'s'], 'FontSize',20)
    else
        caxis([0 15e5])
%         title(['Nightglow t = ',num2str(t(nt)),'s'], 'FontSize',20)
    end
    
    subplot(ax3)
    contourf(y_t(1,:), z(z<=110), squeeze(Vat_Pertur_t(round(length(x)/2),:,(z<=110),1))',30, 'EdgeColor','none');
    colorbar('eastoutside');
    ylim([70 110]);
%     title(['t = ', num2str(t(1)), 's'],'FontSize',20)
    ylabel('Altitude [km]');
    xlabel('Along track distance [km]');
    ylabel(colorbar,'VER [photons cm^{-3} s^{-1}]');
    
    hold on
    plot(yq,zq,'w-','LineWidth',3);
    % plot([theta*r_tan theta*r_tan], [70 110], 'k-', 'LineWidth', 3);
    hold off
    set(gca,'color','none','FontSize',18)
    if abs(zenithangle) <= 100.6
        caxis([0 2.5e5])
    else
        caxis([0 3000])
    end

    set(gcf,'color',[1 1 1])
    fig.InvertHardcopy = 'off';
    frame = getframe(fig);
    im = frame2im(frame);
    [imind,cm] = rgb2ind(im,256);
%     if nt == 1
%         imwrite(imind,cm,filename,'gif', 'Loopcount',inf,'DelayTime',0.2);
%     else
%         imwrite(imind,cm,filename,'gif','WriteMode','append','DelayTime',0.2);
%     end

    imwrite(imind,cm,filename,'png')
end



end
