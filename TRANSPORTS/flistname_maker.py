#generates flistname text files with fill lists of output dates for different runs
#empty or otherwise corrupted output files should hopefully be not included

import numpy as np

def flistMaker(run): 

    #text file of paths to non-empty model output
    gridT_txt = '/home/rowan/projects/rrg-pmyers-ad/rowan/NEMO-analysis-Graham/' + run + '_filepaths/' + run + '_gridT_filepaths.txt'

    #open the text files and get lists of the .nc output filepaths
    with open(gridT_txt) as f: lines = f.readlines()
    filepaths_gridT = [line.strip() for line in lines]

    filepaths_gridT = [filepath[-20:-9] for filepath in filepaths_gridT]


    np.savetxt('flistname_' + run + '.txt', filepaths_gridT, fmt='%s', delimiter="\n")


if __name__ == "__main__":
    flistMaker('EPM151')
    flistMaker('EPM152')
    flistMaker('EPM155')
    flistMaker('EPM156')
    flistMaker('EPM157')
    flistMaker('EPM158')
