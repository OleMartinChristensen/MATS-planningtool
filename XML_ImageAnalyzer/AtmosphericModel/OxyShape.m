%% plot [O] profile
function M_O = OxyShape(z, M_Omax, S, H, zmax)
zm = zmax * ones(size(z)); % peak concentration height [km]

M_O = M_Omax * exp(0.5 * (1 - (z-zm)./(S*H) - exp((zm-z)./(S*H))));
end