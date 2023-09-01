function drawLonLatSectionProj
% make section index (used for sectionplot or section-flux calculation) interactively
% usage:
%       drawLonLatSectionProj
% how-to:
%        1: run the script
%        2: zoom into your interested area
%        3: select the start point
%        4: select the end point of the section
%        5: close the window, the secInf mat-file will be saved under secInd folder
% update:
%      Apr-27: add configuration in the secIndex filename (xianmin@ualberta.ca)
%              update the comments
% xianmin@ualberta.ca (redistribution with permission only)

clc;
close all force
clearvars -global *

% global variables
global navLon navLat lonLog latLog NX NY secName CF meshhgr meshzgr maskfile isClosePoly

CF='ANHA12';
secName='PIES';
%secName='westLancasterSound';
%secName='NaresStrait';
%secName='SBIArray';
%secName='BB1500m';
%secName='KennedyChannel';
%secName='DavisStraitOBS';
%secName='LS1000m'; isClosePoly=1;
%secName='OBCs'; isClosePoly=0;
%secName='EGC785II'; isClosePoly=0;
%secName='AR7W'; isClosePoly=0;
%secName='RAPID'; isClosePoly=0;
%secName='FuryHecla'; isClosePoly=0;
%secName='JonesSound'; isClosePoly=0;
%secName='JonesSoundMouth'; isClosePoly=0;
%secName='northCAANorth';
%secName='northCAASouth';
%secName='northCAAFS'; % Fram Sound
%secName='northCAAPS'; % Penny Strait
%secName='northCAAWS';
%secName='ParryChannalWest';
%secName='ParryChannalMid';
%secName='ParryChannalEast';
%secName='ParryChannalSouth';
%secName='ParryChannalNorth';
%secName='ParryChannalNorthB';
%secName='ParryChannalPS';
%secName='ParryChannalSM';
%secName='ParryChannalSomersetBaffin';
%secName='northCAANE';
%secName='northCAASouth';
%secName='northCAAPS'; % Penny Strait
%secName='northCAAWS';
%secName='northCAAFS'; % Fram Sound
%secName='ParryChannalWest';
%secName='ParryChannalMid';
%secName='BSO';
%secName='BeringStrait';
%secName='FramStrait';
%secName='AmundsenGulf';
%secName='DavisStraitSouth';

switch CF
   case {'ANHA4'}
     maskfile='/mnt/storage1/xhu/ANHA4-I/ANHA4_mask.nc';
     meshhgr='/mnt/storage1/xhu/ANHA4-I/ANHA4_mesh_hgr.nc';
     meshzgr='/mnt/storage1/xhu/ANHA4-I/ANHA4_mesh_zgr.nc';
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

figure;
set(gcf,'color','w','CloseRequestFcn',@clearMyGlobal,'Pointer','cross');
if strcmpi(secName,'pies')
   %m_proj('stereographic','lat',65,'long',-60,'radius',45,'rect','on');
   %m_proj('stereographic','lat',65,'long',-60,'radius',15,'rect','on');
   m_proj('stereographic','lat',50.6,'long',-34.5,'radius',15,'rect','on');
   [~,hh]=m_contour(navLon,navLat,tmask,[0.5 0.5],'k-'); hold on
   if exist('OBSlocation/transport_calculation_positions_Tilia.txt')
      SECobs=load('OBSlocation/transport_calculation_positions_Tilia.txt');
      m_plot(SECobs(:,1),SECobs(:,2),'o');
   end
elseif strcmpi(secName,'rapid')
   m_proj('lambert','lat',[20 30],'long',[-120 10]);
   hpmask=m_pcolor(navLon,navLat,tmask); set(hpmask,'linestyle','none'); hold on
   m_plot([-90:5:10],[-90:5:10]*0+26.6,'gs');
