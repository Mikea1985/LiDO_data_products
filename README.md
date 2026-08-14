# LiDO_data_products

If you have reached this page through a DOI link,
please note that the DOI represents a snapshot of
https://github.com/Mikea1985/LiDO_data_products
at the time of publication.
Please visit the github repository for the most up-to-date version.

This repository is intended to be a central place to collect all of the 
data products from the LiDO survey. 

Structure:

    Astrometry/             - Contains all the astrometry from the survey.
        TUV_blocks/         - Astrometry from spring semester
        ABCDE_blocks/       - Astrometry from fall semester
              *.ast         - All astrometry (including rejected/unmeasured images) 
                              in the extended format used by the tracking software.
              *.obs         - Good astrometry in the MPC 80-character format. 
                              Generally you'll want the .obs or .psv file.
              *.psv         - Good astrometry in the ADES Pipe Separated Values
                              format. Generally you'll want the .psv or .obs file.
              *.obs_dmag    - same as .obs, but with magnitude measurements only
                              on the discovery observations. Used by some scripts.
    Characterization/       - Contains the survey characterization files needed
                              to run the survey simulator.
        pointings.list      - Survey description file. 
                              For each block/field, has a definition of the shape,
                              epoch of discovery, filling factor, observatory code,
                              and the name of which .eff file applies.
        *.eff               - Efficiency parameter file.
                              Defines rate cuts, angle cuts, filter, as well as 
                              parametrization of the magnitude error distribution, 
                              photometric fraction, tracking fraction, and
                              detection efficiency. 
        README.formats      - An explanation of the formats used.
    Logo/                   - Contains the LiDO survey logo.
        *.png               - PNG versions in various colour combinations.
        *.svg               - Vector graphics version in a single colour scheme.
        logo_definition.txt - A descriptive definition of the LiDO logo,
                              as well as the hex keys for the three LiDO colours.
                              These colours should be used for talk slides and posters.
    Orbits/                 - Contains the orbits for all the objects
        correspondence.txt  - List of IDs and designations that belong to the
                              same object. This connects LiDO IDs (occasionally two
                              for objects seen in two fields) with MPC designations
                              and IAU numbers.
        elements_header.txt - Contains an explanation of each column in the
                                elements files.
        LiDO_ABCDE.detections - Elements for the fall objects (ABCDE blocks)
        LiDO_TUV.detections   - Elements for the spring objects (TUV blocks)
        mixed_mode_resonances.txt - A list of the mixed mode resonance objects,
                                    as the .detections file format does not have room
                                    for these parameters.
        notes_not_res.txt   - Additional notes about all objects (resonant or not).
        notes_res.txt       - Additional notes specifically about resonant objects.
    PaperProducts/          - Contains figures and tables created for the survey paper.
    PaperScripts/           - Contains scripts for recreating some of the tables and figures,
                              as well as scripts for converting and correcting astrometry formats.
