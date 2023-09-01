function secInfo=mkSectionIndex(secName,secII,secJJ,varargin)
% prepare for later cross-section fluxes calculation
% usage:
%       secInfo=mkSectionIndex(sectionName,secii,secjj,varargin)
%       secInfo.secII: global i-subscripts for section nodes (f-point)
%              .secJJ: global j-subscripts for section nodes (f-point)
%                 .II: global i-subscript for every section point used for flux calculation
%                 .JJ: global j-subscript for every section point used for flux calculation
%              .uSign: sign for u-velocity for flux calculation [to convert vomecrty to be positive (left side --> right side of the section)]   
%              .vSign: sign for v-velocity for flux calculation [ .... vomecrty ....]
%            .uuIndex: index of u-points for flux calculation
%            .vvIndex: index of v-point for flux calculation
%                .NPT: number of points used for flux calculation
%         .ncStartInd: start index to extract sub-dataset
%           .ncIndCnt: the size of sub-dataset
%         .sectionE3t: layer thickness of each section cell, NZ x NPT array
%                 .E1: e1 of each section cell
%                 .E2: e2 of each section cell
%            .fluxLon: longitude along the section cells used for flux calculation
%            .fluxLat: latitude along the section cells used for flux calculation
%              .E2U2D: e2u on sub-dataset points
%              .E1V2D: e1v on sub-dataset points
%               .mask: (not used so far) 

if nargin<3
   help mkSectionIndex
   return
end

secIndexP='./secIndex/';
isUpdate=0;
while(size(varargin,2)>0)
   switch lower(varargin{1})
     case {'src','datasrc','rootp','datafolder','datap','secindexp'}
          secIndexP=varargin{2};
          varargin(1:2)=[];
     case {'ov','update','write','overwrite'}
          isUpdate=1;
          varargin(1)=[];
       otherwise
          disp(['unknow option: ',varargin{1}])
   end
end
secfile=[secIndexP,secName,'Index.mat'];
if ~exist(secfile,'file'), error(['section info file is not found! ',secfile]); end
eval(['load ',secfile]);

secInfo.secII=secII;
secInfo.secJJ=secJJ;

[secInfo.II,secInfo.JJ,secInfo.uSign,secInfo.vSign]=mkStair_F(secII,secJJ);
if ~isfield(secInfo,'ncmaskfile')
   secInfo.ncmaskfile='mask.nc';
end
if ~isfield(secInfo,'ncmaskfilez')
   secInfo.ncmaskfilez='mesh_zgr.nc'; 
end
if ~isfield(secInfo,'ncmaskfileh')
   secInfo.ncmaskfileh='mesh_hgr.nc'; 
end

if ~exist(secInfo.ncmaskfile,'file') || ~exist(secInfo.ncmaskfilez,'file') || ~exist(secInfo.ncmaskfileh,'file')
   conf = strtok(secName,'-') ;
   secInfo.ncmaskfile = [conf,'_mask.nc'] ;
   secInfo.ncmaskfilez = [conf,'_mesh_zgr.nc'] ;
   secInfo.ncmaskfileh = [conf,'_mesh_hgr.nc'] ;

   if ~exist(secInfo.ncmaskfile,'file') || ~exist(secInfo.ncmaskfilez,'file') || ~exist(secInfo.ncmaskfileh,'file')
    error(['I cannot found the mesh files !'])
   end
end

NX=GetNcDimLen(secInfo.ncmaskfile,'x');
NY=GetNcDimLen(secInfo.ncmaskfile,'y');
NZ=GetNcDimLen(secInfo.ncmaskfile,'z');
secInfo.locIndex=glo2locIndex(sub2ind([NY NX],secInfo.JJ,secInfo.II),NX,NY,secInfo.IIsub,secInfo.JJsub);
[secInfo.uuIndex,secInfo.vvIndex]=myGetUUVVIndexF(secInfo.uSign,secInfo.vSign,secInfo.II,secInfo.JJ,NX,NY,secInfo.IIsub,secInfo.JJsub);