elseif strcmpi(secName,'framstrait') ||  strcmpi(secName,'bso')
   m_proj('stereographic','lat',80,'long',0,'radius',20,'rect','on');
   hpmask=m_pcolor(navLon,navLat,tmask); set(hpmask,'linestyle','none'); hold on
   m_plot([-15 15],[78 78]+5/6,'s-')  
elseif strcmpi(secName,'egc785') || strcmpi(secName,'egc785ii')
   m_proj('stereographic','lat',80,'long',0,'radius',10,'rect','on');
   hpmask=m_pcolor(navLon,navLat,tmask); set(hpmask,'linestyle','none');
   hold on;
   m_plot([-6.5:0.5:-1],[-6.5:0.5:-1]*0+78.5,'s-')  
   m_plot([-6.431 -1.042], [78.515   78.485],'ko')
elseif strcmpi(secName(1:8),'northcaa')
   m_proj('stereographic','lat',75,'long',-95,'radius',10,'rect','on');
   hpmask=m_pcolor(navLon,navLat,tmask); set(hpmask,'linestyle','none');
   hold on;
   bsmask=GetNcVar('/mnt/storage1/xhu/HOME/ANHA12/iceH/vol/ANHA12_CAA_ice_mask_three_regions.nc','tmask');
   m_contour(navLon,navLat,bsmask,[0.5 1.5 2.5],'g-')
elseif strcmpi(secName(1:12),'parrychannal')
   m_proj('stereographic','lat',75,'long',-95,'radius',12,'rect','on');
   hpmask=m_pcolor(navLon,navLat,tmask); set(hpmask,'linestyle','none');
   hold on;
   bsmask=GetNcVar('/mnt/storage1/xhu/HOME/ANHA12/iceH/vol/ANHA12_CAA_ice_mask_three_regions.nc','tmask');
   m_contour(navLon,navLat,bsmask,[0.5 1.5 2.5],'g-')
elseif strcmpi(secName(1:12),'AmundsenGulf')
   %m_proj('stereographic','lat',75,'long',-95,'radius',12,'rect','on');
   m_proj('stereographic','lat',75,'long',-115,'radius',12,'rect','on');
   hpmask=m_pcolor(navLon,navLat,tmask); set(hpmask,'linestyle','none');
   hold on;
   bsmask=GetNcVar('/mnt/storage1/xhu/HOME/ANHA12/iceH/vol/ANHA12_CAA_ice_mask_three_regions.nc','tmask');
   m_contour(navLon,navLat,bsmask,[0.5 1.5 2.5],'g-')
elseif strcmpi(secName,'naresstrait') || strcmpi(secName,'jonessound') || strcmpi(secName,'westlancastersound') || strcmpi(secName,'furyhecla')  || strcmpi(secName,'jonessoundcenter') || strcmpi(secName,'jonessoundmouth')
   m_proj('stereographic','lat',75,'long',-90,'radius',20,'rect','on');
   navLon(navLon>0)=nan; navLat(navLat>87)=nan;
   navLon(navLon<-170)=nan; navLat(isnan(navLon))=nan;
   hpmask=m_pcolor(navLon,navLat,tmask); set(hpmask,'linestyle','none');
   hold on;
   m_plot([-91.18 -90.36],[73.97 74.59],'s-')
elseif strcmpi(secName,'beringstrait')
   m_proj('lambert','long',[-175 -160],'lat',[60 70]);
   hpmask=m_pcolor(navLon,navLat,tmask); set(hpmask,'linestyle','none');
   hold on
   m_plot([-91.18 -90.36],[73.97 74.59],'s-')
   m_plot([-168-56/60 -168-5/60],[65+52.1/60 65+50.9/60],'s-')
