function mySubDataset=GetNcSubDatasetXY(ncfile,ncVarName,IIsub,JJsub,NX,NY)
% extract a sub-dataset (in x, y) of a variable in nc file
% usage:
%       subDataSet=GetNcSubDatasetXY(ncfile,ncVarName,IIsub,JJsub,NX,NY)
%           IIsub: [i-start i-end];
%           JJsub: [j-start j-end];
%              NX: i-dimension in whole dataset
%              NY: j-dimension in whole dataset
%  Note:
%        NX and NY should be different, and not equal to other dimensions
%  xianmin@ualberta.ca (redistribution with permission only)

if ~exist(ncfile,'file')
   error([ncfile,' is not found!']);
end

ncfid=netcdf.open(ncfile,'NC_NOWRITE');
varID=netcdf.inqVarID(ncfid,ncVarName);
[~,~,vardimids,~]=netcdf.inqVar(ncfid,varID);
if varID<0
   error([ncVarName,' is not found in ',ncfile])
end

myVarDimLen=zeros(size(vardimids));
for n=1:numel(vardimids)
    [~,myVarDimLen(n)]=netcdf.inqDim(ncfid,vardimids(n));
end
netcdf.close(ncfid);

startInd=myVarDimLen*0;
cntInd=myVarDimLen;
startInd(myVarDimLen==NX)=IIsub(1)-1;
startInd(myVarDimLen==NY)=JJsub(1)-1;
cntInd(myVarDimLen==NX)=IIsub(2)-IIsub(1)+1;
cntInd(myVarDimLen==NY)=JJsub(2)-JJsub(1)+1;
mySubDataset=squeeze(GetNcVar(ncfile,ncVarName,startInd,cntInd));
