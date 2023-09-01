function  [secVol,secHeat,secSalt,secFW,secIce]=getSectionFlux(secName,timeTag,varargin)
% compute cross-section volume, heat, and salt fluxes for a specific water mass
% usage:
%        [secVol,secHeat,secSalt]=getSectionFlux(secName,timeTag,varargin)
%             varargin option:
%                             'dataP',dataP: model output folder
%                             'CF', CF     : config-experiment (default: CREG012-EXH003)
%                                            datafile ==> [dataP CF_timeTag_grid[TUV].nc]
%                     'secIndexP',secIndexP: path for secIndex file (check mkSectionIndex.m for details)
%                                            .secII, .secJJ: subscripts for section nodes
%                                                  .II, .JJ: 
%                     'matfileP', matfileP : path for section mat-file created by combineSectionTSUV.m
%   Note:
%        secVol: volume flux through each cell (NZ x NumOfPoints array, unit: m^3/s)
%                total volume flux: nansum(secVol(:))
%       secHeat: heat flux (NZ x NPT array, unit: TW (10^12W)), reference temperature: 0^oC
%       secSalt: salt flux (NZ x NPt array, unit: kt/s (1000 ton per second)

%    April 2014, xianmin@ualberta.ca
%   August 2014, xianmin@ualberta.ca
%                modified to be f-grid based (produce same results as cdftools)
%                save secT and secS using original t & s (to avoid nan where volume flux is zero)

if nargin<2
   help getSectionFlux
   return
end

secIndexP='./secIndex/';

matfileP='./matfile/';

if ~exist(matfileP,'dir')
    mkdir(matfileP)
end

isUpdate=0;
%CF='ANHA4-EPM048';
methodType=0;  % 0 is more accurate (close to the values from cdftools
tRef=-2.0;
sRef=34.8;
isDisp=0;
tLim=[-3 100]; % tempearture range
sLim=[0 50];   % salinity range
isForceUpdate=0;
isReplace=0;
isE3=1;

while(size(varargin,2)>0)
   switch lower(varargin{1})
     case {'cf','case','casetag','conf','config-case'}
          CF=varargin{2};
          varargin(1:2)=[];
     case {'src','datasrc','rootp','datafolder','datap'}
          dataP=varargin{2};
          varargin(1:2)=[];
     case {'savep'}
          isSubFolder=1;
          saveP=varargin{2};
          varargin(1:2)=[];
     case {'secp','sectionindex','secindex','secindexp'}
          secIndexP=varargin{2};
          varargin(1:2)=[];
     case {'ov','update','write','overwrite','isupdate'}
          isUpdate=1;
          varargin(1)=[];
     case {'-f','force'}
          isForceUpdate=1;
          varargin(1)=[];
     case {'tref','reft'}
          tRef=varargin{2};
          varargin(1:2)=[];
     case {'sref','refs'}
          sRef=varargin{2};
          varargin(1:2)=[];          
     case {'t','tlim','trange'}
          tLim=varargin{2};
          varargin(1:2)=[];
     case {'tmin','mint'}
          tLim(1)=varargin{2};
          varargin(1:2)=[];
     case {'tmax','maxt'}
          tLim(2)=varargin{2};
          varargin(1:2)=[];          
     case {'s','srange','slim'}
          sLim=varargin{2};
          varargin(1:2)=[];
     case {'smin','mins'}
          sLim(1)=varargin{2};
          varargin(1:2)=[];
     case {'smax','maxs'}
          sLim(2)=varargin{2};
          varargin(1:2)=[];          
     case {'method','fluxtype','type','mtype'}
          methodType=varargin{2};
          varargin(1:2)=[];
     case {'print','screen','debug','disp','display'}
          isDisp=1;
          varargin(1)=[]; 
       otherwise
          disp(['unknow option: ',varargin{1}])          
          varargin(1)=[];
   end
end

dataP

if isdir(secIndexP)
   secfile=[secIndexP,secName,'Index.mat'];
else
  if exist(secIndexP,'file')
    secfile=secIndexP;
    secIndexP=[fileparts(secfile),'/'];
  else
    secfile=[secIndexP,secName,'Index.mat']; 
  end
end

if ~exist(secfile,'file'), error(['section info file is not found! ',secfile]); end
eval(['load ',secfile]);


   
% make the local index and section fluxes associated fields if not exists
if ~isfield(secInfo,'locIndex') || isForceUpdate==1
   if ~isfield(secInfo,'iLogOri')
      error(['Please create the iLogOri field in secInfo: ',secfile])
   end
  if isUpdate==1
       section=mkSectionIndex(secName,secInfo.iLogOri,secInfo.jLogOri,'secIndexP',secIndexP,'update');
   else
     section=mkSectionIndex(secName,secInfo.iLogOri,secInfo.jLogOri,'secIndexP',secIndexP);
   end
else
   section=secInfo; clear secInfo;
end

caseTagStr=strrep(CF,'-','_');
secResult=[caseTagStr,'_',secName,'_',timeTag,'_TSUV'];
%secResult=[caseTagStr,'_','labsea','_',timeTag,'_TSUV'];
if any(strcmp(who,'saveP'))
    secName=strsplit(secName,'-');
    matfileP=saveP;
    %secResult=[caseTagStr,'_','labsea','_',timeTag,'_TSUV'];
    %secResult1=['ANHA4_ECP004','_','labsea','_',timeTag,'_TSUV'];
    secResult1=[caseTagStr,'_',secName{1},'_',timeTag,'_TSUV'];
end

% model outputs

secResult1

if ~exist([matfileP,secResult,'.mat'],'file') || isReplace==1 ;
    sprintf(['I COMPUTE ',matfileP,secResult,'.mat for this date and section'])
    %timeTag=[timeTag,'_HBCclip'];
    tfile=[dataP,CF,'_',timeTag,'_gridT.nc']; if ~exist(tfile,'file'), error([tfile,' is not found!']); end
    sfile=[dataP,CF,'_',timeTag,'_gridT.nc']; if ~exist(sfile,'file'), error([sfile,' is not found!']); end
    ufile=[dataP,CF,'_',timeTag,'_gridU.nc']; if ~exist(ufile,'file'), error([ufile,' is not found!']); end
    vfile=[dataP,CF,'_',timeTag,'_gridV.nc']; if ~exist(vfile,'file'), error([vfile,' is not found!']); end
    icefile=[dataP,CF,'_',timeTag,'_icemod.nc']; if ~exist(sfile,'file'), error([sfile,' is not found!']); end

    NZ=size(section.mask,1);
    secVol=zeros(NZ,section.NPT);
    secSalt=secVol;
    secHeat=secVol;  rho0=1000; rcp=4000;
    secT=secVol; secS=secVol; % salinity and temperature
    heatfactor=rho0*rcp*1e-12;  % ==> TW
    uu=zeros(section.ncIndCnt([2 1]));
    vv=uu;tt=uu; ss=tt; 
    uut=uu; vvt=uu; 
    uus=uu;vvs=uu;
    uuis=uu;vvis=uu;
    uui=uu;vvi=uu;
    uuic=uu;vvic=uu;
    uuih=uu;vvih=uu;

    for nz=1:NZ
        if any(section.mask(nz,:)>0)
           uu(:,:)=GetNcVar(ufile,'vozocrtx',[section.ncStartInd(1:2) nz-1 0],[section.ncIndCnt(1:2) 1 1]); 
           vv(:,:)=GetNcVar(vfile,'vomecrty',[section.ncStartInd(1:2) nz-1 0],[section.ncIndCnt(1:2) 1 1]);
           
           % temperature range
           tt(:,:)=GetNcVar(tfile,'votemper',[section.ncStartInd(1:2) nz-1 0],[section.ncIndCnt(1:2) 1 1]);
           uut(:,1:end-1)=(tt(:,1:end-1)+tt(:,2:end))*0.5; uut(:,end)=uut(:,end-1);  % t at u-point
           vvt(1:end-1,:)=(tt(1:end-1,:)+tt(2:end,:))*0.5; vvt(end,:)=vvt(end-1,:);  % t at v-point
           % salinity range
           ss(:,:)=GetNcVar(sfile,'vosaline',[section.ncStartInd(1:2) nz-1 0],[section.ncIndCnt(1:2) 1 1]);
           uus(:,1:end-1)=(ss(:,1:end-1)+ss(:,2:end))*0.5; uus(:,end)=uus(:,end-1); % s at u-point
           vvs(1:end-1,:)=(ss(1:end-1,:)+ss(2:end,:))*0.5; vvs(end,:)=vvs(end-1,:); % s at v-point           
           % ice H
           iceh(:,:)=GetNcVar(icefile,'iicethic',[section.ncStartInd(1:2) 0],[section.ncIndCnt(1:2) 1]);
           uuih(:,1:end-1)=(iceh(:,1:end-1)+iceh(:,2:end))*0.5; uuih(:,end)=uuih(:,end-1); % s at u-point
           vvih(1:end-1,:)=(iceh(1:end-1,:)+iceh(2:end,:))*0.5; vvih(end,:)=vvih(end-1,:); % s at v-point           
           % ice C
           icec(:,:)=squeeze(GetNcVar(icefile,'ileadfra',[section.ncStartInd(1:2) 0],[section.ncIndCnt(1:2) 1]));
           uuic(:,1:end-1)=(icec(:,1:end-1)+icec(:,2:end))*0.5; uuic(:,end)=uuic(:,end-1); % s at u-point
           vvic(1:end-1,:)=(icec(1:end-1,:)+icec(2:end,:))*0.5; vvic(end,:)=vvic(end-1,:); % s at v-point 
           % ice velo
           ui(:,:)=GetNcVar(icefile,'iicevelv',[section.ncStartInd(1:2) 0],[section.ncIndCnt(1:2) 1]); 
           vi(:,:)=GetNcVar(icefile,'iicevelu',[section.ncStartInd(1:2) 0],[section.ncIndCnt(1:2) 1]);
           uui(:,1:end-1)=(ui(:,1:end-1)+ui(:,2:end))*0.5; uui(:,end)=uui(:,end-1); % ui at u-point
           vvi(1:end-1,:)=(vi(1:end-1,:)+vi(2:end,:))*0.5; vvi(end,:)=vvi(end-1,:); % vi at v-point           
           % wind stress
           uuos(:,:)=GetNcVar(ufile,'sozotaux',[section.ncStartInd(1:2) 0],[section.ncIndCnt(1:2) 1]); 
           vvos(:,:)=GetNcVar(vfile,'sometauy',[section.ncStartInd(1:2) 0],[section.ncIndCnt(1:2) 1]);
           % ice stress
           uuis=1035*5e-3.*abs(uui - uu).*abs(uui - uu) ;
           vvis=1035*5e-3.*abs(vvi - vv).*abs(vvi - vv) ;

           uu(uut<tLim(1))=nan; uu(uut>tLim(2))=nan; uu(uus<sLim(1))=nan; uu(uus>sLim(2))=nan;
           vv(vvt<tLim(1))=nan; vv(vvt>tLim(2))=nan; vv(vvs<sLim(1))=nan; vv(vvs>sLim(2))=nan;

	   try getNcVar(ufile,'e3u',[0 0 0],[1 1 1]);
           catch exception 
             isE3=0;
           end
           if isE3==1
             e3u=getNcVar(ufile,'e3u',[section.ncStartInd(1:2) nz-1 0],[section.ncIndCnt(1:2) 1 1]);
             section.sectionE3u(nz,:)=e3u(section.uuIndex);
             e3v=getNcVar(vfile,'e3v',[section.ncStartInd(1:2) nz-1 0],[section.ncIndCnt(1:2) 1 1]);
              section.sectionE3v(nz,:)=e3v(section.vvIndex);
           end

           if nz == 1 
                  if methodType==0
                      % Ice velocity
                      secIceVel(:)= uui(section.uuIndex).*section.uSign.*section.E2U2D(section.uuIndex) ...
                                   +vvi(section.vvIndex).*section.vSign.*section.E1V2D(section.vvIndex);
                      % Ice Transport
                      secIce(:)= uuih(section.uuIndex).*uuic(section.uuIndex).*uui(section.uuIndex).*section.uSign.*section.E2U2D(section.uuIndex) ...
                                +vvih(section.vvIndex).*vvic(section.vvIndex).*vvi(section.vvIndex).*section.vSign.*section.E1V2D(section.vvIndex);
                      % Surface stress
                      uust=uuic(section.uuIndex).*uuis(section.uuIndex) + (1-uuic(section.uuIndex)).*uuos(section.uuIndex) ;
                      vvst=vvic(section.vvIndex).*vvis(section.vvIndex) + (1-vvic(section.vvIndex)).*vvos(section.vvIndex) ;
                      secStress(:) = sqrt(uust.^2 + vvst.^2); % no need for uu/vv-indexes here.
                      % Ice Fraction
                      secIceC=uuic(section.uuIndex) + vvic(section.vvIndex);
                  end  
           end
           
           for nv=1:5
               if nv==1  % vol
                  if methodType==0
                     secVol(nz,:)=   uu(section.uuIndex).*section.E2U2D(section.uuIndex).*section.uSign.*section.sectionE3u(nz,:) ...
                                    +vv(section.vvIndex).*section.E1V2D(section.vvIndex).*section.vSign.*section.sectionE3v(nz,:);              
                  else
                     error('not defined methodType')
                  end
               elseif nv==2 % heat
                  secT(nz,:)= uut(section.uuIndex).*abs(section.uSign) ...
                             +vvt(section.vvIndex).*abs(section.vSign);
                  uut(:,:)=(uut-tRef).*uu*heatfactor; vvt(:,:)=(vvt-tRef).*vv*heatfactor;
                  if methodType==0
                     secHeat(nz,:)=  uut(section.uuIndex).*section.E2U2D(section.uuIndex).*section.uSign.*section.sectionE3u(nz,:) ...
                                    +vvt(section.vvIndex).*section.E1V2D(section.vvIndex).*section.vSign.*section.sectionE3v(nz,:);              
                     %  secT(nz,:)= uut(section.uuIndex)./uu(section.uuIndex).*abs(section.uSign) ...
                     %             +vvt(section.vvIndex)./vv(section.vvIndex).*abs(section.vSign);
                  else
                     error('not defined methodType')
                  end
               elseif nv==3 % salt             
                  secS(nz,:)= uus(section.uuIndex).*abs(section.uSign) ...
                             +vvs(section.vvIndex).*abs(section.vSign);
                  uus(:,:)=uus.*uu;  vvs(:,:)=vvs.*vv;
                  if methodType==0
                     secSalt(nz,:)=  uus(section.uuIndex).*section.E2U2D(section.uuIndex).*section.uSign.*section.sectionE3u(nz,:) ...
                                    +vvs(section.vvIndex).*section.E1V2D(section.vvIndex).*section.vSign.*section.sectionE3v(nz,:);              
                     %  secS(nz,:)= uus(section.uuIndex)./uu(section.uuIndex).*abs(section.uSign) ...
                     %             +vvs(section.vvIndex)./vv(section.vvIndex).*abs(section.vSign);
                  end                  
              end % switch of a variable
           end % Loop of variables
           %disp(['level=',num2str(nz)])
        else
          secVol(nz,:)=nan;
          secHeat(nz,:)=nan;
          secSalt(nz,:)=nan;
          secT(nz,:)=nan;
          secS(nz,:)=nan;
        end
    end

    secFW=secVol-secSalt./sRef ;
    secSalt=secSalt*1e-6; %==> kt s^-1
    %secIce=secIce.*(sRef-6)./sRef ;
    %secT=secT/heatfactor; 
    secT(secS==0)=nan;
    secS(secS==0)=nan; %#ok<*NASGU>
else
    eval(['load ',matfileP,secResult,'.mat '])
    sprintf(['I OPENED',matfileP,secResult,'.mat for this date and section'])

    
    eval(['secVol=', secResult1,'.secVolFlux ;'])
    eval(['secHeat=', secResult1,'.secHeatFlux ;'])
    eval(['secSalt=', secResult1,'.secSaltFlux ;'])
    eval(['secFW=', secResult1,'.secFWFlux ;'])    
    %eval(['secIce=', secResult1,'.secIceFlux ;'])
    %eval(['secIceVel=',secResult1,'.secIceVelocity;'])
    %eval(['secStress=',secResult1,'.secSurfaceStress;'])
    %eval(['secIceC=',secResult1,'.secIceC;'])
    eval(['sLim=', secResult1,'.sRange ;'])
    eval(['tLim=', secResult1,'.tRange ;'])
    eval(['tRef=', secResult1,'.tRef ;'])
    eval(['sRef=', secResult1,'.sRef ;'])
end

if isDisp==1
   disp(['Methodtype: ',num2str(methodType), ' tLim=',num2str(tLim(1)),' - ',num2str(tLim(2)),' sLim=',num2str(sLim(1)),' - ',num2str(sLim(2))])
   disp([' total  vol: ',num2str(nansum(secVol(:)),10)])
   disp([' total heat: ',num2str(nansum(secHeat(:)),10)])
   disp([' total salt: ',num2str(nansum(secSalt(:)),10)])
   disp([' total freswhater: ',num2str(nansum(secFW(:)),10)])  
end

if isUpdate==1
    % add fields into 
   if ~exist([matfileP,secResult,'.mat'],'file')
     %disp([matfileP,secResult,'.mat is not found!'])
   else
      eval(['load ',matfileP,secResult,'.mat'])
   end
   if exist('secT','var')
   %   eval([secResult,'.secT=secT;'])
   end
   if exist('secS','var')
   %   eval([secResult,'.secS=secS;'])
   end
   eval([secResult1,'.secVolFlux=secVol;'])
   eval([secResult1,'.secHeatFlux=secHeat;'])
   eval([secResult1,'.secSaltFlux=secSalt;'])
   eval([secResult1,'.secFWFlux=secFW;'])
   %eval([secResult1,'.secIceFlux=secIce;'])
   %eval([secResult1,'.secIceVelocity=secIceVel;'])
   %eval([secResult,'.secSurfaceStress=secStress;'])
   %eval([secResult,'.secIceC=secIceC;'])
   eval([secResult1,'.totalVolFlux=nansum(secVol(:));'])
   eval([secResult1,'.totalHeatFlux=nansum(secHeat(:));'])
   eval([secResult1,'.totalSaltFlux=nansum(secSalt(:));'])
   eval([secResult1,'.totalFWFlux=nansum(secFW(:));'])
   %eval([secResult1,'.totalIceFlux=nansum(secIce(:));'])
   %eval([secResult1,'.meanSurfaceStress=nanmean(secStress(:));'])
   %eval([secResult1,'.meanIceVelocity=nanmean(secIceVel(:));'])
   %eval([secResult1,'.meanIceConcentration=nanmean(secIceC(:));'])
   eval([secResult1,'.saltFluxUnit=''kt s^-1'';'])
   eval([secResult1,'.heatFluxUnit=''TW'';'])
   eval([secResult1,'.volFluxUnit=''m^3 s^-1'';'])   
   eval([secResult1,'.iceFluxUnit=''m^3 s^-1'';'])   
   eval([secResult1,'.surfaceStressUnit=''N m^-2'';'])   
   eval([secResult1,'.sRange=sLim;'])
   eval([secResult1,'.tRange=tLim;'])
   eval([secResult1,'.tRef=tRef;'])
   eval([secResult1,'.sRef=sRef;'])
   eval(['save ',matfileP,secResult1,'.mat ',secResult1])
end
if nargout==0
   clear secVol secHeat secSalt
end
