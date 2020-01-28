function animation_airglow3D(filename, Vat_Pertur_t, x, y_t, z, t, zenithangle)
% filename = './Dayglow3D.gif';

fig=figure('Visible','off','Position',[0 0 560*2 700]);

for nt=1:length(t)
    subplot(1,5,[1,1.5])
    plot(reshape(Vat_Pertur_t((x==0),73,(z<=110),nt),[],1),z(z<=110), 'k-','LineWidth',2,'DisplayName','Perturbed VER');
    legend('hide');
    legend('boxoff')
    xlabel('VER [cm^{-3} s^{-1}]');
    ylabel('Altitude [km]');
    ylim([70 110])
    if abs(zenithangle) <= 100.6
        xlim([0 2.5e5])
%         title(['Dayglow t = ',num2str(t(nt)),'s'],'FontSize',20)
    else
        xlim([0 3000])
%         title(['Nightglow t = ',num2str(t(nt)),'s'],'FontSize',20)
    end
    set(gca,'color','none','FontSize',18)
    
    subplot(1,5,[3,5])
    colormap parula
    s = slice(y_t(nt,:), x, z(z<=110), Vat_Pertur_t(:,:,(z<=110),nt), min(y_t(nt,:)), min(x), 110);
    set(s,'EdgeColor','none')
    hold on
    plot3(min(y_t(nt,:))*ones(length(z(z<=110)),1), 0*z(z<=110), z(z<=110), 'w-','LineWidth',3)
    ylabel('x [km]')
    xlabel('y [km]')
    zlabel('Altitude [km]')
    xlim([y_t(1,1) y_t(end,end)])
    colorbar('eastoutside');
    ylabel(colorbar,'VER [cm^{-3} s^{-1}]');
    if abs(zenithangle) <= 100.6
        caxis([0 2.5e5])
        title(['Dayglow t =',num2str(t(nt)),'s'],'FontSize',20)
    else
        caxis([0 3000])
        title(['Nightglow t =',num2str(t(nt)),'s'],'FontSize',20)
    end
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
    
end
