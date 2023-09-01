function mydata=GetNcVar(ncFileName,ncVarName,startIndex,cnt,isPermute,isDouble)
% read a given variable from a netcdf file
% usage:
%       myData=GetNcVar(Netcdf-filename,netcdf-varname [,startIndex,cnt,isPermute,isDouble])
% Jan 2011: xianmin@ualberta.ca (redistribution with permission only)
% Aug 2015: add isCDFTOOLS to deal with nc file compressed by cdf16bit
% Sep 2016: add isDouble option to disable data type conversion

if ~exist(ncFileName,'file')
	   error([ncFileName,' is not found!']);
   end

   if nargin<6
	      isDouble=1;
      end

      ncfid=netcdf.open(ncFileName,'NC_NOWRITE');
      varID=netcdf.inqVarID(ncfid,ncVarName);
      [varname,vartype,vardimids,numAtts]=netcdf.inqVar(ncfid,varID);

      myScale=1; myOffSet=0;
      isCDFTOOLS=0;

      for numA=1:numAtts
	  tmpattname=netcdf.inqAttName(ncfid,varID,numA-1);
	  switch lower(tmpattname)
	         case {'scale_factor','scalefactor'}
	              myScale=netcdf.getAtt(ncfid,varID,tmpattname);
	         case {'add_offset','off_set','offset','offset_value'}
	              myOffSet=netcdf.getAtt(ncfid,varID,tmpattname);
	         case {'savelog10'}
	              isCDFTOOLS=1;
	         otherwise
	              % do nothing
          end
      end
      if nargin>=4
         if nargin==4, isPermute=1; end
         mydata=netcdf.getVar(ncfid,varID,startIndex,cnt);
         if ischar(isPermute)
            switch lower(isPermute)
            case {'nopermute','origin','xy','xyz','xyzt'}
                isPermute=0;
            otherwise
                disp(['unknown option: ',isPermute])
                isPermute=1;
            end
         end
     else
         isPermute=1;
         mydata=netcdf.getVar(ncfid,varID);
         if nargin==3
            switch lower(startIndex)
            case {'nopermute','origin','xy','xyz','xyzt'}
                isPermute=0;
            otherwise
                disp('unknown option: ')
                startIndex
            end
         end
      end
      netcdf.close(ncfid);
      if ~ischar(mydata)
       % rescale data if necessary
        if isPermute==1
           mydata=permute(mydata,length(size(mydata)):-1:1);
        end
        if isDouble==1
           mydata=double(double(mydata)*myScale+myOffSet);
        else
           mydata=mydata*myScale+myOffSet;
        end
        %to deal with nc file compressed by cdf16bit xhu, Aug 2015
        if isCDFTOOLS==1 && (myScale~=1 || myOffSet ~=0)
           mydata(mydata==myOffSet)=0;
        end
    end