elseif strcmpi(secName,'sbiarray')
   %m_proj('lambert','long',[-156 -150],'lat',[70 72]);
   m_proj('lambert','long',[-153 -151],'lat',[71 72]);
   [~,hh]=m_contour(navLon,navLat,tmask,[0.5 0.5],'k-'); hold on;
   tmpLon=-[152+13.38/60 152+11.28/60 152+7.62/60 152+6.72/60 152+3.78/60 152+1.56/60 151+59.28/60 151+56.82/60 151+55.98/60 151+53.52/60 151+50.82/60 151+49.14/60 151+46.44/60 151+43.50/60 151+42.96/60];
   tmpLat= [13.49 16.29 18.86 21.91 24.0 26.86 29.68 32.0 34.51 37.53 39.51 42.16 45.32 47.54 50.81]/60+71;
   m_plot(tmpLon,tmpLat,'o-')
   %m_plot(tmpLon(1:6),tmpLat(1:6),'kp')
   m_plot(-[152.0987  152.0468  152.0038  151.9753  151.9310  151.9137  151.8347], [71.3523   71.3948   71.4363   71.4843   71.5318   71.5678   71.6662],'ks');
   disp('black squares show the location of BS2 to BS8')
   m_etopo1('pcolorocean'); caxis([-800 0]); colorbar; hold on
   load nclcolormap; colormap(shiftColor(nclcolormap.example,'low'));
   set(findobj('tag','m_etopo1'),'facecolor','interp')
   m_ShowGridLine(navLon(2185:2200,590:600),navLat(2185:2200,590:600),1)
elseif strcmpi(secName,'kennedychannel') || strcmpi(secName,'naresstrait')
   m_proj('lambert','long',[-76 -58],'lat',[78 82.75]);
   navLon(navLon>0)=nan; navLat(navLat>85)=nan;
   hpmask=m_pcolor(navLon,navLat,tmask); set(hpmask,'linestyle','none')
   hold on;
   % 2003-06
   tmpLon=-[68.8744 67.9296 67.6709 67.4458];
   tmpLat= [80.5538 80.4438 80.4092 80.3884];
   m_plot(tmpLon,tmpLat,'o-')
   % 2007-09
   tmpLon=-[68.7393 68.4555 68.1850 67.8930 67.5927];
   tmpLat= [80.5378 80.5038 80.4715 80.4355 80.3993];
   m_plot(tmpLon,tmpLat,'ks-')
   disp('black squares show the locations in 2007-09')
elseif strcmpi(secName,'bb1500m')
   m_proj('stereographic','lat',72,'long',-66,'radius',8);
   modDep=GetNcVar('/mnt/storage1/xhu/ANHA4-I/ANHA4_bathy_etopo1_gebco1_smoothed_coast_corrected_mar10.nc','Bathymetry');
   [~,hh]=m_contour(navLon,navLat,modDep,[1500 1500],'k-'); hold on;
   m_coast('color','b');
   %m_etopo1('pcolorocean'); caxis([-800 0]); colorbar; hold on
   %set(findobj('tag','m_etopo1'),'facecolor','interp')
   %load nclcolormap; colormap(shiftColor(nclcolormap.example,'low'));
elseif strcmp(secName,'DavisStraitOBS')
   m_proj('stereographic','lat',72,'long',-66,'radius',8);
   %modDep=GetNcVar('/mnt/storage1/xhu/ANHA4-I/ANHA4_bathy_etopo1_gebco1_smoothed_coast_corrected_mar10.nc','Bathymetry');
   %[~,hh]=m_contour(navLon,navLat,modDep,[1500 1500],'k-'); hold on;
   hpmask=m_pcolor(navLon,navLat,tmask); set(hpmask,'linestyle','none'); hold on;
   obsLocation=load('/mnt/storage1/myers/DATA/CANADIAN-ARCTIC/DAVIS-STRAIT/DS0413_mTS.mat','mlon','mlat');
   m_plot(obsLocation.mlon, obsLocation.mlat,'s');
