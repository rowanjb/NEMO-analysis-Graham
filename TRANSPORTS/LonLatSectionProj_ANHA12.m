close all force
clear all
clear all
%clearvars -global *

% global variables
%global navLon navLat lonLog latLog NX NY secName CF meshhgr meshzgr maskfile isClosePoly

CF='ANHA12';

switch CF
   case {'ANHA4'}
     maskfile='/mnt/storage0/xhu/ANHA4-I/ANHA4_mask.nc';
     meshhgr='/mnt/storage0/xhu/ANHA4-I/ANHA4_mesh_hgr.nc';
     meshzgr='/mnt/storage0/xhu/ANHA4-I/ANHA4_mesh_zgr.nc';
   case {'ANHA12'}
     maskfile='/mnt/storage1/xhu/ANHA12-I/new_bathymetry/ANHA12_mask.nc';
     meshhgr='/mnt/storage1/xhu/ANHA12-I/new_bathymetry/ANHA12_mesh_hgr.nc';
     meshzgr='/mnt/storage1/xhu/ANHA12-I/new_bathymetry/ANHA12_mesh_zgr.nc';
   otherwise
     disp(['Not ready for CF=',CF])
     return
end

lonLog=[]; latLog=[];
navLon=GetNcVar(meshhgr,'glamf'); navLat=GetNcVar(meshhgr,'gphif');
[NY,NX]=size(navLon);

% load surface mask file
tmask=squeeze(GetNcVar(maskfile,'fmask')); tmask=squeeze(tmask(1,:,:));

isClosePoly=0;
%secName='Fram1';
%lonLog=[2 12];
%latLog=[78 78];
m_proj('stereographic','lat',90,'long',0,'radius',25);
%secName='Fram2';
%lon=[0.03307 0.02228]; %[x1,x2]
%lat=[-0.1736 -0.1688]; %[y1,y2]
%[lonLog,latLog]=m_xy2ll(lon,lat);
%secName='OSNAP';
%lonLog=[-57.0 -52.0996 -49.7806 -47.5645 -45.7209 -45.0];
%latLog=[52.0 52.6653 53.5930 59.0072 59.7931 60.20];
%secName='BaffinBayNorth';
%lonLog=[-67.0 -67.0 -76.0];
%latLog=[ 76.5  73.0  72.2];
%secName='JamesBayMouth';
%lonLog=[-82.3  -79.5];
%latLog=[ 54.65  54.65];
%secName='HudsonStraitEndGate';
%lonLog=[-66.2316 -64.7838];
%latLog=[62.0454 60.1663];
%secName='GulfOfBoothiaNorth'
%lonLog=[-90.69 -87.35];
%latLog=[ 73.45  73.68];
%secName='GulfOfBoothiaMiddle'
%lonLog=[-93.59 -89.57];
%latLog=[ 71.40  71.43];
%secName='GulfOfBoothiaSouth'
%lonLog=[-91.28 -84.78];
%latLog=[ 69.42  69.39];
%secName='NorthofCAA1'
%lonLog=[-76.16 -76.16];
%latLog=[ 83.12  85.00];
%secName='NorthofCAA2'
%lonLog=[-95.21 -127.97];
%latLog=[ 80.52  83.99];
%secName='NorthofCAA3'
%lonLog=[-119.30 -138.02];
%latLog=[ 76.97  79.64];
%secName='NorthofGreenland1'
%lonLog=[-38.11 -38.11];
%latLog=[ 83.51  86.00];
%secName='LomonosovRidge1'
%lonLog=[128.29 161.34];
%latLog=[ 82.04  81.91];
%secName='LomonosovRidge2'
%lonLog=[128.29 161.34];
%latLog=[ 85.00  85.00];
%secName='LomonosovRidge3'
%lonLog=[128.29 161.34];
%latLog=[ 89.90  89.90];
%secName='LomonosovRidge4'
%lonLog=[-82.00 -19.00];
%latLog=[ 85.00  85.00];
secName='WesternArctic1'
lonLog=[179.90 125.00];
latLog=[ 84.00  84.00];






 % save some variables
% global lonLog latLog NX NY secName navLon navLat CF meshhgr meshzgr maskfile isClosePoly
% [lonLog,latLog]=myUnique(lonLog,latLog);

 NPT=numel(lonLog);
 indmin=zeros(1,NPT);
 for np=1:NPT
     [~,indmin(np)]=min((navLon(:)-lonLog(np)).^2 + (navLat(:)-latLog(np)).^2);
 end
 [~,iidx,~]=unique(indmin);
 indmin=indmin(sort(iidx));
 [jLogOri,iLogOri]=ind2sub([NY NX],indmin);
 if isClosePoly==1
    if iLogOri(end)~=iLogOri(1) || jLogOri(end)~=jLogOri(1)
       iLogOri=[iLogOri   iLogOri(1)];
       jLogOri=[jLogOri   jLogOri(1)];
    end
 end

 %% secInfo
 secInfo.name=secName;
 secInfo.IIsub=[max(1,min(iLogOri)-4) min(NX,max(iLogOri)+4)];
 secInfo.JJsub=[max(1,min(jLogOri)-4) min(NY,max(jLogOri)+4)];
 indLonLat=sub2ind([NY NX],jLogOri,iLogOri);
 secInfo.myLon=navLon(indLonLat);
 secInfo.myLat=navLat(indLonLat);
 secInfo.iLogOri=iLogOri;
 secInfo.jLogOri=jLogOri;
 secInfo.e3t0varname='e3t';
 secInfo.ncmaskfile=maskfile;
 secInfo.ncmaskfilez=meshzgr;
 secInfo.ncmaskfileh=meshhgr;
 
 if ~exist('secIndex','dir')
    mkdir('secIndex');
 end
 eval(['save secIndex/',CF,'_',secName,'Index.mat secInfo'])
 % clear global variables when close the window
% clearvars -global *
% delete(gcf);