secInfo.NPT=numel(secInfo.locIndex);
secInfo.ncStartInd=[secInfo.IIsub(1)-1 secInfo.JJsub(1)-1 0 0];
secInfo.ncIndCnt=[secInfo.IIsub(2)-secInfo.IIsub(1)+1 secInfo.JJsub(2)-secInfo.JJsub(1)+1 NZ 1];

% read e3t
[secInfo.sectionE3t,secInfo.sectionE3u,secInfo.sectionE3v]=myGetSectionE3TUV(secInfo);

% read e2 and e1
secInfo.E2U2D=GetNcSubDatasetXY(secInfo.ncmaskfileh,'e2u',secInfo.IIsub,secInfo.JJsub,NX,NY);
secInfo.E1V2D=GetNcSubDatasetXY(secInfo.ncmaskfileh,'e1v',secInfo.IIsub,secInfo.JJsub,NX,NY);

% mask (not used)
secInfo.mask=myGetSectionMask(secInfo,NX,NY,NZ);
% section infor (not used)
[secInfo.fluxLon,secInfo.fluxLat,secInfo.E1,secInfo.E2]=myGetSectionLonLat(secInfo,NX,NY,NZ);

if isUpdate==1
   eval(['save ',secIndexP,secName,'Index.mat secInfo']);
end
if nargout==0
   clear secInfo
end

function [iLogNew,jLogNew,uSign,vSign]=mkStair_F(iLog,jLog)
% return the i,j index of intermediate points between given nodes
%       uSign: the sign used to compute flux from left to right of this section using u-component (-1, 1 or 0)
%       vSign: the sign used to compute flux from left to right of this section using v-component (-1, 1 or 0)
% usage:
%       [iLogNew,jLogNew,uSign,vSign]=mkStair_F(iLog,jLog)
%  e.g.,
%       iLog=[5 10 15 10 5]; 
%       jLog=[10 15 10 5 10];
%       [iiNew,jjNew]=mkStair(iLog,jLog);
%       figure;
%       plot(iiNew,jjNew,'ko-');
%       hold on; 
%       hp=plot(iLog,jLog,'-s'); set(hp,'color',[0 0 0.4],'markersize',10,'linewidth',3);
%       axis equal;
%       xlim([4 17]);
%
% April 15, 2014: xianmin@ualberta.ca
% Aug    6, 2015:  modified for f-point, xianmin@ualberta.ca

if nargin~=2
   help mkStair_F
   return
end

[iLog,jLog]=mkStairSub(iLog,jLog); % simple interplation

np=numel(iLog);
iLogNew=iLog(1);
jLogNew=jLog(1);

for nn=2:np
    if iLog(nn)~=iLog(nn-1) && jLog(nn-1)~=jLog(nn)
        if (abs(iLog(nn-1)-iLog(nn))>=abs(jLog(nn)-jLog(nn-1)))
          if (jLog(nn-1)>jLog(nn))
             jj=jLog(nn-1):-1:jLog(nn);
          else
             jj=jLog(nn-1):jLog(nn);
          end
          tmpII=floor(interp1([jLog(nn-1) jLog(nn)],[iLog(nn-1) iLog(nn)],jj));
          iLogNew=[iLogNew iLog(nn-1) tmpII(2:end)]; %#ok<AGROW>
          jLogNew=[jLogNew jLog(nn) jj(2:end)]; %#ok<AGROW>
       else
          if iLog(nn-1)>iLog(nn)
             ii=iLog(nn-1):-1:iLog(nn);
          else
             ii=iLog(nn-1):iLog(nn);
          end
          tmpJJ=floor(interp1([iLog(nn-1) iLog(nn)],[jLog(nn-1) jLog(nn)],ii));
          iLogNew=[iLogNew iLog(nn) ii(2:end)]; %#ok<AGROW>
          jLogNew=[jLogNew jLog(nn-1) tmpJJ(2:end)]; %#ok<AGROW>
       end
    elseif (abs(iLog(nn-1)-iLog(nn))>1 || abs(jLog(nn)-jLog(nn-1))>1)
       error('I or J should be continous')
    else
       iLogNew=[iLogNew iLog(nn)]; %#ok<AGROW>
       jLogNew=[jLogNew jLog(nn)]; %#ok<AGROW>
    end
