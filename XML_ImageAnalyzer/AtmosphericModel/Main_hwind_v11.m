function limb_radiance = Main_hwind_v11(v_pix_num, h_pix_num, angle_xi, zenithangle, FullVFOV, FullHFOV)
% This version only generates data. 
%Slightly modified by David Skånberg to function as a function with inputs
%to be able to call this program to generate a scene of the limb radiance
%viewed. Removed time dependency and output animation to simplify the
%program.

%clear; close all;

%% set wave parameters
Period = 1;
omega = 2*pi/(3600 * Period);
l_z = -5; %vertical wavelength [km] (Negative sign?)
k_z = 2*pi / l_z; %vertical wavenumber [km-1] (=2*pi/wavelength[km])
k_hor = DR(omega, k_z); %horizontal wavenumber [km-1]
l_hor = 2*pi / k_hor; %horizontal wavelength [km]
%zenithangle = 110;
%zenithangle = 90;
%angle_xi = 0; %choose angle of horizontal direction
k_x = k_hor * cos(deg2rad(angle_xi));
k_y = k_hor * sin(deg2rad(angle_xi));
A = 1; %reduced amplitude [km*s2]
cp_x = omega/k_x; %phase velocity in x direction [km/s]


%disp('========Generating waves=======')
%disp(['Period is ', num2str(Period),'hour(s)']);
%disp(['Vertical wavelength is ', num2str(l_z),'km']);
%disp(['Horizontal wavelength is ', num2str(l_hor),'km']);
%disp(['Reduced amplitude is ', num2str(A),'km*s2']);
%disp(['Horizontal angle is ', num2str(angle_xi)]);

tic

G = 6.673e-20; %km3/(s2*kg2)
Mearth = 5.98e24; %kg
R = 6370; %km earth radius
r_tan = R + 92.5;
r_sat = R + 600; %altitude of the satellite orbit[km]
r_bot = R + 50;
r_top = R + 150;

theta = acos(r_tan/r_sat);
r_sat2tan = sin(theta)*r_sat;
VFOV = FullVFOV/2;
HFOV = FullHFOV/2;

v_field = tan(VFOV)*r_sat2tan; %vertical field of view [km]
h_field = tan(HFOV)*r_sat2tan; %horizontal field of view [km]

%v_field = 20; %vertical field of view [km]
%h_field = 130; %horizontal field of view [km]
%v_pix_num = 81;
%h_pix_num = 27;
angular_speed = sqrt(G * Mearth / r_sat^3); %radians/s
[y_rad_start, y_rad_end, x_rad] = domain_start_and_end(r_bot, r_top, ...
    r_tan, r_sat, h_field);

%% set atmosphere grid size
x = linspace(-x_rad*r_tan, x_rad*r_tan,101); %km
z = r_bot-R : 0.5 : r_top-R; %km must be the same size/interval as temperature profile from msis
t = linspace(0,1,1);
% t = 240;

