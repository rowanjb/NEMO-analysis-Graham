close all force
clear all
clear all
%clearvars -global *

% global variables
%global navLon navLat lonLog latLog NX NY secName CF meshhgr meshzgr maskfile isClosePoly

CF='ANHA4';

switch CF
   case {'ANHA4'}
     maskfile='/mnt/storage1/xhu/ANHA4-I/ANHA4_mask.nc';
     meshhgr='/mnt/storage1/xhu/ANHA4-I/ANHA4_mesh_hgr.nc';
     meshzgr='/mnt/storage1/xhu/ANHA4-I/ANHA4_mesh_zgr.nc';
   case {'ANHA12'}
     maskfile='/mnt/storage0/xhu/ANHA12-I/new_bathymetry/ANHA12_mask.nc';
     meshhgr='/mnt/storage0/xhu/ANHA12-I/new_bathymetry/ANHA12_mesh_hgr.nc';
     meshzgr='/mnt/storage0/xhu/ANHA12-I/new_bathymetry/ANHA12_mesh_zgr.nc';
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
%secName='AZMP_BB';
%lonLog=[-52.9667 -47.9467];
%latLog=[48.7333 50.3317];
%secName='OSNAP';
%lonLog=[-57.0 -52.0996 -49.7806 -47.5645 -45.7209 -45.0];
%latLog=[52.0 52.6653 53.5930 59.0072 59.7931 60.20];
%secName='AZMP_BI';
%lonLog=[-61.3050 -58.5833];
%latLog=[57.0583 57.8833];
%secName='AZMP_FC';
%lonLog=[-52.8317 -42.0];
%latLog=[47.0 47.0];
%secName='AZMP_MB';
%lonLog=[-58.5133 -56.5100];
%latLog=[55.2167 56.0783];
%secName='AZMP_SEGB';
%lonLog=[-52.9333 -48.6667];
%latLog=[46.5833 41.5833];
%secName='AZMP_SI';
%lonLog=[-55.6500 -52.500];
%latLog=[53.3333 55.0667];
%secName='AZMP_WB';
%lonLog=[-56.4533 -49.7500];
%latLog=[50.2267 52.1167];
%secName='ParryChannalEast';
%lonLog=[-80.4948 -82.0024];
%latLog=[73.7327 74.6640];
%secName='BaffinBayNorth';
%lonLog=[-67.0 -67.0 -76.0];
%latLog=[ 76.5  73.0  72.2];
%secName='JamesBayMouth';
%lonLog=[-82.3  -79.5];
%latLog=[ 54.65  54.65];
%secName='JamesBayMouth2';
%lonLog=[-82.3  -79.5];
%latLog=[ 54.65  54.65];
%secName='GulfOfBoothiaNorth'
%lonLog=[-90.69 -87.35];
%latLog=[ 73.45  73.68];
%secName='GulfOfBoothiaMiddle'
%lonLog=[-93.59 -89.57];
%latLog=[ 71.40  71.43];
%secName='GulfOfBoothiaSouth'
%lonLog=[-91.28 -84.78];
%latLog=[ 69.42  69.39];
%secName='GulfOfBoothiaMiddle2'
%lonLog=[-92.36 -88.82];
%latLog=[ 72.82  72.82];
%secName='LS_2000m_isobath'
secName='LabSea2kDepth'
lonLog=[-51.4992 -52.6373 -56.5496 -58.4562 -60.0925 -60.2982 -57.0936 -52.7255 -50.1475 -47.5044 -44.4362 -44.5681 -43.5097]
latLog=[53.1388 54.8910 55.7519 57.5588 60.1108 61.0223 63.3172 62.8904 61.0619 60.0037 59.0564 58.4538 58.6695]

%print(length(latLog))
%quit
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