end

% get u- and v-sign
numP=numel(iLogNew);
uSign=zeros(1,numP);
vSign=uSign;
for np=2:numP
    if iLogNew(np)==iLogNew(np-1) && jLogNew(np-1)<jLogNew(np)
       %    ^  
       %   /|\
       %    |  
       %    |  
       uSign(np)=1;
    elseif iLogNew(np)==iLogNew(np-1) && jLogNew(np-1)>jLogNew(np)
       %    |  
       %    |  
       %   \|/ 
       %    v
       uSign(np)=-1;
    elseif jLogNew(np)==jLogNew(np-1) && iLogNew(np-1)<iLogNew(np)
       %   ------>
       vSign(np)=-1;
    elseif jLogNew(np)==jLogNew(np-1) && iLogNew(np-1)>iLogNew(np)
       %   <------
       vSign(np)=1;
    else
       disp(['i: ',num2str(iLogNew(np-1)),' -> ',num2str(iLogNew(np))])
       disp(['j: ',num2str(jLogNew(np-1)),' -> ',num2str(jLogNew(np))])
       error('should not see this errror')
    end
end

function [iLogNew,jLogNew]=mkStairSub(iLog,jLog)
np=numel(iLog);
iLogNew=iLog(1);
jLogNew=jLog(1);

for nd=2:np
    if abs(iLog(nd-1)-iLog(nd))==1 && abs(jLog(nd-1)-jLog(nd))==1
       iLogNew=[iLogNew iLog(nd)]; %#ok<AGROW>
       jLogNew=[jLogNew jLog(nd)]; %#ok<AGROW>
    elseif iLog(nd-1)==iLog(nd) && jLog(nd-1)==jLog(nd)
       continue
    elseif iLog(nd-1)==iLog(nd)
       if jLog(nd-1)>jLog(nd)
           jj=jLog(nd-1):-1:jLog(nd);
       else
           jj=jLog(nd-1):jLog(nd);
       end
       jLogNew=[jLogNew jj(2:end)]; %#ok<AGROW>
       iLogNew=[iLogNew jj(2:end)*0+iLog(nd)]; %#ok<AGROW>
    elseif jLog(nd-1)==jLog(nd)
       if iLog(nd-1)>iLog(nd)
           ii=iLog(nd-1):-1:iLog(nd);
       else
           ii=iLog(nd-1):iLog(nd);
       end
       jLogNew=[jLogNew ii(2:end)*0+jLog(nd)]; %#ok<AGROW>
       iLogNew=[iLogNew ii(2:end)]; %#ok<AGROW>
    else
       pp=polyfit(iLog(nd-1:nd),jLog(nd-1:nd),1);
       if abs(pp(1))>=1
           if iLog(nd)~=iLog(nd-1) && jLog(nd-1)~=jLog(nd)
               if jLog(nd-1)>jLog(nd)
                   jj=jLog(nd-1):-1:jLog(nd);
               else
                   jj=jLog(nd-1):jLog(nd);
               end
               tmpII=ceil(interp1([jLog(nd-1) jLog(nd)],[iLog(nd-1) iLog(nd)],jj));
               iLogNew=[iLogNew tmpII(2:end)]; %#ok<AGROW>
               jLogNew=[jLogNew jj(2:end)];    %#ok<AGROW>
           else
               iLogNew=[iLogNew iLog(nd)]; %#ok<AGROW>
               jLogNew=[jLogNew jLog(nd)]; %#ok<AGROW>
           end
       else
           if iLog(nd)~=iLog(nd-1) && jLog(nd-1)~=jLog(nd)
               if iLog(nd-1)>iLog(nd)
                   ii=iLog(nd-1):-1:iLog(nd);
               else
                   ii=iLog(nd-1):iLog(nd);
               end
               tmpJJ=ceil(interp1([iLog(nd-1) iLog(nd)],[jLog(nd-1) jLog(nd)],ii));
               iLogNew=[iLogNew ii(2:end)]; %#ok<AGROW>
               jLogNew=[jLogNew tmpJJ(2:end)]; %#ok<AGROW>
           else
               iLogNew=[iLogNew iLog(nd)]; %#ok<AGROW>
               jLogNew=[jLogNew jLog(nd)]; %#ok<AGROW>
           end
       end
    end
