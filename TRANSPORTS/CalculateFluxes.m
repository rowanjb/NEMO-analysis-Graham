% get fluxes across sections
%1 define gates by using drawLonLatSectionProj
%2 run getSectionFluxBatch??


gate={'ANHA4_LC2kDepth'}; %'ANHA4_LabSea2kDepth' 'ANHA4_LC2kDepth' 'ANHA4_WGC2kDepth' 'ANHA4_LSsouth'

configEXP={'ANHA4-EPM155'};

for c=1:length(configEXP)
    for n=1:length(gate) % gate
      
        getSectionFluxBatch(gate{n},configEXP{c})
        
    end
end
return 

