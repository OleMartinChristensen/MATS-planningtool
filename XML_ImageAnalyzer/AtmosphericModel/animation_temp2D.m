function animation_temp2D(filename, Temp_Pertur_t, x, z, t, zs_index_t)

fig = figure;
for nt = 1:length(t)
    subplot(1,5,[1,1.5])
    plot(Temp_Pertur_t(round(length(x)/2),:,nt), z, 'k-','LineWidth',2)
    xlabel('[K]');
    ylabel('Altitude [km]');
    text(Temp_Pertur_t(round(length(x)/2),...
        zs_index_t(round(length(x)/2), nt), nt) +3, ...
        z(zs_index_t(round(length(x)/2),nt)), ...
        '\leftarrow Saturated altitude','FontSize',18)
    set(gca,'color','none','FontSize',18)
    
    
    subplot(1,5,[3,5])
    contourf(x, z', Temp_Pertur_t(:,:,nt)',30,'EdgeColor','none');
    hold on
    plot([0 0], [min(z) max(z)], 'w-', 'LineWidth',3)
    xlabel('Accross track [km]');
    ylabel('Altitude [km]');
    colorbar('eastoutside');
    ylabel(colorbar, '[K]');
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
    