end

function [uuIndex,vvIndex]=myGetUUVVIndexF(uSign,vSign,iiSec,jjSec,NX,NY,iiLim,jjLim)
% f<--v--- vSign=1
indVPos=glo2locIndex(sub2ind([NY NX],jjSec,iiSec+1)  ,NX,NY,iiLim,jjLim);
% --v->f vSign=-1
indVNeg=glo2locIndex(sub2ind([NY NX],jjSec,iiSec)    ,NX,NY,iiLim,jjLim);
%   f
%   ^
%   |   uSign=1
%   u
%   |
indUPos=glo2locIndex(sub2ind([NY NX],jjSec,iiSec)    ,NX,NY,iiLim,jjLim);
%   |
%   u
%   |  uSign=-1
%   v
%   f
indUNeg=glo2locIndex(sub2ind([NY NX],jjSec+1,iiSec)    ,NX,NY,iiLim,jjLim);
uuIndex=indUPos; uuIndex(uSign<0)=indUNeg(uSign<0);
vvIndex=indVPos; vvIndex(vSign<0)=indVNeg(vSign<0);

function [myE3t,myE3u,myE3v]=myGetSectionE3TUV(secInfo)
% get the layer thickness (t,u,v-points) at given locations (local-index)
%secInfo.sectionE3t=myGetSectionE3t(secInfo.ncmaskfilez,secInfo.locIndex,secInfo.ncStartInd,secInfo.ncIndCnt,NZ);
% myE3t=myGetE3t(secInfo)
%      need secInfo.ncmaskfilez
%           secInfo.locIndex
%           secInfo.ncStartInd
%                  .ncIndCnt

if ~isfield(secInfo,'locIndex')
   error('no locIndex field in secInfo!')
end
locIndex=secInfo.locIndex;

if isfield(secInfo,'e3t0varname')
   cdep=secInfo.e3t0varname;
else
   cdep='e3t_1d'; 
end
if isfield(secInfo,'e3tpsvarname')
   ce3=secInfo.e3tpsvarname;
else
   ce3='e3t_ps';
end

if isfield(secInfo,'ncmaskfilez')
   meshfile=secInfo.ncmaskfilez;
else
   meshfile='mesh_zgr.nc';
end

if isfield(secInfo,'ncmaskfile')
   maskfile=secInfo.ncmaskfile;
else
   maskfile='mask.nc';
end

if ~exist(meshfile,'file')
   error([meshfile,' is not found!'])
end

NZ=GetNcDimLen(meshfile,'z');
NX=GetNcDimLen(meshfile,'x');
NY=GetNcDimLen(meshfile,'y');
subNX=secInfo.IIsub(2)-secInfo.IIsub(1)+1;
subNY=secInfo.JJsub(2)-secInfo.JJsub(1)+1;
is3dE3t=0;
%[~,e3DimLen]=GetNcVarDims(meshfile,cdep);

%if sum(e3DimLen>1)>1
%   is3dE3t=1;
%end
is3dE3t=0;

if is3dE3t==1
   startInd=e3DimLen*0;
   cntInd=startInd+1;
   startInd(e3DimLen==NX)=secInfo.IIsub(1)-1;
   startInd(e3DimLen==NY)=secInfo.JJsub(1)-1;
   cntInd(e3DimLen==NX)=subNX+1;
   cntInd(e3DimLen==NY)=subNY+1;
   cntInd(e3DimLen==NZ)=NZ;

   tmask=squeeze(GetNcVar(maskfile,'tmask',startInd,cntInd));
   my3dE3t=squeeze(GetNcVar(meshfile,cdep,startInd,cntInd));
   my3dE3u=zeros(NZ,subNX,subNY);
   my3dE3v=zeros(NZ,subNX,subNY);
   % my3dE3u
   for ni=1:subNX
       e3tOri=my3dE3t(:,:,ni);
       e3tRight=my3dE3t(:,:,ni+1);
       e3tOri(e3tRight< e3tOri)=e3tRight(e3tRight< e3tOri);
       my3dE3u(:,:,ni)=e3tOri(:,1:subNY,:);
   end
   % my3dE3v
   for nj=1:subNY
       e3tOri=my3dE3t(:,nj,:);
       e3tUpper=my3dE3t(:,nj+1,:);
       e3tOri(e3tUpper< e3tOri)=e3tUpper(e3tUpper< e3tOri);
       my3dE3v(:,nj,:)=e3tOri(:,:,1:subNX);
   end
   my3dE3t=my3dE3t(:,1:subNY,1:subNX);
   my3dE3t(tmask(:,1:subNY,1:subNX)==0)=0;
