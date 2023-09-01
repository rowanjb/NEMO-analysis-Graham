function getSectionFluxBatch(secName,caseTag,varargin)
% compute section fluxes from ANHA4 output in a batch mode
%dataP='/mnt/storage0/xhu/NEMO/ANHA4-EXH005/';
%dataP='/mnt/storage0/xhu/NEMO/ANHA4-EXH003B/';
%dataP='/mnt/storage3/xhu/NEMO/ANHA4-EXH001C/';
%dataP='/mnt/storage3/yarisbel/NEMO/ANHA4-EYG004-S/';

fnameP='/mnt/storage4/inge/matlab/';

if strcmp(caseTag,'ANHA4-EPM047')
  dataP='/mnt/storage5/laura/ANHA4/ANHA4-EPM047-S/'; flistFile=['./','flistname_1996-2014','.txt']
elseif strcmp(caseTag,'ANHA4-EPM048')
  dataP='/mnt/storage5/laura/ANHA4/ANHA4-EPM048-S/'; flistFile=['./','flistname_1996-2014','.txt']
elseif strcmp(caseTag,'ANHA4-EPM067')
  dataP='/mnt/storage4/laura/ANHA4/ANHA4-EPM067-S/'; flistFile=[fnameP,'flistname','.txt']
elseif strcmp(caseTag,'ANHA4-EPM068')
  dataP='/mnt/storage4/laura/ANHA4/ANHA4-EPM068-S/'; flistFile=[fnameP,'flistname','.txt']

%% Future Naturalized 
elseif strcmp(caseTag,'ANHA4-EPM032NB')
  dataP= '/mnt/storage5/yiran/ANHA4-EPM032NB-S/'; flistFile=['./','flistname_future','.txt']

elseif strcmp(caseTag,'ANHA4-EPM033NB')
  dataP= '/mnt/storage5/yiran/ANHA4-EPM033NB-S/'; flistFile=['./','flistname_future','.txt']

elseif strcmp(caseTag,'ANHA4-EPM042NB')
  dataP='/mnt/storage5/yiran/ANHA4-EPM042NB-S/'; flistFile=['./','flistname_future','.txt']

elseif strcmp(caseTag,'ANHA4-EPM052NB')
  dataP='/mnt/storage5/yiran/ANHA4-EPM052NB-S/'; flistFile=['./','flistname_future','.txt']

elseif strcmp(caseTag,'ANHA4-EPM053NB')
  dataP='/mnt/storage5/yiran/ANHA4-EPM053NB-S/'; flistFile=['./','flistname_future','.txt']


elseif strcmp(caseTag,'ANHA4-EPM071-S')
  dataP='/project/6007519/pmyers/ANHA4/ANHA4-EPM071-S/'; flistFile=['flistname','.txt']
  caseTag='ANHA4-EPM071';
elseif strcmp(caseTag,'ANHA4-EPM072')
  dataP='/project/6007519/pmyers/ANHA4/ANHA4-EPM072-S/'; flistFile=['flistname','.txt']

elseif strcmp(caseTag,'ANHA4-EPM073')
  dataP='/project/6007519/pmyers/ANHA4/ANHA4-EPM073-S/'; flistFile=['flistname','.txt']

elseif strcmp(caseTag,'ANHA4-EPM074')
  dataP='/project/6007519/pmyers/ANHA4/ANHA4-EPM074-S/'; flistFile=['flistname','.txt']

elseif strcmp(caseTag,'ANHA4-EPM075')
  dataP='/mnt/storage5/yiran/HBCrunoff/ANHA4-EPM075/'; flistFile=['./','flistname','.txt']

%% Historical naturalized


elseif strcmp(caseTag,'ANHA4-ELC042')
  dataP='/mnt/storage3/laura/ANHA4/ANHA4-ELC042-S/'; flistFile=['./','flistname_past','.txt']

elseif strcmp(caseTag,'ANHA4-ELC021')
  dataP='/mnt/storage5/laura/ANHA4/ANHA4-ELC021-S'; flistFile=['./','flistname_past','.txt']

elseif strcmp(caseTag,'ANHA4-ELC031')
  dataP='/mnt/storage5/laura/ANHA4/ANHA4-ELC031-S'; flistFile=['./','flistname_past','.txt']


%% Historical regulated
elseif strcmp(caseTag,'ANHA4-EPM061')
  dataP='/project/6007519/pmyers/ANHA4/ANHA4-EPM061-S/'; flistFile=['flistname_2005','.txt']

elseif strcmp(caseTag,'ANHA4-EPM062')
  dataP='/project/6007519/pmyers/ANHA4/ANHA4-EPM062-S/'; flistFile=['flistname_2005','.txt']

elseif strcmp(caseTag,'ANHA4-EPM063')
  dataP='/project/6007519/pmyers/ANHA4/ANHA4-EPM063-S/'; flistFile=['flistname_2005','.txt']
