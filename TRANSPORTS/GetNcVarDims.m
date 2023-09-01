function [nDims,dimLen]=GetNcVarDims(ncFileName,ncVarName)
% return the dimension number of a variable in a ncfile
% usage:
%       nDims=GetNcVarDims(Netcdf-filename,netcdf-varname)
%  xianmin@ualberta.ca (redistribution with permission only)

if ~exist(ncFileName,'file')
   error([ncFileName,' is not found!']);
end

ncfid=netcdf.open(ncFileName,'NC_NOWRITE');
varID=netcdf.inqVarID(ncfid,ncVarName);
[varname,vartype,vardimids,numAtts]=netcdf.inqVar(ncfid,varID);
dimLen=zeros(size(vardimids));

for n=1:numel(vardimids)
    [~,dimLen(n)]=netcdf.inqDim(ncfid,vardimids(n));
end
netcdf.close(ncfid);
nDims=numel(vardimids);
if nargout==1
   clear dimLen
end
