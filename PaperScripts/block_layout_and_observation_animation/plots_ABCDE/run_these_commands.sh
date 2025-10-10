python3 ../plot_all_times.py ../../../Astrometry/ABCDE_blocks/ -pa -l 47 62 -3.5 +5.5
python3 ../plot_all_times.py ../../../Astrometry/ABCDE_blocks/ -pa -l 47 62 -3.5 +5.5 -sd 2020-01-01 -dr 670 -a
python3 ../plot_all_times.py ../../../Astrometry/ABCDE_blocks/ -pa -l 47 62 -3.5 +5.5 -sd 2021-12-01 -dr 670 -a
python3 ../plot_all_times.py ../../../Astrometry/ABCDE_blocks/ -pa -l 47 62 -3.5 +5.5 -sd 2023-10-02 -dr 670 -a
cd plot_disc
bash make_abg.sh
bash make_PH2.sh
python3 ../../plot_all_times.py -d . ../all.list
cd ..
