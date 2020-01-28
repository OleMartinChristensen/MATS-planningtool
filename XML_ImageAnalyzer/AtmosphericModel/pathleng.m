function [pathlength, columnpathl]= pathleng(heights, Xi)

%computes the pathlengths through atmospheric layers for rays 
%incident on the layer given by the row index passing through the layers
%given by the column index for a solar zenith angle of xi. 
%It also considers geometrical shading by the earth when zenitangles>90. 

[m,n]=size(heights);
if n<m 
        heights=heights';
end

length_heights = length(heights);
deltaz=heights(2:length_heights)-heights(1:length_heights-1);
deltaz=[deltaz deltaz(length(deltaz))];
heights=[heights max(heights)+deltaz(length(deltaz))];

nheights = length(heights);
Re=6370; % km Earth radius
d2r=pi/180;

if Xi==90
	Zt=heights;
else
	Zt=(Re+heights)*sin(Xi*d2r)-Re;
end

pathl=zeros(nheights);

for j=1:nheights
        h=heights(j:nheights); 
        Ztj=Zt(j);
        pathl(j,j:nheights) = sqrt(h.*h+2*Re*(h-Ztj)-Ztj*Ztj);
end

pathl(:,1:nheights-1) = pathl(:,2:nheights) - pathl(:,1:nheights-1);
pathl=pathl(1:nheights-1,1:nheights-1);
pathl=triu(pathl);

pathlength = pathl;

heights=heights(1:(length(heights)-1));
nheights=nheights-1;

if (Xi>90)
    
    for j=1:nheights
        if Zt(j)>0
            
            I=find(heights<heights(j) & heights>Zt(j));
            
            if ((isempty(I)))
                I=max(1,j-1);
                
            else
                I=[max(I(1)-1,1) I];
            end
            
            h=heights(I)+deltaz(I);
            Ztj=Zt(j);
            pathl(j,I) = sqrt(h.*h+2*Re*(h-Ztj)-Ztj*Ztj);
            
            if (isempty(find(I==1, 1)))
                pathl(j,I)=...
                    (pathl(j,I)-pathl(j,max(I-1,1)));
            else
                J=I(I~=1);
                pathl(j,J)=...
                    (pathl(j,J)-pathl(j,max(J-1,1)));
            end
            
        elseif Zt(j)<=0
            pathl(j,:) = zeros(size(pathl(j,:)));
            
        end
    end
    
    pathl1=fliplr(pathl);
    nanregion=find(isnan(pathl)==1);
    pathl2=(triu((pathl'),1))';
    pathl2(nanregion')=zeros(size(nanregion'));
    
    pathlength=pathl+pathl2;
    columnpathl=[pathl1 pathl2];
end