else
   e3t0=squeeze(GetNcVar(meshfile,cdep));
   %e3t0=squeeze(GetNcVar(meshfile,'e3t_0'));
   if numel(e3t0)~=NZ
      error('vertical levels does not match!')
   end
   [~,e3DimLen]=GetNcVarDims(meshfile,ce3);
   startInd=e3DimLen*0;
   cntInd=startInd+1;
   startInd(e3DimLen==NX)=secInfo.IIsub(1)-1;
   startInd(e3DimLen==NY)=secInfo.JJsub(1)-1;
   cntInd(e3DimLen==NX)=subNX+1;
   cntInd(e3DimLen==NY)=subNY+1;
   e3tps=squeeze(GetNcVar(meshfile,ce3,startInd,cntInd));

   [~,e3DimLen]=GetNcVarDims(meshfile,'mbathy');
   startInd=e3DimLen*0;
   cntInd=startInd+1;
   startInd(e3DimLen==NX)=secInfo.IIsub(1)-1;
   startInd(e3DimLen==NY)=secInfo.JJsub(1)-1;
   cntInd(e3DimLen==NX)=subNX+1;
   cntInd(e3DimLen==NY)=subNY+1;
   mbathy=GetNcVar(meshfile,'mbathy',startInd,cntInd);

   % compute 3D e3t, e3u, e3v
   tmpH=zeros(subNY+1,subNX+1);
   my3dE3t=zeros(NZ,subNY+1,subNX+1);
   my3dE3u=zeros(NZ,subNY,subNX);
   my3dE3v=zeros(NZ,subNY,subNX);
   for nl=1:NZ
       tmpH(:,:)=e3t0(nl);
       tmpH(mbathy==nl)=e3tps(mbathy==nl);    
       my3dE3t(nl,:,:)=tmpH;
   end
   % my3dE3u
   for ni=1:subNX
       e3tOri=my3dE3t(:,:,ni);
       e3tRight=my3dE3t(:,:,ni+1);
       e3tOri(e3tRight <e3tOri)=e3tRight(e3tRight< e3tOri);
       my3dE3u(:,:,ni)=e3tOri(:,1:subNY,:);
   end
   % my3dE3v
   for nj=1:subNY
      e3tOri=my3dE3t(:,nj,:);
      e3tUpper=my3dE3t(:,nj+1,:);
      e3tOri(e3tUpper< e3tOri)=e3tUpper(e3tUpper< e3tOri);
       my3dE3v(:,nj,:)=e3tOri(:,:,1:subNX);
   end
   my3dE3t=my3dE3t(:,1:subNY,1:subNX);
end
myE3t=zeros(NZ,numel(locIndex));
myE3u=zeros(NZ,numel(locIndex));
myE3v=zeros(NZ,numel(locIndex));
for nl=1:NZ
    e3ttab=squeeze(my3dE3t(nl,:,:));
    myE3t(nl,:)=e3ttab(locIndex) ;
    e3ttab=squeeze(my3dE3u(nl,:,:));
    myE3u(nl,:)=e3ttab(secInfo.uuIndex) ;
    e3ttab=squeeze(my3dE3v(nl,:,:));
    myE3v(nl,:)=e3ttab(secInfo.vvIndex) ;
end