elseif strcmp(secName,'DavisStraitSouth')
   m_proj('stereographic','lat',66,'long',-66,'radius',8);
   %modDep=GetNcVar('/mnt/storage1/xhu/ANHA4-I/ANHA4_bathy_etopo1_gebco1_smoothed_coast_corrected_mar10.nc','Bathymetry');
   %[~,hh]=m_contour(navLon,navLat,modDep,[1500 1500],'k-'); hold on;
   hpmask=m_pcolor(navLon,navLat,tmask); set(hpmask,'linestyle','none'); hold on;
   obsLocation=load('/mnt/storage1/myers/DATA/CANADIAN-ARCTIC/DAVIS-STRAIT/DS0413_mTS.mat','mlon','mlat');
   m_plot(obsLocation.mlon, obsLocation.mlat,'s');
elseif strcmp(secName,'LS1000m') || strcmp(secName,'LS3000m') || strcmp(secName,'LS2000m') || strcmp(secName,'AR7W') || strcmp(secName,'AR7WEast')
   m_proj ('stereographic','lat',60,'long',-50,'radius',15,'rect','on')
   hpmask=m_pcolor(navLon,navLat,tmask); set(hpmask,'linestyle','none'); hold on;
   %modDep=GetNcVar('/mnt/storage1/xhu/ANHA12-I/new_bathymetry/ANHA12_bathymetry_sandwell_etopo1_2014_rmax_10.nc', 'Bathymetry');
   %[~,hh]=m_contour(navLon,navLat,modDep,[1500 1500],'k-'); hold on;
   latlonAR7W=load('/mnt/storage1/xhu/ANHA12-EXH003/section/longlat_ar07w');
   m_plot(latlonAR7W(:,2),latlonAR7W(:,1),'s');
   m_coast('color','b');
   m_etopo2('contour',[-3500 -3500],'k-');
   modDep=GetNcVar('/mnt/storage1/xhu/ANHA12-I/new_bathymetry/ANHA12_bathymetry_sandwell_etopo1_2014_rmax_10.nc','Bathymetry');
   [~,hh]=m_contour(navLon,navLat,modDep,[3500 3500],'k-'); hold on;
else
   m_proj('stereographic','lat',90,'long',-60,'radius',45,'rect','on');
   [~,hh]=m_contour(navLon,navLat,tmask,[0.5 0.5],'k-'); hold on
end
%m_etopo2('pcolorocean'); caxis([-4000 0]); colorbar;
m_grid; hold on;
% datacursor
mycobj=datacursormode(gcf);
datacursormode on;
set(mycobj,'UpdateFcn',@myupdatefcn,'SnapToDataVertex','off','Enable','on','DisplayStyle','window');
title(secName,'fontweight','bold')

end

%---------------------------------------------------------------
function clearMyGlobal(varargin)
 % save some variables
 global lonLog latLog NX NY secName navLon navLat CF meshhgr meshzgr maskfile isClosePoly
 [lonLog,latLog]=myUnique(lonLog,latLog);

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
 clearvars -global *
 delete(gcf);
end

function output_txt = myupdatefcn(~,~)
% Display the position of the data cursor
% obj          Currently not used (empty)
% event_obj    Handle to event object
% output_txt   Data cursor text string (string or cell array of strings).

hh=datacursormode(gcf);
if strcmpi(hh.Enable,'on')
    global preXX preYY lonLog latLog
    pos = get(gca,'CurrentPoint');
    [clon,clat]=m_xy2ll(pos(1,1),pos(1,2));
    if ~ishold, hold on; end
    plot(pos(1,1),pos(1,2),'ko');  % label the previous selections
    lonLog=[lonLog clon];
    latLog=[latLog clat];
    
    if ~isempty(preXX)
        plot([preXX pos(1,1)],[preYY pos(1,2)])
    end
    % update previous location
    preXX=pos(1,1); preYY=pos(1,2);
    output_txt = {['Lon: ',num2str(clon,4)],[' Lat: ',num2str(clat,4)]};
else
    output_txt='';
end
end