%% set input profiles
load msisdata.mat
month = 7;
lat = 10;
T = interp1(zMsis,TMsis(:,month,lat), z');
M = interp1(zMsis,NMsis(:,month,lat), z');
O2 = 0.2 * M;
N2 = 0.8 * M;
const = A .* sqrt(NMsis(1,month,lat)); %for calculating wave amplitutde

%%%%%%%%%%%%%%%%sythetic horizontal wind profile!!!!!
u = linspace(-50, 50, length(z));
u_x = cos(angle_xi) * u;
u_y = sin(angle_xi) * u;
[~, ~, uu_x] = ndgrid(x,1:145,u_x);
[~, ~, uu_y] = ndgrid(x,1:145,u_y);

%%%%%%%%%%%%%%%%sythetic horizontal wind profile!!!!!!

%% Parameters for [O] profile
OMax = 3e11; %oxygen peak concentration [molecule/cm3]
S = 0.8; %scale factor
H = 5.38; %scale height [km]
zmax = 98; % peak concentration height [km]
O = OxyShape(z, OMax, S, H, zmax)'; %[molecule/cm3]
% clear OMax S H zmax latMsis monthMsis NMsis TMsis zMsis lat month
% clear prompt k_hor Period l_hor l_z

%% Vectorise
y_length = 145;

[~, ~, Temp_Mean] = ndgrid(x,1:y_length,T);
[~, ~, O_Mean] = ndgrid(x,1:y_length,O);
[~, ~, M_Mean] = ndgrid(x,1:y_length,M);
O2_Mean = 0.2 * M_Mean;
N2_Mean = 0.8 * M_Mean;

%% Calculate Ozone in day and photolysis rates
if abs(zenithangle) <= 100.6
    O(z<86) = O(z==86);
    O3 = mkozone(O, O2, N2, T, z, zenithangle);
    [Jhart,Jsrc,Jlya,JO3,~] = Jfactors(O, O2, O3, N2, zenithangle, z);
    gA = gfactor(O2, T, zenithangle, z);
    [~, ~, Jhart] = ndgrid(x,1:y_length,Jhart);
    [~, ~, Jsrc] = ndgrid(x,1:y_length,Jsrc);
    [~, ~, Jlya] = ndgrid(x,1:y_length,Jlya);
    [~, ~, JO3] = ndgrid(x,1:y_length,JO3);
    [~, ~, gA] = ndgrid(x,1:y_length,gA);
end


%% Loop over t
%Vat_Pertur_t = zeros(length(x),y_length,length(z),length(t));
%limb_radiance_t = zeros(v_pix_num,h_pix_num,length(t));
%y_t = zeros(length(t),y_length);
%Temp_Pertur_t = zeros(length(x), length(z), length(t)); 
%zs_index_t = zeros(length(x), length(t));

for nt = 1:length(t)
    y_plus = t(nt) * angular_speed * r_tan;
    y = linspace(y_plus + y_rad_start*r_tan, y_plus + y_rad_end*r_tan,y_length);
    
    [hor_x, hor_y, alt] = ndgrid(x,y,z);
    
    %% Gravity wave model
    [Temp_Pertur, M_s, zs_index] = TempPertur(Temp_Mean, ...
        t(nt), hor_x, hor_y, alt, omega, k_x, k_y, k_z, const, M_Mean, uu_x, uu_y);
    Aw = const ./ sqrt(M_s); % wave amplitude
    O_Pertur = MinorPertur(O_Mean, t(nt), hor_x, hor_y, alt, ...
        omega, k_x, k_y, k_z, Aw, uu_x, uu_y);
    M_Pertur = DensPertur(M_Mean, t(nt), hor_x, hor_y, alt, ...
        omega, k_x, k_y, k_z, Aw, uu_x, uu_y);
    O2_Pertur = DensPertur(O2_Mean, t(nt), hor_x, hor_y, alt, ...
        omega, k_x, k_y, k_z, Aw, uu_x, uu_y);
    N2_Pertur = DensPertur(N2_Mean, t(nt), hor_x, hor_y, alt, ...
        omega, k_x, k_y, k_z, Aw, uu_x, uu_y);
    % [vel_x, vel_y] = VelocityHor(tim, hor_x, hor_y, alt, ...
    %     omega, k_x, k_y, k_z, Aw); % m/s
    % vel_z = VelocityVer(tim, hor_x, hor_y, alt, omega, k_x, k_y, k_z, Aw); % m/s
    % clear k_x k_y k_z omega A const tim hor_x hor_y alt const
    % clear O_Mean O2_Mean N2_Mean
    
    % vel_sqr = vel_x.^2 + vel_y.^2 + vel_z.^2; % v^2 [m2/s2]
    % Ek_Pertur = 0.5 * (M_Pertur*1e6) .* vel_sqr; % kinetic energy density[m-1s-2]
    % Ek_Mean = mean(mean(mean(Ek_Pertur,1),2),4);
    
    %% Airglow model
    if abs(zenithangle) <= 100.6
        disp(['Calculating dayglow, t=' num2str(t(nt)) 's'])
        ka = 6e-34 * exp(300./Temp_Pertur).^2.3;
        kb = 8e-12 * exp(-2060./Temp_Pertur);
        O3_Pertur = ka .* M_Pertur .* O2_Pertur .* O_Pertur ./ (JO3 + kb.*O_Pertur);
        
        Vat_Pertur = dayglow(O_Pertur, O2_Pertur, O3_Pertur, N2_Pertur, Temp_Pertur,...
            Jhart, Jsrc, Jlya, gA);
        [Vat, Vat_from_O3, Vat_from_O2, Vat_from_barth, Vat_from_gA] ...
            = dayglow(O, O2, O3, N2, T, reshape(Jhart(1,1,:,1),[],1), ...
            reshape(Jsrc(1,1,:,1),[],1), reshape(Jlya(1,1,:,1),[],1), ...
            reshape(gA(1,1,:,1),[],1));
        %[~, ~, Vat_Mean] = ndgrid(x,y,Vat);
        clear ka kb gA Jhart Jlya Jsrc JO3 JO2
        
    elseif abs(zenithangle) > 100.6
        %disp(['Calculating nightglow, t=' num2str(t(nt)) 's'])
        Vat_Pertur = nightglow(O_Pertur, O2_Pertur, N2_Pertur, Temp_Pertur);
        Vat = nightglow(O, O2, N2, T);
        %[~, ~, Vat_Mean] = ndgrid(x,y,Vat);
    end
    
    %Vat_Pertur_t(:,:,:,nt) = Vat_Pertur;
    %y_t(nt,:) = y;
    %Temp_Pertur_t(:,:,nt) = squeeze(Temp_Pertur(:,1,:));
    %zs_index_t(:,nt) = zs_index(:,1);
    
    %% HITRAN model
    %[Vat_ch1,Vat_ch2,ratio_ch] = AbandHitran(Vat_Pertur, Temp_Pertur);
    %[V_Mean_ch1,V_Mean_ch2] = AbandHitran(Vat_Mean, Temp_Mean);
    %ratio_Vat = Vat_ch1./Vat_ch2;
 
    %% Limb radiance
    limb_radiance = satmove(Vat_Pertur, x, y, z, t(nt),...
        v_field, h_field, v_pix_num, h_pix_num, r_bot, r_top, r_tan, r_sat);
    %limb_radiance_Mean = satmove(Vat_Mean, x, y, z, t(nt),...
    %    v_field, h_field, v_pix_num, h_pix_num, r_bot, r_top, r_tan, r_sat);

    %limb_radiance_t(:,:,nt) = limb_radiance; 
   
end

% clear OMax S H zmax latMsis monthMsis NMsis TMsis zMsis lat month
% clear prompt k_hor Period l_hor l_z 
% clear A const tim hor_x hor_y alt const Aw M_s
% clear O_Mean O2_Mean N2_Mean
% clear Mearth G 
% clear M M_Mean M_Pertur N2 N2_Pertur O O_Pertur O2 O2_Pertur T Temp_Mean Temp_Pertur
% clear r_bot r_top rad_end rad_start y_plus angular_speed
% clear nt limb_radiance Vat_Pertur

% %% Save data
% disp('Saving Data...')
% filename = ['Vat_Pertur', num2str(angle_xi),'.mat'];
% save(filename, 'Vat_Pertur_t', 'x', 'y_t', 'z', 't', '-v7.3')
% filename = ['limb_radiance_t', num2str(angle_xi),'.mat'];
% save(filename, 'limb_radiance_t', 't', 'v_field', 'h_field', 'r_bot', ...
%     'r_top', 'r_tan', 'r_sat');
% 
% %% Line of sight 2D slide
% disp('Ploting line of sight....')
% filename = ['los',num2str(angle_xi), '.png'];
% [yq,zq] = los_2d(filename, Vat_Pertur_t, x, y_t, z, t, ...
%     v_field, h_field, r_bot, r_top, r_tan, r_sat);

% filename = ['limbview_1d_los',num2str(angle_xi),'.png'];
% animation_1d_satview_los(filename, Vat_Pertur_t, limb_radiance_t,...
%     limb_radiance_Mean, x, y_t, z, t, zenithangle, h_field, yq, zq)

% filename = ['limbview_los',num2str(angle_xi),'.png'];
% animation_satview_los(filename, Vat_Pertur_t, limb_radiance_t,...
%     x, y_t, z, t, zenithangle, h_field, yq, zq)


%% Plotting outcommented by David Skånberg as XML_ImageAnalyzer is only intereste in the generated array
%% Limb view 1D and 2D plots
%disp('Ploting satellite images...')
%filename = ['./limbimage_hwind'...
%    num2str(angle_xi) '.gif'];
%animation_satview(filename,limb_radiance_t,z,t,zenithangle, h_field, h_pix_num);

%% Airglow 1D and 3D Plots
%disp('Ploting airglow animations...')
%filename = ['./Nightglow3D_hwind'...
%    num2str(angle_xi) '.gif'];
%animation_airglow3D(filename, Vat_Pertur_t, x, y_t, z, t,zenithangle);

%% Temperture field 2D Plots
%disp('Ploting temperture animations...')
%filename = './Temperture_hwind.gif';
%animation_temp2D(filename, Temp_Pertur_t, x, z, t, zs_index_t);
%% Time series
% figure; 
% subplot 121
% imagesc(-h_field:h_field, z, squeeze(Vat_Pertur_t(:,146/2,:,1))'); 
% set(gca,'YDir','normal')
% xlabel('Distance [km]')
% title('Spacial snapshot')
% ylim([r_tan-R-v_field r_tan-R+v_field])
% 
% subplot 122
% imagesc(t, z, squeeze(Vat_Pertur_t(102/2,146/2,:,:))); 
% xlabel('Time [s]')
% title('Time ser')
% set(gca,'YDir','normal')
% ylim([r_tan-R-v_field r_tan-R+v_field])
% saveas(gcf,['Timeseries' num2str(angle_xi) '4.png']) 

% figure;semilogx(Vat_from_barth,z, Vat_from_gA,z, Vat_from_O2,z, Vat_from_O3,z)
% legend('barth','gA','O2','O3')
% xlim([1e2 1e6])
% ylim([70 110])


end
