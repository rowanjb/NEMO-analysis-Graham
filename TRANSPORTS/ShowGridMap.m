function ShowGridMap()
% to show model horizontal mesh
% history:
%      xxx, 2008: xianmin@ualberta.ca (redistribution with permission only)
%               : updated for NAA, ANHA configurations

nCF=4;

nSkip=15;
isCoast=1;
isMask=0;
isV=1;
isV=0;
isLS=0;  % Labrador Sea
isCleanMap=1;
if nCF==1
     meshfile='/mnt/storage0/xhu/NAA-I/mesh_mask_arc4.nc';
     maskfile=meshfile;
     CFstr='NAA';
     m_proj('stereographic','long',-30,'lat',85,'radius',45);
     nSkip=8;
     xxTick0=-150:30:180; yyTick0=50:10:80;
     xxTick=-120:60:180; yyTick=55:10:85;
elseif nCF==0 
     meshfile='/mnt/storage0/xhu/PROGRAM/orca2creg/orca05/ANHA2_mesh_mask.nc';
     maskfile=meshfile;
     CFstr='ANHA2';
     m_proj('Azimuthal Equal-area','lat',48,'long',-30,'radius',[-105 -45],'rect','on')
     nSkip=5;
     xxTick=-120:60:180; yyTick=-10:10:80;
     myCAXIS=[15 60];
     isMask=1;
elseif nCF==2 
     meshfile='/mnt/storage0/xhu/CREG025-I/CREG025_coordinates.nc';
     maskfile='/mnt/storage0/xhu/CREG025-I/CREG025-CICEREF_tmask.nc';
     CFstr='ANHA4';
     %m_proj('stereographic','lat',45,'long',-30,'radius',75);
     %m_proj('ortho','lat',55,'long',-30);
     %m_proj('ortho','lat',35,'long',-45,'radius',95);
     %m_proj('ortho','lat',40,'long',-45,'radius',95,'rotate',-5);
     %m_proj('ortho','lat',30,'long',-30,'radius',95,'rotate',-0);
     %m_proj('Azimuthal Equidistant','lat',45,'long',-30,'radius',70);
     %m_proj('Azimuthal Equal-area','lat',38,'long',-30,'radius',88);
     m_proj('Azimuthal Equal-area','lat',48,'long',-30,'radius',[-105 -45],'rect','on')
     %m_proj('Azimuthal Equidistant','lat',50,'long',-30,'radius',[-100 -40],'rect','on')
     nSkip=10;
     xxTick=-120:60:180; yyTick=-10:10:80;
     myCAXIS=[8 28];
     isMask=1;
elseif nCF==3
    
    meshfile='/mnt/storage0/xhu/ANHA12-I/new_bathymetry/ANHA12_mesh_hgr.nc';
    maskfile='/mnt/storage0/xhu/ANHA12-I/new_bathymetry/ANHA12_mask.nc';
    %meshfile='/mnt/storage0/xhu/CREG012-I/mask/CREG012_mesh_hgr.nc';
    %maskfile='/mnt/storage0/xhu/CREG012-I/mask/CREG012_mask_v34.nc';
    CFstr='ANHA12';
    if isLS==0
        %m_proj('ortho','lat',30,'long',-30,'radius',95,'rotate',-0);
        m_proj('Azimuthal Equal-area','lat',48,'long',-30,'radius',[-105 -45],'rect','on')
        nSkip=20;
        xxTick=-120:60:180; yyTick=-10:10:80;
        myCAXIS=[3.5 9.5];
     else
        m_proj('Azimuthal Equal-area','lat',60,'long',-50,'radius',[-80 40],'rect','on')
        nSkip=5;
        xxTick=-120:60:180; yyTick=-10:10:80;
        myCAXIS=[3.5 7];
        IIsub=[250 970]; JJsub=[920 1330];
     end
     isMask=1;
