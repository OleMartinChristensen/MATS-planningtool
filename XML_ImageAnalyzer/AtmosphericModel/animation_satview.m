function animation_satview(filename, limb_radiance_t ,z , t, zenithangle, h_field, h_pix_num)

fig=figure('Visible','off','Position',[0 0 1100 680]);   
colormap parula
for nt = 1:length(t)
    subplot(1,5,[1,1.5])
    plot(limb_radiance_t(:,round(h_pix_num/2),nt), z(z<=110), 'k-','LineWidth',2)
    xlabel('[cm^{-3} s^{-1}]');
    ylabel('Tangent Altitude [km]');
    if abs(zenithangle) <= 100.6 
        xlim([0 20e7])
%         title(['Dayglow t = ',num2str(t(nt)),'s'],'FontSize',20)
    elseif abs(zenithangle) > 100.6
        xlim([0 15e5])
%         title(['Nightglow t = ',num2str(t(nt)),'s'],'FontSize',20)
    end
    set(gca,'color','none','FontSize',18)
    
    subplot(1,5,[3,5])
    imagesc(-h_field:h_field, z(z<=110), limb_radiance_t(:,:,nt))
    set(gca, 'YDir', 'normal')
    %     ylabel('Tangent altitude [km]')
    xlabel('Horizontal field of view [km]')
    colorbar('eastoutside');
    ylabel(colorbar,'Limb Radiance [cm^{-3} s^{-1}]');
%     hold on
%     plot(0*z(z<=110), z(z<=110), 'w-', 'LineWidth',3);
    set(gca,'color','none','FontSize',18)
    set(gcf,'color',[1 1 1])
    fig.InvertHardcopy = 'off';
    
    if abs(zenithangle) <= 100.6
        caxis([0 20e7])
        title(['Dayglow t = ',num2str(t(nt)),'s'],'FontSize',20)
    elseif abs(zenithangle) > 100.6
        caxis([0 15e5])
        title(['Nightglow t = ',num2str(t(nt)),'s'],'FontSize',20)
    end
    frame = getframe(fig);
    im = frame2im(frame);
    [imind,cm] = rgb2ind(im,256);
    if nt == 1
        imwrite(imind,cm,filename,'gif', 'Loopcount',inf,'DelayTime',0.2);
    else
        imwrite(imind,cm,filename,'gif','WriteMode','append','DelayTime',0.2);
    end
end
