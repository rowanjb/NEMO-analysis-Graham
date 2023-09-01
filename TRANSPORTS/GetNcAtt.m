function A=GetNcAtt(FileName,VarName,AttName)
% function to extract a given attribute of a variable from a given nc file
% Usage: A=GetNcAtt('file.nc','A','Units')
% See also:    GetNcVar, ShowNcAtt
%  xianmin@ualberta.ca (redistribution with permission only)

if ~exist(FileName,'file')
    error([FileName,' can''t be found!!!']);
end

matVer=version('-release');
matVer=str2num(matVer(1:4));
if matVer>=2008
   A=myGetNcAtt(FileName,VarName,AttName);
   return
end
ncfid=netcdf(FileName,'nowrite');
if isempty(ncfid) error(['# Error in openning ',FileName]); end

ncvar=var(ncfid);
for n=1:length(ncvar)
    if (strcmp(name(ncvar{n}),VarName))
        TempAtt=att(ncvar{n});
        for Natt=1:length(TempAtt)
            if (strcmp(name(TempAtt{Natt}),AttName))
                eval(['A=TempAtt{',num2str(Natt),'}(:);']);
                return;                
            end
        end
        if exist('A','var')~=1 
            disp([AttName,' of ', VarName,' in ',FileName,' cann''t been found!']);
            A='';
        end
    end
end
close(ncfid);

function myAtt=myGetNcAtt(FileName,VarName,AttName);
ncfid=netcdf.open(FileName,'NC_NOWRITE');
isGlobal=0;
switch VarName
    case {'global','g','gatt'}
       isGlobal=1;
    otherwise
       % do nothing
end

myAtt='';
if isGlobal==0
   varID=netcdf.inqVarID(ncfid,VarName);
   if varID<0
      error([VarName,' does not exist'])
   end
   [myNcName,xtype,myDims,numAtt] = netcdf.inqVar(ncfid,varID);
   for numA=0:numAtt-1
       tmpAttName=netcdf.inqAttName(ncfid,varID,numA);
       if strcmpi(tmpAttName,AttName)
          myAtt=netcdf.getAtt(ncfid,varID,tmpAttName);
          netcdf.close(ncfid);
          return
       end
   end
else
  attID=netcdf.inqAttID(ncfid,netcdf.getConstant('NC_GLOBAL'),AttName);
  if attID>=0
     myAtt=netcdf.getAtt(ncfid,netcdf.getConstant('NC_GLOBAL'),AttName);
     netcdf.close(ncfid);
     return
  end
end
netcdf.close(ncfid);
return
