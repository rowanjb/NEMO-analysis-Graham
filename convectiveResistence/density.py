import numpy as np

def density(S,T):
    """Calculates density at atmospheric pressure.
    From on "Algorithms for Computation of Fundamental Properties of Seawater", 1983, pg. 17.
    
    Based on .m files from:
    https://github.com/kerfoot/spt/blob/master/seawater_ver3_3/sw_dens0.m 
    https://github.com/pgaube/matlab/blob/master/general/sw_smow.m"""

    #part 1; density of reference pure seawater

    a0 = 999.842594
    a1 =   6.793952e-2
    a2 =  -9.095290e-3
    a3 =   1.001685e-4
    a4 =  -1.120083e-6
    a5 =   6.536332e-9

    T68 = np.multiply(T, 1.00024) #uses IPTS-68 instead of ITS-90, etc.
    T68_2 = np.power(T68,2)
    T68_3 = np.power(T68,3)
    T68_4 = np.power(T68,4)
    T68_5 = np.power(T68,5)

    term1 = a0
    term2 = np.multiply(a1,T68)
    term3 = np.multiply(a2,T68_2)
    term4 = np.multiply(a3,T68_3)
    term5 = np.multiply(a4,T68_4)
    term6 = np.multiply(a5,T68_5)

    #density of reference pure seawater
    SMOW = np.add(term1,np.add(term2,np.add(term3,np.add(term4,np.add(term5,term6)))))

    #part 2; potential density based on salinity and temperature

    b0 =  8.24493e-1
    b1 = -4.0899e-3
    b2 =  7.6438e-5
    b3 = -8.2467e-7
    b4 =  5.3875e-9

    c0 = -5.72466e-3
    c1 = +1.0227e-4
    c2 = -1.6546e-6

    d0 = 4.8314e-4

    term1 = SMOW

    termB1 = b0
    termB2 = np.multiply(b1,T68)
    termB3 = np.multiply(b2,T68_2)
    termB4 = np.multiply(b3,T68_3)
    termB5 = np.multiply(b4,T68_4)
    term2 = np.multiply(S,np.add(termB1,np.add(termB2,np.add(termB3,np.add(termB4,termB5)))))

    termC1 = c0
    termC2 = np.multiply(c1,T68)
    termC3 = np.multiply(c2,T68_2)
    term3 = np.multiply(np.power(S,1.5),np.add(termC1,np.add(termC2,termC3)))

    term4 = np.multiply(d0,np.power(S,2))

    rho = np.add(term1,np.add(term2,np.add(term3,term4)))

    return rho