elseif nCF==4

    meshfile='/mnt/storage5/clark/CAA60/MakeCoord/CAA60_coordinates_final.nc';
    maskfile='/mnt/storage5/clark/CAA60/MakeBathy/CAA60_Bathymetry_final.nc';
    %meshfile='/mnt/storage0/xhu/CREG012-I/mask/CREG012_mesh_hgr.nc';
    %maskfile='/mnt/storage0/xhu/CREG012-I/mask/CREG012_mask_v34.nc';
    CFstr='ARC60';
    if isLS==0
        %m_proj('ortho','lat',30,'long',-30,'radius',95,'rotate',-0);
        %m_proj('Azimuthal Equal-area','lat',48,'long',-30,'radius',[-105 -45],'rect','on')
        m_proj('Azimuthal Equal-area','lat',90,'long',-30,'radius',[-105 55])
        nSkip=20;
        xxTick=-120:60:180; yyTick=-10:10:80;
        myCAXIS=[0.3 1.2];
     else
        m_proj('Azimuthal Equal-area','lat',60,'long',-50,'radius',[-80 40],'rect','on')
        nSkip=5;
        xxTick=-120:60:180; yyTick=-10:10:80;
        myCAXIS=[3.5 7];
        IIsub=[250 970]; JJsub=[920 1330];
     end
     isMask=1;
else
     error('not defined nCF')
end
if isLS==1
   nav_lon=GetNcVar(meshfile,'nav_lon',[IIsub(1)-1 JJsub(1)-1],[diff(IIsub)+1 diff(JJsub)+1]);
   nav_lat=GetNcVar(meshfile,'nav_lat',[IIsub(1)-1 JJsub(1)-1],[diff(IIsub)+1 diff(JJsub)+1]);
   e1t=GetNcVar(meshfile,'e1t',[IIsub(1)-1 JJsub(1)-1 0],[diff(IIsub)+1 diff(JJsub)+1 1])*1e-3;
else
   nav_lon=GetNcVar(meshfile,'nav_lon');
   nav_lat=GetNcVar(meshfile,'nav_lat');
   e1t=GetNcVar(meshfile,'e1t')*1e-3; % km
end
if isMask==1
   if isLS==1
      lsmask=GetNcVar(maskfile,'tmask',[IIsub(1)-1 JJsub(1)-1 0 0],[diff(IIsub)+1 diff(JJsub)+1 1 1]);
   else
      NX=GetNcDimLen(maskfile,'x');
      NY=GetNcDimLen(maskfile,'y');
      lsmask=GetNcVar(maskfile,'Bathymetry',[0 0],[NX NY]);
   end
   e1t(lsmask==0)=nan;
end

m_pcolor(nav_lon,nav_lat,e1t); set(findobj('tag','m_pcolor'),'linestyle','none')
if exist('myCAXIS','var')
   caxis(myCAXIS)
end
if isCoast==1
   m_coast('patch',[0.3 0.3 0.3]); set(findobj('tag','m_coast'),'linestyle','none')
else
   m_gshhs_i('patch',[0.3 0.3 0.3]); set(findobj('tag','m_gshhs_i'),'linestyle','none')
end
m_nolakes()
hold on;
%if isV==1
%   m_ShowGridLine(nav_lon,nav_lat,nSkip,[0.6 0.6 0.6])
%else
%   m_ShowGridLine(nav_lon,nav_lat,nSkip,[0 0 0.7])
%end
%set(findobj(gcf,'tag','glines'),'linewidth',0.05)

if exist('xxTick0','var')
   m_grid('xtick',xxTick0,'ytick',yyTick0,'xticklabel','','yticklabel','','tickdir','out','color','g');
end
m_grid('xtick',xxTick,'ytick',yyTick,'fonts',12,'fontw','b','tickdir','out','linestyle','-','color','g');
set(findobj('tag','m_grid_box'),'linewidth',2,'color','k');

%xlabel('Model grids on t-points','fontweight','bold')
set(gcf,'color','w');
load nclcolormap
colormap(nclcolormap.BlAqGrYeOrReVi200)
hbar=colorbar; set(hbar,'fontname','Nimbus Sans L','fontweight','bold','linewidth',2,'fontsize',14);
fixcolorbar(1,hbar);
if isCleanMap==1
   cleanmap
end
%disp(['print -dpng -r300 fig/grid_',CFstr,'.png']);
disp(['print -dpng -r300 grid_',CFstr,'.png']);