function mymask=myGetSectionMask(secInfo,NX,NY,NZ)
% get the mask at given locations (local-index)
% usage:
%      mymask=myGetSectionMask(maskfile,locIndex,startInd,cntInd,maskvar)
if ~exist(secInfo.ncmaskfile,'file')
   error([secInfo.ncmaskfile,' is not found!'])
end

mymask=zeros(NZ,numel(secInfo.uSign));
vmask=GetNcSubDatasetXY(secInfo.ncmaskfile,'vmask',secInfo.IIsub, secInfo.JJsub,NX,NY);
umask=GetNcSubDatasetXY(secInfo.ncmaskfile,'umask',secInfo.IIsub, secInfo.JJsub,NX,NY);
for nz=1:NZ
    tmpUmask=squeeze(umask(nz,:,:));
    tmpVmask=squeeze(vmask(nz,:,:));
    tmpUmask=tmpUmask(secInfo.uuIndex);
    tmpVmask=tmpVmask(secInfo.vvIndex);
    tmpUmask(secInfo.uSign==0)=tmpVmask(secInfo.uSign==0);
    mymask(nz,:)=tmpUmask(:);
end

function [myLon,myLat,myE1,myE2]=myGetSectionLonLat(secInfo,NX,NY,NZ)
% get the lon,lat, e1 and e2 at locations for fluxes calculation
% usage:
%        [myLon,myLat,myE1,myE2]=myGetSectionLonLat(meshfile,uSign,vSign,iiSec,jjSec,NX,NY,NZ,iiLim,jjLim)
if ~exist(secInfo.ncmaskfileh,'file')
   error([secInfo.ncmaskfileh,' is not found!'])
end

myLon=zeros(1,numel(secInfo.uSign));
myLat=myLon;
myE1=myLon;
myE2=myLon;

% uSign==1
%    f
%    ^
%    |
%    u    umask(j,i)
%    |
indUPos=glo2locIndex(sub2ind([NY NX],secInfo.JJ,secInfo.II),NX,NY,secInfo.IIsub,secInfo.JJsub);
% uSign==-1
%    |
%    u    umask(j+1,i)
%    |
%   \ /
%    f
indUNeg=glo2locIndex(sub2ind([NY NX],secInfo.JJ+1,secInfo.II),NX,NY,secInfo.IIsub,secInfo.JJsub); %#ok<*NASGU>
% vSign==1
% f<--v---
%    |
% vmask(i+1,j)
indVPos=glo2locIndex(sub2ind([NY NX],secInfo.JJ,secInfo.II+1),NX,NY,secInfo.IIsub,secInfo.JJsub);
% vSign==-1
% ---v--->f
%    |
% vmask(i,j)
indVNeg=glo2locIndex(sub2ind([NY NX],secInfo.JJ,secInfo.II),NX,NY,secInfo.IIsub,secInfo.JJsub);

varList={'myLon','myLat','myE1','myE2'};
ncVarList={'glam','gphi','e1','e2'};

for nv=1:numel(varList);
    locVarV=GetNcSubDatasetXY(secInfo.ncmaskfileh,[ncVarList{nv},'v'],secInfo.IIsub,secInfo.JJsub,NX,NY);
    locVarU=GetNcSubDatasetXY(secInfo.ncmaskfileh,[ncVarList{nv},'u'],secInfo.IIsub,secInfo.JJsub,NX,NY);
    locVarT=GetNcSubDatasetXY(secInfo.ncmaskfileh,[ncVarList{nv},'t'],secInfo.IIsub,secInfo.JJsub,NX,NY);

    eval([varList{nv},'(1)=locVarT(indUNeg(1)-1);']);
    eval([varList{nv},'(secInfo.uSign==1)=locVarU(indUPos(secInfo.uSign==1));']);
    eval([varList{nv},'(secInfo.uSign==-1)=locVarU(indUNeg(secInfo.uSign==-1));']);
    eval([varList{nv},'(secInfo.vSign==1)=locVarV(indVPos(secInfo.vSign==1));']);
    eval([varList{nv},'(secInfo.vSign==-1)=locVarV(indVPos(secInfo.vSign==-1));']);
end
