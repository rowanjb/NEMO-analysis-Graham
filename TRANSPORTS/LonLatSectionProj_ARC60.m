close all force
clear all
clear all
%clearvars -global *

% global variables
%global navLon navLat lonLog latLog NX NY secName CF meshhgr meshzgr maskfile isClosePoly

CF='ARC60';

switch CF
   case {'ANHA4'}
     maskfile='/mnt/storage0/xhu/ANHA4-I/ANHA4_mask.nc';
     meshhgr='/mnt/storage0/xhu/ANHA4-I/ANHA4_mesh_hgr.nc';
     meshzgr='/mnt/storage0/xhu/ANHA4-I/ANHA4_mesh_zgr.nc';
   case {'ANHA12'}
     maskfile='/mnt/storage0/xhu/ANHA12-I/new_bathymetry/ANHA12_mask.nc';
     meshhgr='/mnt/storage0/xhu/ANHA12-I/new_bathymetry/ANHA12_mesh_hgr.nc';
     meshzgr='/mnt/storage0/xhu/ANHA12-I/new_bathymetry/ANHA12_mesh_zgr.nc';
   case {'LAB60'}
     maskfile='/mnt/storage4/clark/ANHA4-ECP007/2_ANHA4-ECP007_mask.nc';
     meshhgr='/mnt/storage4/clark/ANHA4-ECP007/2_ANHA4-ECP007_mesh_hgr.nc';
     meshzgr='/mnt/storage4/clark/ANHA4-ECP007/2_ANHA4-ECP007_mesh_zgr.nc';
   case {'ARC60'}
     maskfile='/mnt/storage6/clark/NEMO_meshes/ARC60/ARC60_mask.nc';
     meshhgr='/mnt/storage6/clark/NEMO_meshes/ARC60/ARC60_mesh_hgr.nc';
     meshzgr='/mnt/storage6/clark/NEMO_meshes/ARC60/ARC60_mesh_zgr.nc';
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
secName='Fram2';
lon=[0.03307 0.02228]; %[x1,x2]
lat=[-0.1736 -0.1688]; %[y1,y2]
[lonLog,latLog]=m_xy2ll(lon,lat);
secName='OSNAP';
lonLog=[-57.0 -52.0996 -49.7806 -47.5645 -45.7209 -45.0];
latLog=[52.0 52.6653 53.5930 59.0072 59.7931 60.20];

secName='AZMP_BB';
lonLog=[-52.9667 -47.9467];
latLog=[48.7333 50.3317];
secName='AZMP_BI';
lonLog=[-61.3050 -58.5833];
latLog=[57.0583 57.8833];
secName='AZMP_FC';
lonLog=[-52.8317 -42.0];
latLog=[47.0 47.0];
secName='AZMP_MB';
lonLog=[-58.5133 -56.5100];
latLog=[55.2167 56.0783];
secName='AZMP_SEGB';
lonLog=[-52.9333 -48.6667];
latLog=[46.5833 41.5833];
secName='AZMP_SI';
lonLog=[-55.6500 -52.500];
latLog=[53.3333 55.0667];
secName='AZMP_WB';
lonLog=[-56.4533 -49.7500];
latLog=[50.2267 52.1167];
secName='Uummannaq_Inner';
lonLog=[-54.2 -54.4];
latLog=[70.8 71.33];
secName='Uummannaq_Outer';
lonLog=[-54.8 -55.4];
latLog=[70.33 71.6];




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
% secInfo.e3t0varname='e3t';
 secInfo.e3t0varname='e3t_1d';
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
