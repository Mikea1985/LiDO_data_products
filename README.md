# LiDO_data_products
This repository is intended to be a central place to collect all of the 
data products from the LiDO survey. 

Structure:
LiDO_data_products/
    Astrometry/        - Contains all the astrometry from the survey.
        TUV_blocks/    - Astrometry from spring (A) semester
        ABCDE_blocks/  - Astrometry from fall (B) semester
              *.ast    - All astrometry (including rejected/unmeasured images) 
                         in the extended format used by the tracking software.
              *.obs    - Good astrometry in the MPC 80-character format. 
                         Generally you'll want the .obs file.
    Orbits/                 - Contains the orbits for all the objects
        elements_ABCDE.txt  - Elements for the fall objects (ABCDE blocks)
        elements_TUV.txt    - Elements for the spring objects (TUV blocks)
        elements_header.txt - Contains an explanation of each column in the
                              elements files.
    Characterization/   - Contains the survey characterization files needed
                          to run the survey simulator.
        pointings.list  - Survey description file. 
                          For each block/field, has a definition of the shape,
                          epoch of discovery, filling factor, observatory code,
                          and the name of which .eff file applies.
        *.eff           - Efficiency parameter file.
                          Defines rate cuts, angle cuts, filter, as well as 
                          parametrization of the magnitude error distribution, 
                          photometric fraction, tracking fraction, and
                          detection efficiency. 
