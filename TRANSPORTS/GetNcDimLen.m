function dimLen=GetNcDimLen(ncfile,dimName)
% return the dimension length in a netcdf file
% usage:
%       dimLen=GetNcDimLen(ncfile,dimName)
% e.g.,
%       nx=GetNcDimLen('mask.nc','x');
%  xianmin@ualberta.ca (redistribution with permission only)

if nargin~=2
   help GetNcDimLen
   error('Need two input')
end

if ~exist(ncfile,'file')
   error([ncfile,' is not found!'])
end

ncfid=netcdf.open(ncfile,'NC_NOWRITE');
idDim=netcdf.inqDimID(ncfid,dimName); 
if idDim<0
   netcdf.close(ncfid);
   error(['dimension: ',dimName,' is not found!'])
else
   [~,dimLen]=netcdf.inqDim(ncfid,idDim);
   netcdf.close(ncfid);
end
