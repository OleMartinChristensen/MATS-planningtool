function gA = gfactor(O2, T, zenitangle, z)

load alines.dat
niu0=alines(:,1);
Sj=alines(:,2);
Al=alines(:,3);
Elow=alines(:,4);
K = 1.3807e-23; %Boltzmann constant [m2kgs-2K-1]
C = 299792458; %speed of light [m/s]
AMU = 1.66e-27; %atomic mass unit [kg]

AD = niu0/C *sqrt(2*log(2)*K*298/32/AMU); 
niu = 12900:0.01:13170; %frequency interval
sigma = zeros(length(z),length(niu));

for zi=1:length(z)
	
	Sjlayer=Sj*298/T(zi).*exp(1.439*Elow*(T(zi)-298)/298/T(zi));
	ADlayer=AD*sqrt(T(zi)/298);
	
    for freqi=1:length(niu0)
		sigma(zi,:) = sigma(zi,:) + Sjlayer(freqi)*doppler(ADlayer(freqi),niu-niu0(freqi));
    end
end
path = pathleng(z,zenitangle);
tau = ((O2*ones(1,size(sigma,2))).*sigma)'*path'*1e5;
gA = sum((2.742e13*sigma'.*exp(-tau)))./size(niu0,1);
gA(tau(1,:)==0) = 0;
% [~,~,gA,~] = ndgrid(x,y,gA,t);

end