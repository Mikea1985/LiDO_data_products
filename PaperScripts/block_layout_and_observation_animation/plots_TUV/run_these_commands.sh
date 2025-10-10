python3 ../plot_all_times.py ../../../Astrometry/TUV_blocks/ -pa -l 237 252 -8.25 +0.75
python3 ../plot_all_times.py ../../../Astrometry/TUV_blocks/ -pa -l 237 252 -8.25 +0.75 -sd 2020-01-01 -dr 670 -a
python3 ../plot_all_times.py ../../../Astrometry/TUV_blocks/ -pa -l 237 252 -8.25 +0.75 -sd 2021-12-01 -dr 670 -a
python3 ../plot_all_times.py ../../../Astrometry/TUV_blocks/ -pa -l 237 252 -8.25 +0.75 -sd 2023-10-02 -dr 670 -a
cd plot_disc
bash make_abg.sh
bash make_PH2.sh
python3 ../../plot_all_times.py -d . ../all.list
cd ..