elseif strcmp(caseTag,'ANHA4-EPM101')
  dataP='/project/6007519/pmyers/ANHA4/ANHA4-EPM101-S/'; flistFile=['flistname_2005','.txt']
elseif strcmp(caseTag,'ANHA4-EPM102')
  dataP='/project/6007519/pmyers/ANHA4/ANHA4-EPM102-S/'; flistFile=['flistname_2005','.txt']

elseif strcmp(caseTag,'ANHA4-EPM151')
  dataP='/project/6007519/pmyers/ANHA4/ANHA4-EPM151-S/'; flistFile=['flistname_EPM151','.txt']
elseif strcmp(caseTag,'ANHA4-EPM152')
  dataP='/project/6007519/pmyers/ANHA4/ANHA4-EPM152-S/'; flistFile=['flistname_EPM152','.txt']
elseif strcmp(caseTag,'ANHA4-EPM155')
  dataP='/project/6007519/pmyers/ANHA4/ANHA4-EPM155-S/'; flistFile=['flistname_EPM155','.txt']
elseif strcmp(caseTag,'ANHA4-EPM156')
  dataP='/project/6007519/pmyers/ANHA4/ANHA4-EPM156-S/'; flistFile=['flistname_EPM156','.txt']
elseif strcmp(caseTag,'ANHA4-EPM157')
  dataP='/project/6007519/pmyers/ANHA4/ANHA4-EPM157-S/'; flistFile=['flistname_EPM157','.txt']
elseif strcmp(caseTag,'ANHA4-EPM158')
  dataP='/project/6007519/pmyers/ANHA4/ANHA4-EPM158-S/'; flistFile=['flistname_EPM158','.txt']

else

disp('Model run not included in script')
return
end

isFuture = 0 ;
isExit = 0 ;

saveP='./matfile/';
%CF='1_ANHA4-ECP004';
caseTagStr=strrep(caseTag,'-','_');
%secResult=[caseTagStr,'_',secName,'_',timeTag,'_TSUV'];

while(size(varargin,2)>0)
  switch lower(varargin{1})
    case {'future','-f'}
      isFuture = 1 ;
      varargin(1)=[];
    case {'exit','quit','stop'}
      isExit=1;
      varargin(1)=[];
    case {'savep','matfile','save'}
      saveP=varargin{2};
      varargin(1:2)=[];  
    otherwise
      error('I do not understand one of the given options')
  end
end

%if isFuture == 1
%  flistFile=['./','flistname_','.txt'];
%else
%  flistFile=['./','flistname','.txt']
%end

timeTag=textread(flistFile,'%s') ;

myVol=zeros(size(timeTag));
myHeat=zeros(size(timeTag));
mySalt=zeros(size(timeTag));
myFW=zeros(size(timeTag));

n=0;
for ii=1:size(timeTag,1)
  if mod(ii,300)==1
    sprintf('Yes I am alive, current working file: %s',timeTag{ii})
  end
  %[secVol,secHeat,secSalt]=getSectionFlux(secName,caseTag{ii},'dataP',['./',caseTag,'/'],timeTag{ii},'saveP',saveP);
  [secVol,secHeat,secSalt,secFW]=getSectionFlux1(secName,timeTag{ii},'dataP',dataP,'saveP',saveP,'cf',caseTag,'update');
  %[secVol,secHeat,secSalt,secFW,secIce]=getSectionFlux(secName,timeTag{ii},'dataP',['./',caseTag,'/'],'saveP',saveP,'cf',caseTag,'update');
  %secResult=[caseTagStr,'_',secName,'_',timeTag{ii},'_TSUV'];
  %eval(['load ',saveP,secResult,'.mat '])
  %sprintf(['I OPENED',saveP,secResult,'.mat for this date and section'])
  
  %eval(['secVol=', secResult1,'.secVolFlux ;'])
  %eval(['secHeat=', secResult1,'.secHeatFlux ;'])
  %eval(['secSalt=', secResult1,'.secSaltFlux ;'])
  %eval(['secFW=', secResult1,'.secFWFlux ;'])

  myVol(ii)=nansum(secVol(:));
  myHeat(ii)=nansum(secHeat(:));
  mySalt(ii)=nansum(secSalt(:));
  myFW(ii)=nansum(secFW(:));
  %myIce(ii)=nansum(myIce(:));
end
npt=size(timeTag,1);
myVol=myVol(1:npt);
mySalt=mySalt(1:npt);
myHeat=myHeat(1:npt);
myFW=myFW(1:npt);
%myIceFW=myIce(1:npt);


secName=strsplit(secName,'-') ;
if ~exist(['./secFlux/',caseTag,'/']); mkdir(['./secFlux/',caseTag,'/']); end
matdir=['./secFlux/',caseTag,'/',secName{1},'_',caseTag,'_',num2str(timeTag{1}(2:5)),'_',num2str(timeTag{end}(2:5)),'.mat'];
eval(['save ',matdir,' myVol myHeat mySalt myFW timeTag'])

if isExit == 1
  exit
end

