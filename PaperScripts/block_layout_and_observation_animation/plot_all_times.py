#!/home/malexand/.anaconda3/envs/lidoconda3/bin/python3

import sys
import argparse
import subprocess as sp
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from time import sleep
from matplotlib import gridspec
from pathlib import Path
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import SkyCoord
from matplotlib.patches import Ellipse, Polygon, Circle
from typing import Union, List, Dict, Optional, Tuple


PH2_HEADER = """


<?xml version = "1.0"?>
<!DOCTYPE ASTRO SYSTEM "http://vizier.u-strasbg.fr/xml/astrores.dtd">
<ASTRO ID="v0.8" xmlns:ASTRO="http://vizier.u-strasbg.fr/doc/astrores.htx">
  <TABLE ID="Table">
    <NAME>Fixed Targets</NAME>
    <TITLE>Fixed Targets for CFHT QSO</TITLE>
    <!-- Definition of each field -->
    <FIELD name="NAME" datatype="A" width="20">
        <DESCRIPTION>Name of target</DESCRIPTION>
    </FIELD>
    <FIELD name="RA"    datatype="A" width="11" unit="h"   format="RAh:RAm:RAs">
        <DESCRIPTION>Right ascension of target</DESCRIPTION>
    </FIELD>
    <FIELD name="DEC"   datatype="A" width="11" unit="deg" format="DEd:DEm:DEs">
        <DESCRIPTION>Declination of target</DESCRIPTION>
    </FIELD>
    <FIELD name="EPOCH" datatype="F" width="6">
        <DESCRIPTION>Epoch of coordinates</DESCRIPTION>
    </FIELD>
    <FIELD name="POINT" datatype="A" width="5">
        <DESCRIPTION>Pointing name</DESCRIPTION>
    </FIELD>
        <!-- Data table -->
<DATA><CSV headlines="4" colsep="|">
<![CDATA[
NAME                |RA         |DEC        |EPOCH |POINT|
                    |hh:mm:ss.ss|+dd:mm:ss.s|      |     |
12345678901234567890|12345678901|12345678901|123456|12345|
--------------------|-----------|-----------|------|-----|
"""


def clean_ast_list_and_get_times_and_expnos(ast_dir: str,
                                            object_list: List[str]
                                            ) -> Dict[str, List[str]]:
    times = {}
    with open("ast.all", "w", encoding='ascii') as ast_all, open("ast.det", "w", encoding="ascii") as ast_det:
        for obj in object_list:
            with open(f"{ast_dir}/{obj}.ast", 'r', encoding='ascii') as ast_file:
                ast_lines = ast_file.readlines()
            with open(f"{obj}.o568", 'w', encoding='ascii') as obs_file:
                for line in ast_lines:
                    if line[0] != '!':
                        clean_ast = f'     {obj:7}' + line[12:]
                        ast_all.write(clean_ast)
                        if line[12] in ["*", "&"]:
                            ast_det.write(clean_ast)
                        clean_line = f'     {obj:7}' + line[12:77].replace('&', ' ') + '568\n'
                        if ("0109A01" in clean_line and "C2014" in clean_line):
                            # For some reason, including these perfectly good observations break fit_radec
                            # For 0109A01 it's likely because the arc becomes too long for a nearby object.
                            pass
                        if ("4A12E12" in clean_line and "C2022 03" in clean_line):
                            # For some reason, including these perfectly good observations break fit_radec
                            # For 4A12E12 I think it is because the object was observed very far from opposition.
                            pass
                        else:
                            obs_file.write(clean_line)
                        time = clean_line[15:25]
                        expno = line[82:95].split('p')[0].strip()
                        if time not in times:
                            times[time] = [expno]
                        else:
                            times[time].append(expno)
    return times


def ast2abg_aei_pred(dates: Union[str, List[str]],
                     object_list: List[str]) -> None:
    """
    Take observations and convert them to abg, aei and prediction
    information.
    """
    if isinstance(dates, str):
        dates = [dates]
    for obj in object_list:
        print(f"fit_radec < {obj}")
        sp.run(f'fit_radec < {obj}.o568 > {obj}.abg', shell=True)
        print(f"abg_to_aei {obj}")
        sp.run(f'abg_to_aei < {obj}.abg > {obj}.aei', shell=True)
    for date in dates:
        for obj in object_list:
            print(f"predict {obj} {date}")
            with open(f"{obj}.pred", 'w', encoding='ascii') as p_out:
                sp.run(['predict', f"{obj}.abg"],
                       input=f"568\n{date}\n".encode(),
                       stdout=p_out, check=True)
        abgaeipred2meta(object_list, date=date.replace(' ', '') + '.3877')


def abgaeipred2meta(object_list: List[str],
                    date: Optional[str] = None) -> None:
    outfile = 'abgaeipred.all' if not date else f'abgaeipred_{date.replace(' ', '')}.all'
    with open(outfile, 'w', encoding='ascii') as f_out:
        for obj in object_list:
            sp.run(f'echo "{obj}" `grep -o " at epoch .*$" {obj}.aei`', stdout=f_out, shell=True)
            sp.run(f'head -n 6 {obj}.aei | tail -n 2', stdout=f_out, shell=True)
            sp.run(f"grep Barycentric {obj}.abg | sed 's/#//'", stdout=f_out, shell=True)
            print(get_and_fix_predline(obj), file=f_out, flush=True)
            print("#", file=f_out, flush=True)
        sp.run(r'sed -i "/distance .\./s/distance /distance  /g" ' + outfile, shell=True)


def get_and_fix_predline(obj: str) -> str:
    predline = Path(f"{obj}.pred").read_text().splitlines()[-1]
    if len(predline) > 74:
        split_line = predline.split()
        sra = float(split_line[4])
        sdec = float(split_line[5])
        ang = float(split_line[6])
        rap = 9 - len(str(int(sra)))
        decp = 9 - len(str(int(sdec)))
        print(rap, decp)
        ras = f"{sra:10.{max([rap, 0])}f}"
        decs = f"{sdec:10.{max([decp, 0])}f}"
        print(predline)
        return f"{predline[:44]} {ras[:10]} {decs[:10]} {ang:>7}"
    return predline


def get_list_of_observed_dates(object_list: List[str]) -> List[str]:
    times = []
    for obj in object_list:
        with open(f"{obj}.o568", 'r', encoding='ascii') as o_in:
            for line in o_in:
                if line[15:25] not in times:
                    times.append(line[15:25])
    return times


def make_PH2_files(times: Dict[str, List[str]]) -> None:
    """On each day, make a PH2 file with the coordinates used."""
    from astroquery.cadc import Cadc
    cadc = Cadc()
    for time, expnos in times.items():
        print(f"Getting information for time={time}")
        with open(f"PH2_{time.replace(' ', '')}.xml", "w") as ph2:
            ph2.write(PH2_HEADER)
            for expno in expnos:
                print(f"Getting RA, Dec for {expno}")
                query = (f"SELECT obs_id, target_name, s_ra, s_dec, instrument_name, calib_level "
                         f"FROM ivoa.ObsCore "
                         f"WHERE instrument_name='MegaPrime' "
                         f"AND obs_id='{expno}' "
                         f"ORDER BY calib_level DESC")
                results = cadc.exec_sync(query)
                try:
                    ra = results[0]['s_ra']
                    dec = results[0]['s_dec']
                    coord = SkyCoord(ra=ra * u.degree, dec=dec * u.degree, frame='icrs')
                    ra_hex = coord.ra.to_string(u.hourangle, sep=":", precision=2, pad=True)
                    dec_hex = coord.dec.to_string(u.degree, sep=":", precision=1,
                                                  pad=True, alwayssign=True)
                    ph2.write(f"{expno:<20}|{ra_hex}|{dec_hex}|2000.0|1    |\n")
                except IndexError:
                    print(f"Could not find expno={expno} at {time}")
            ph2.write("]]></CSV></DATA>\n  </TABLE>\n</ASTRO>")


def main(ast_dir: str, object_list: List[str],
         limits: List[float],
         # Old shoddy argument handling in a single string; can't be bothered to improve.
         what: str = 'skyfownoshowsavedatecold',
         plot_astrometry: bool = False,
         date_start_and_range: Optional[Tuple[str, int]] = None,  # ("2020-01-01", 2000),
         make_PH2_and_o568_files: bool = False,
         convert_ast2abgaeipred: bool = False
         ) -> None:
    if make_PH2_and_o568_files or not list(Path('.').glob('PH2*.xml')) or not list(Path('.').glob('*.o568')):
        times = clean_ast_list_and_get_times_and_expnos(ast_dir, object_list)
        make_PH2_files(times)
        dates = list(times.keys())
    elif date_start_and_range:
        dates = []
        for i in np.arange(date_start_and_range[1]):
            date = Time(date_start_and_range[0]) + i
            dates.append(f"{date.ymdhms.year} {date.ymdhms.month:02.0f} {date.ymdhms.day:02.0f}")
    else:
        dates = get_list_of_observed_dates(object_list)
    if convert_ast2abgaeipred or len(list(Path('.').glob('abgaeipred*.all'))) <= len(dates):
        ast2abg_aei_pred(dates=dates,
                         object_list=object_list)
    for date in dates:
        plt.close("all")
        plot_all(abgaeipredfile=f"abgaeipred_{date.replace(' ', '')}.3877.all",
                 det_ast="ast.all", pointfile=f"PH2_{date.replace(' ', '')}.xml",
                 what=what, date=date,
                 limits=limits, plot_astrometry=plot_astrometry
                 )


def plot_all(what: str = "skyfow",
             abgaeipredfile: str = "abgaeipred.all",
             pointfile: str = "PH2.xml",
             filename: str = "ast.all",
             det_ast: str = "ast.det",
             date: str = '',
             limits: Union[None, List[float]] = None,
             plot_astrometry: bool = False,
             pdf: bool = False,
             field_colours: str = ''
             ) -> None:
    """
    Make some plots.

    This is awful code stollen from M. Alexandersen's 'plot_all.py' that was written in 2011 or so
    and gradually made messier over the years.
    """
    print(what, abgaeipredfile, pointfile, filename, det_ast, plot_astrometry, limits, date)
    file_suffix = f"_{date.replace(' ', '')}" if date else ""
    # Read the file file
    tmp1 = np.genfromtxt(abgaeipredfile, dtype=str, delimiter=[7, 9, 10])
    tmp2 = np.genfromtxt(abgaeipredfile, dtype=str, delimiter=[2, 10, 11, 10, 9, 10, 12])
    tmp3 = np.genfromtxt(abgaeipredfile, dtype=str, delimiter=[21, 7, 2, 5])
    tmp4 = np.genfromtxt(abgaeipredfile, dtype=str, delimiter=[16, 2, 1, 2, 1, 9, 1, 2, 1, 2, 1, 7, 11, 11, 7])

    # Define arrays (this is stupid)
    ntmp = len(tmp1)
    n = ntmp // 5
    names = list()
    a = np.zeros(n)
    e = a.copy()
    inc = a.copy()
    Onode = a.copy()
    oargp = a.copy()
    t0 = a.copy()
    epoch = a.copy()
    sa = np.zeros(n)
    se = sa.copy()
    sinc = sa.copy()
    sOnode = sa.copy()
    soargp = sa.copy()
    st0 = sa.copy()
    d = np.zeros(n)
    sd = d.copy()
    ra = np.zeros(n)
    dec = ra.copy()
    sra = ra.copy()
    sdec = ra.copy()
    rah = ra.copy()
    ram = ra.copy()
    ras = ra.copy()
    decsign = ra.copy()
    decd = ra.copy()
    decm = ra.copy()
    decs = ra.copy()
    sras = ra.copy()
    sdecs = ra.copy()
    ang = ra.copy()
    colour = np.zeros((n, 4))

    # Loop through to assign each sub-array of ast to an independent array.
    # (More stupid)
    for i in np.arange(0, ntmp // 5):
        j = i * 5
        # name of object
        names.append(tmp1[j][0])
        # epoch:
        try:
            epoch[i] = tmp1[j][2].astype(float)
        except ValueError:
            epoch[i] = np.nan
        # elements and 1-sigma uncertainty of elements
        a[i] = tmp2[j + 1][1]
        sa[i] = tmp2[j + 2][1]
        e[i] = tmp2[j + 1][2]
        se[i] = tmp2[j + 2][2]
        inc[i] = tmp2[j + 1][3]
        sinc[i] = tmp2[j + 2][3]
        Onode[i] = tmp2[j + 1][4]
        sOnode[i] = tmp2[j + 2][4]
        oargp[i] = tmp2[j + 1][5]
        soargp[i] = tmp2[j + 2][5]
        t0[i] = tmp2[j + 1][6]
        st0[i] = tmp2[j + 2][6]
        # discovery distance and uncertainty
        d[i] = tmp3[j + 3][1]
        sd[i] = np.nan if ('nan' in tmp3[j + 3][3]) else tmp3[j + 3][3]
        # predicted position
        rah[i] = tmp4[j + 4][1]
        ram[i] = tmp4[j + 4][3]
        ras[i] = tmp4[j + 4][5]
        decsign[i] = tmp4[j + 4][6] + '1'
        decd[i] = tmp4[j + 4][7]
        decm[i] = tmp4[j + 4][9]
        decs[i] = tmp4[j + 4][11]
        # uncertainty in prediction, and angle (relative to due south :-S)
        sras[i] = tmp4[j + 4][12]
        sdecs[i] = tmp4[j + 4][13]
        ang[i] = tmp4[j + 4][14] 

    scoos = (sras**2 + sdecs**2)**0.5

    # define the colour map to be used:
    cm = plt.get_cmap('gist_rainbow')
    cm = plt.get_cmap('plasma')
    if "logcola" in what:  # Colours scale by log(da/a)
        for i in np.arange(0, n):
            j = np.log10(sa[i] / a[i])
            colour[i][:] = cm((j + 4) / 4.)
    if "cold" in what:  # Colours scale by distance
        for i in np.arange(0, n):
            #colour[i][:]= cm((d[i]-np.min(d))**2/np.max(d-np.min(d))**2)
            colour[i][:] = cm((d[i] - 7)**2 / 56**2)
    else:                 # Colour objects in order
        for i in np.arange(0, n):
          colour[i, :] = cm(i * 1. / (n - 4))

    # calculate average magnitudes from the detection astrometry.
    # Read ast file
    det = np.genfromtxt(det_ast, dtype=str,
                        delimiter=[1, 11, 1, 2, 4, 3, 9, 3, 3, 7, 1, 2, 3, 6, 9, 4, 2, 9, 2, 13, 13, 1, 1])
    ndet = len(det)
    magd = np.zeros(ndet)
    named = list()
    for i in range(0, ndet):
        if det[i][15] == '    ' or det[i][22] != ' ':
            magd[i] = np.nan
        else:
            magd[i] = det[i][15]
        named.append("".join(det[i][1].split()))
    # Weed out the fields with no magnitude, and then take the mean.
    indsd = np.zeros(n, dtype=int)
    indcd = indsd.copy()
    mmagd = np.zeros(n)
    smmagd = mmagd.copy()
    for i in range(n):
        namedi = names[i]
        indsd[i] = named.index(namedi)
        indcd[i] = named.count(namedi)
    for i in range(n):
        indd = range(indsd[i], indsd[i] + indcd[i])
        mag_NANd = magd[indd]
        ind_noNANd = np.where(np.invert(np.isnan(mag_NANd)))
        magsd = mag_NANd[ind_noNANd]
        mmagd[i] = np.nanmean(mag_NANd)
        smmagd[i] = np.nanstd(mag_NANd)

    # calculate average magnitudes from astrometry.
    # Read ast file
    ast = np.genfromtxt(filename, dtype=str,
                        delimiter=[1, 11, 1, 2, 4, 3, 10, 2, 3, 7, 1, 2, 3, 6, 9, 4, 2, 9])
    nast = len(ast)
    mag = np.zeros(nast)
    name = list()
    for i in range(0, nast):
        mag[i] = np.nan if ast[i][15] == '    ' else ast[i][15]
        name.append("".join(ast[i][1].split()))
    # Weed out the fields with no magnitude, and then take the mean.
    inds = np.zeros(n, dtype=int)
    indc = inds.copy()
    mmag = np.zeros(n)
    smmag = mmag.copy()
    for i in range(n):
        namei = names[i]
        inds[i] = name.index(namei)
        indc[i] = name.count(namei)
    for i in range(n):
        ind = range(inds[i], inds[i] + indc[i])
        mag_NAN = mag[ind]
        ind_noNAN = np.where(np.invert(np.isnan(mag_NAN)))
        mags = mag_NAN[ind_noNAN]
        mmag[i] = np.nanmean(mags)
        smmag[i] = np.std(mags)

    # calculate the arcs for each object.
    # Define arrays (this is stupid)
    DCd = np.zeros(nast)
    RAd = DCd.copy()
    year = DCd.copy()
    month = DCd.copy()
    day = DCd.copy()
    arc = np.zeros(n)
    # Loop through to assign each sub-array of ast to an independent array.
    # (More stupid)
    for i in range(0, nast):
        year[i] = ast[i][4]
        month[i] = ast[i][5]
        day[i] = ast[i][6]
        DCd[i] = (np.abs(float(ast[i][11])) + (float(ast[i][12]) + float(ast[i][13]) / 60.) / 60.) * float(ast[i][10] + '1')
        RAd[i] = 15 * (float(ast[i][7]) + (float(ast[i][8]) + float(ast[i][9]) / 60.) / 60.)
    ytd = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    ytd = [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    for i in range(n):
        ind = range(inds[i], inds[i] + indc[i])
        arc[i] = (year[ind[-1]] * 365. + ytd[month[ind[-1]].astype('<i2') - 1] + day[ind[-1]]) - (year[ind[0]] * 365. + ytd[month[ind[0]].astype('<i2') - 1] + day[ind[0]])

    astrometry_to_plot = []
    if date and plot_astrometry:
        for i in range(0, nast):
            if date in f"{ast[i][4]}{ast[i][5]}{ast[i][6]}":
                astrometry_to_plot.append([RAd[i], DCd[i]])

    # Estimate absolute H magnitude
    hmag = mmag - 2.5 * np.log10(d**2 * (d - 1.)**2 / 1.**4)
    hmagd = mmagd - 2.5 * np.log10(d**2 * (d - 1.)**2 / 1.**4)

    # Filter the objects with an index idx
    indtmp = np.where((a < 9999.) & (a > 0.1))
    if ("plutino" in what) or ("3:2" in what):
        indtmp = np.where((a > 39.00) & (a < 39.75))
    if ("twotino" in what) or ("2:1" in what):
        indtmp = np.where((a > 47.0) & (a < 48.5))
    if ("trojan" in what) or ("1:1" in what):
        indtmp = np.where((a > 29.75) & (a < 30.45))
    if ("trojan2" in what) or ("1:1" in what):
        indtmp = np.where((a > 29.75) & (a < 30.45) & (e < 0.5))
    if ("magcut" in what):
        indtmp = np.where(mmag < 24.15)
    if ("magcutB" in what):
        indtmp = np.where(mmagd < 24.15)
    if ("magcutD" in what):
        indtmp = np.where(mmag < 24.55)
    if ("magcutC" in what):
        indtmp = np.where((mmagd<24.55))# & (mmag>24.30))
    if ("cut3" in what):
        indtmp = np.where((arc<200))# & (mmag<24.65))# | (a<25))
    if ("cut4" in what):
        indtmp = np.where((((sa>0.004) | (sa/a>0.0001)) & (mmag<24.65)) | ((a>38.95) & (a<39.75)) | ((a>47.0) & (a<48.5)) | (a<25))
    if ("cut5" in what):
        indtmp = np.where((((sa>0.1) | (sa/a>0.001)) & (mmag<24.65)) | (a<25))
    if ("cut6" in what):
        indtmp = np.where((arc>0.5) & (np.invert(np.isnan(sa))) & (np.invert(np.isnan(sinc))) & (np.invert(np.isnan(sd))))
    if ("cut7" in what):
        indtmp = np.where((arc<187))
    if ("cut8" in what):
        indtmp = np.where((a>10.0) & (arc > 15))
    if ("cut9" in what):
      for i, si in enumerate(sa):
        print(f"{si:8.5f}, {si/a[i]:8.5f}")
      indtmp = np.where((sa>0.1) | (sa/a>0.001))
    if ("acut" in what):
      indtmp = np.where((a>28.0))
    if ("pricut" in what):
      nam = np.array(names).astype('U')
      indtmp = np.where((((a>39.00) & (a<39.75)) | ((a>54.95) & (a<56.0)) | ((a>47.0) & (a<48.3)) | (a>54) | (arc<187)))
    #  indtmp = np.where((mmag> = 24.55))
    if ("namecut" in what):
      nam = np.array(names)
      indtmp = np.where((a != np.nan) & (nam != '0109A01'))
    if ("namecut2" in what):
      nam = np.array(names)
      indtmp= np.where((a>1.0) & ['F12' not in nami for nami in nam] & ['F13' not in nami for nami in nam] & ['F14' not in nami for nami in nam] & ['F15' not in nami for nami in nam] & ['F16' not in nami for nami in nam] & ['F17' not in nami for nami in nam])
    if ("errcut" in what):
      nam = np.array(names)
      indtmp= np.where((a>0.01) & (scoos<9*60) | ['0D18E15' in nami for nami in nam] | ['4G16E13' in nami for nami in nam] | ['1H04A00' in nami for nami in nam] | ['0S31C07' in nami for nami in nam] | ['2X08C08' in nami for nami in nam] | ['2A04A02' in nami for nami in nam] | ['5D11B02' in nami for nami in nam])
    if ("errcut2" in what):
      nam = np.array(names)
      indtmp= np.where((a>0.01) & (scoos>0.1*60))
    if ("multicut" in what):
      nam = np.array(names)
      indtmp= np.where((a>1.0) & ((sras>2*60) | (sdecs>2*60)) & ['F12' not in nami for nami in nam] & ['F13' not in nami for nami in nam] & ['F14' not in nami for nami in nam] & ['F15' not in nami for nami in nam] & ['F16' not in nami for nami in nam] & ['F17' not in nami for nami in nam])
    if ("multicut2" in what):
      nam = np.array(names)
      indtmp= np.where((a>0.01) & (scoos>9*60) & ['F12' not in nami for nami in nam] & ['F13' not in nami for nami in nam] & ['F14' not in nami for nami in nam] & ['F15' not in nami for nami in nam] & ['F16' not in nami for nami in nam] & ['F17' not in nami for nami in nam])
    if ("colcut" in what):
      colidx = (((arc > 15) & ((a<39.4) | (a>54.4) | ((a<44.2) & (a>43.2)) | ((a<42.8) & (a>41.8)) | ((a<48.3) & (a>47.3)) | ((a<39.94) & (a>38.94)))) | ((arc < 187) & (arc > 15)))
      if ("colcuta" in what):
        colidx = (((arc < 187) & (arc > 15)))
      if ("colcutb" in what):
        nam = np.array(names)
        #indtmp = np.where((arc < 187))
        colidx = (arc < 187) | ['0B09T03' in nami for nami in nam] | ['0130T05' in nami for nami in nam] | ['0403U07' in nami for nami in nam] | ['1438U11' in nami for nami in nam] | ['0H15V12' in nami for nami in nam] | ['2A14V15' in nami for nami in nam] | ['2O15V15' in nami for nami in nam] | ['0210V16' in nami for nami in nam]
      if ("colcutc" in what):
        colidx = (arc > 15) & ((arc < 187) | ((a<39.94) & (a>38.94)) | (scoos > 1.5) & (((a<39.94) & (a>38.94)) | ((a<48.3) & (a>47.3)) | ((a<42.8) & (a>41.8)) | ((a<44.2) & (a>43.2)) | (a>54.4) | (a<39.4)))
    if ("colcut3" in what):
      indtmp = np.where((arc > 15) & ((a<40.) | (a>47.3) | ((a<44.2) & (a>43.2)) | ((a<42.8) & (a>41.8)) | ((a<48.3) & (a>47.3))) & (d>15))
    if ("colcut4" in what):
      nam = np.array(names)
      indtmp = np.where((arc < 45))
    idx = indtmp[0]  # np.where is strange
    print(len(a))
    a = a[idx]
    print(len(a))
    e = e[idx]
    inc = inc[idx]
    Onode= Onode[idx]
    oargp= oargp[idx]
    t0=    t0[idx]
    sa=    sa[idx]
    se=    se[idx]
    sinc=  sinc[idx]
    sOnode = sOnode[idx]
    soargp = soargp[idx]
    st0=   st0[idx]
    d=     d[idx]
    sd=    sd[idx]
    ra=    ra[idx]
    dec=   dec[idx]
    sra=   sra[idx]
    sdec=  sdec[idx]
    rah=   rah[idx]
    ram=   ram[idx]
    ras=   ras[idx]
    decsign = decsign[idx]
    decd=  decd[idx]
    decm=  decm[idx]
    decs=  decs[idx]
    sras=  sras[idx]
    sdecs= sdecs[idx]
    ang=   ang[idx]
    hmag = hmag[idx]
    hmagd = hmagd[idx]
    arc = arc[idx]
    epoch = epoch[idx]
    namesnew = []
    namesremoved = []
    for i, n in enumerate(names):
        if i in idx:
            namesnew.append(n)
        else:
            namesremoved.append(n)
    print(namesremoved)
    names = namesnew
    mmag = mmag[idx]
    smmag = smmag[idx]
    n = len(a)
    colour = colour[idx][:]
    #print colour
    if ("colcut" in what):
      print(colidx)
      print(len(a[colidx[idx]]))
      colour[np.invert(colidx[idx])] = [0., 0., 0., 1.]
    #else:
      #colour[arc<100] = [0., 0., 0., 1.]
      #colour[arc<70] = [0., 1., 0., 0.5]
      #colour[arc<10] = [0., 0., 1., 0.25]
      #colour[arc<1] = [1., 0., 0., 0.125]
      #colour[arc<0.5] = [0., 0., 0., 1.]
      #colour[arc<70, 3] = 0.5
      #colour[arc<0.00005] = [0., 0., 0., 1.]

    font = {'weight':'bold', 'size':16}
    mpl.rc('font', **font)
    mpl.rc('lines', linewidth=9, c='r')

    #### flag = sky #### Make sky plot #############################################
    if ("all" in what) or ("sky" in what):

    ## convert ra, dec and their uncertainties to decimal degrees
      ra = 15*(rah + (ram + ras/60.)/60.)
      dec = decsign * (decd + (decm + decs/60.)/60.)
      sra=sras/3600.  # sras is in arcsecs, not secs of time
      sdec = sdecs/3600.

    ## Plot predicted positions
      fig3 = plt.figure(1, figsize=(10, 10))
      gs = gridspec.GridSpec(10, 1, height_ratios=[1]*9 + [0.2])  # 9 plots + 1 small row for colorbar
      ax3 = fig3.add_subplot(gs[:-1, 0], aspect="equal")  # Main plot
      ax3cb = fig3.add_subplot(gs[-1, 0])  # Colour bar
      for i in np.arange(0, n):
        ax3.plot(ra[i], dec[i], 'o', markeredgewidth = 0, markersize = 6, color = colour[i], linewidth = 2.0)
    ## Set axes the right way round
      ramin = min(ra)
      ramax = max(ra)
      decmin = min(dec)
      decmax = max(dec)
      ax3.axis([ramax + 0.2, ramin-0.2, decmin-0.2, decmax + 0.2])

    ## Colour bar!
      if 'logcola' in what:
        exponents = np.arange(-4, 0.01, 1)
        labels_str = [r"$10^{" + f"{l:1.0f}" + "}$" for l in exponents]
        ticks = (np.log10(10**exponents) + 4) / 4
        cb1 = mpl.colorbar.ColorbarBase(ax3cb, cmap=cm, orientation='horizontal', ticks=ticks)
        cb1.ax.set_xticklabels(labels_str)
        cb1.set_label('Log10(da/a)')
      if 'cold' in what:
        j = np.arange(0, 1.01, 0.25)
        tick_d = [f"{i:4.1f}" for i in 7 + (j**0.5)*56]
        labels_str = tick_d
        ticks = j
        cb1 = mpl.colorbar.ColorbarBase(ax3cb, cmap=cm, orientation='horizontal', ticks=ticks)
        cb1.ax.set_xticklabels(labels_str)
        cb1.set_label('Distance (au)')

    ## setup error ellipses
      scale = np.array([1.])  # for scaling error ellipses
      errs = [Ellipse(xy=[ra[i], dec[i]], width=sra[i]*scale[0], height=sdec[i]*scale[0], angle=90-ang[i],
                      clip_box=ax3.bbox, alpha=colour[i][-1], facecolor='none', edgecolor=colour[i], linewidth=2)
              for i in np.arange(n)]  #this because ang is measured ccw from due NS,
                                      #and python measures cw from EW (BAD python!)
      for i in errs:
        ax3.add_artist(i)  # Actually add it to the plot
      ax3.axis([ramax + 0.2, ramin-0.2, decmin-0.2, decmax + 0.2])

    ## Read in the exact pointings that are generated from the pointing script.
    ## Read the file file
    #  os.system("python ../PH2/Pointings_scripts/layout_ll.py > PH2.xml") 
    #  os.system("python ./layout_ll.py > PH2.xml")
      try:
        tmp5 = np.genfromtxt(pointfile,
                             dtype = "a20, a, i, a, i, a, f, a, a1, i, a, i, a, f, a, f, a, a",
                             delimiter=[20, 1, 2, 1, 2, 1, 5, 1, 1, 2, 1, 2, 1, 4, 1, 6, 1, 5])
        nf = len(tmp5)-35  # number of frames
        fname = list()
        fra = np.zeros(nf)
        fdec = fra.copy()
        for i in np.arange(nf):
          j = i + 32
          fname.append(tmp5[j][0].rstrip().decode())
          fra[i] = 15*(tmp5[j][2] + (tmp5[j][4] + tmp5[j][6]/60.)/60.)
          fdec[i] = int(tmp5[j][8].astype(str) + '1') * (tmp5[j][9] + (tmp5[j][11] + tmp5[j][13]/60.)/60.)
        if ("magellan" not in what):
          fdec += (15 + 7.5) / 3600
      except FileNotFoundError:
          fra = []
          fdec = []
          nf = 0
          fname = []

    ## Set up dimensions of field-of-view and of individual ccd's
      if ("magellan" in what):  # Plot Magellan IMACS f/2 ccds instead
        if ('f4' in what):  # IMACS f/4
          dimf = np.array([15.4*60, 15.4*60])
          sgap = 8.0/3600           #dimension small gaps, deg
          bgap = 10.1/3600          #dimension big gaps, deg
        else:
          dimf = np.array([27.5*60, 27.5*60])  #dimensions of fow, width, height "
          sgap = 11.4/3600           #dimension small gaps, deg
          bgap = 18.4/3600           #dimension big gaps, deg
        ncol = 4
        if ("magellan2" in what):
          nrow = 4
        else:
          nrow = 2
        dimc = np.array([(dimf[0]-sgap*3600*(nrow-1))/ncol,
                       (dimf[1]-bgap*3600*(ncol-1))/nrow])  #dimensions of a chip, "
        fw = dimf[0]/3600.              # field width
        fh = dimf[1]/3600.              # Field height
        cw = dimc[0]/3600.              # Chip width
        ch = dimc[1]/3600.              # Chip height
      else:
        dimf = np.array([3514.60, 3580.55])  #dimensions of fow, width, height "
        dimc = np.array([376.77, 850.01])    #dimensions of a chip, "
        fw = dimf[0]/3600.              # field width
        fh = dimf[1]/3600.              # Field height
        cw = dimc[0]/3600.              # Chip width
        ch = dimc[1]/3600.              # Chip height
        sgap = ((fw-9*cw)/8.)           #dimension small gaps, deg
        bgap = ((fh-4*ch-1*sgap)/2.)    #dimension big gaps, deg
        nrow = 4
        ncol = 9

    #Now plot each 1 sq.deg. patch
      ramin = np.min([ra.min()])
      ramax = np.max([ra.max()])
      decmin = np.min([dec.min()])
      decmax = np.max([dec.max()])
      if ("fow" in what):    # Plot every field of view
        if ("ccd" in what):  # Plot every ccd
          cldec = np.zeros([nrow, ncol, nf])
          cudec = cldec.copy()
          cwura = cldec.copy()
          cwlra = cldec.copy()
          ceura = cldec.copy()
          celra = cldec.copy()
          for j in range(ncol):
            if ("magellan" in what):
              cldec[0, j, :] = fdec-fh/2.
              cldec[1, j, :] = fdec + fh/2.-ch
              if ("magellan2" in what):
                cldec[2, j, :] = fdec + fh/4.-ch
                cldec[3, j, :] = fdec-fh/4.
              for i in range(nrow):
                cudec[i, j, :] = cldec[i, j, :] + ch
                cwura[i, j, :] = fra + (j*(cw + sgap)-fw/2.)/np.cos(np.radians(cudec[i, j, :]))
                cwlra[i, j, :] = fra + (j*(cw + sgap)-fw/2.)/np.cos(np.radians(cldec[i, j, :]))
                ceura[i, 3-j, :] = fra-(j*(cw + sgap)-fw/2.)/np.cos(np.radians(cudec[i, j, :]))
                celra[i, 3-j, :] = fra-(j*(cw + sgap)-fw/2.)/np.cos(np.radians(cldec[i, j, :]))
            else:
              cldec[0, j, :] = fdec - fh / 2.
              cldec[1, j, :] = fdec - fh / 2. + ch + bgap
              cldec[2, j, :] = fdec + fh / 2. - 2 * ch - bgap
              cldec[3, j, :] = fdec + fh / 2. - ch
              for i in range(nrow):
                cudec[i, j, :] = cldec[i, j, :] + ch
                cwura[i, j, :] = fra + (j*(cw + sgap)-fw/2.)/np.cos(np.radians(cudec[i, j, :]))
                cwlra[i, j, :] = fra + (j*(cw + sgap)-fw/2.)/np.cos(np.radians(cldec[i, j, :]))
                ceura[i, 8-j, :] = fra-(j*(cw + sgap)-fw/2.)/np.cos(np.radians(cudec[i, j, :]))
                celra[i, 8-j, :] = fra-(j*(cw + sgap)-fw/2.)/np.cos(np.radians(cldec[i, j, :]))
          ccds = [Polygon(xy=[[cwura[i, j, k], cudec[i, j, k]], [cwlra[i, j, k], cldec[i, j, k]]
                  , [celra[i, j, k], cldec[i, j, k]], [ceura[i, j, k], cudec[i, j, k]]]) 
                  for i in range(nrow) for j in range(ncol) for k in np.arange(nf)] 
          for i in ccds:
            ax3.add_artist(i)
            i.set_clip_box(ax3.bbox)
            i.set_alpha(0.5)
            i.set_facecolor('none')  # none = see-through
            i.set_edgecolor([0.30, 0.30, 0.30, 0])
        cldec = fdec-fh/2.                             # Lower edge's Dec
        cudec = fdec + fh/2.                             # Upper edge's Dec
        cwura = fra-(fw/2.)/np.cos(np.radians(cudec))  # Western upper corner's RA
        cwlra = fra-(fw/2.)/np.cos(np.radians(cldec))  # Western lower corner's RA
        ceura = fra + (fw/2.)/np.cos(np.radians(cudec))  # Eastern upper corner's RA
        celra = fra + (fw/2.)/np.cos(np.radians(cldec))  # Eastern lower corner's RA
        earudec = fdec + ch + sgap/2.
        earldec = fdec - (ch + sgap/2.)
        wewura = fra-(fw/2. + sgap + cw)/np.cos(np.radians(earudec))  # Western ears's western upper corner's RA
        wewlra = fra-(fw/2. + sgap + cw)/np.cos(np.radians(earldec))  # Western ears's western lower corner's RA
        weeura = fra-(fw/2.)/np.cos(np.radians(earudec))          # Western ear's eastern upper corner's RA
        weelra = fra-(fw/2.)/np.cos(np.radians(earldec))          # Western ear's eastern lower corner's RA
        eewura = fra + (fw/2.)/np.cos(np.radians(earudec))          # Eastern ears's western upper corner's RA
        eewlra = fra + (fw/2.)/np.cos(np.radians(earldec))          # Eastern ears's western lower corner's RA
        eeeura = fra + (fw/2. + sgap + cw)/np.cos(np.radians(earudec))  # Eastern ear's eastern upper corner's RA
        eeelra = fra + (fw/2. + sgap + cw)/np.cos(np.radians(earldec))  # Eastern ear's eastern lower corner's RA

        #fields = [Polygon(xy=[[cwura[i], cudec[i]], [cwlra[i], cldec[i]]
        #      , [celra[i], cldec[i]], [ceura[i], cudec[i]]]) for i in np.arange(nf)]  # Simple rectangle, no ears
        if ("magellan" in what):  # Plot Magellan IMACS f/2 field of view instead
            fields = [Circle(xy=[fra[i], fdec[i]], radius=12/60.) for i in np.arange(nf)]
        else:
            fields = [Polygon(xy=[[ceura[i], cudec[i]], [cwura[i], cudec[i]],
                                [weeura[i], earudec[i]], [wewura[i], earudec[i]],
                                [wewlra[i], earldec[i]], [weelra[i], earldec[i]],
                                [cwlra[i], cldec[i]], [celra[i], cldec[i]],
                                [eewlra[i], earldec[i]], [eeelra[i], earldec[i]],
                                [eeeura[i], earudec[i]], [eewura[i], earudec[i]],
                                ]) for i in np.arange(nf)]
        if field_colours:
            fc_name, fc_col1, fc_col2, fc_col3, fc_style = np.genfromtxt(field_colours, usecols=(0, 1, 2, 3, 4),
                                                                         dtype=None, unpack=True)
        for j, i in enumerate(fields):
            ax3.add_artist(i)
            i.set_clip_box(ax3.bbox)
            i.set_alpha(1)
            i.set_facecolor('none')  # none = see-through
            i.set_linewidth(1.0)
            if field_colours:
                for k, fc in enumerate(fc_name):
                    if fc in fname[j]:
                        i.set_edgecolor([fc_col1[k], fc_col2[k], fc_col3[k]])
                        i.set_linestyle(fc_style[k])
            else:
                i.set_edgecolor([0, 0, 0, 0])
        if plot_astrometry and astrometry_to_plot:
            print(np.array(astrometry_to_plot).T[0], np.array(astrometry_to_plot).T[1])
            ax3.plot(np.array(astrometry_to_plot).T[0], np.array(astrometry_to_plot).T[1],
                     'ok', markeredgewidth = 1, markerfacecolor='none',
                     markersize=6, zorder=20)
        if ("fname" in what):
          for i in range(nf):
            ax3.text(fra[i] + 0.04, fdec[i] + 0.05, fname[i][-2:], size=10)
        sraa = np.max([sra, sdec], 0)
        sdeca = np.min([sra, sdec], 0)
        try:
            ramin = np.min([ra.min(), cwlra.min(), cwura.min()])
            ramax = np.max([ra.max(), celra.max(), ceura.max()])
            decmin = np.min([dec.min(), cldec.min()])
            decmax = np.max([dec.max(), cudec.max()])
        except ValueError:
            ramin = ra.min()
            ramax = ra.max()
            decmin = dec.min()
            decmax = dec.max()
      if limits:
          ramin, ramax, decmin, decmax = limits
      print(ramin, ramax, decmin, decmax)
      if ("mmag" in what):
        for i in range(n):
          ax3.text(ra[i] + 0.04, dec[i] + 0.05, mmag[i].astype('U4'), size = 8)
      if ("dmag" in what):
        for i in range(n):
          ax3.text(ra[i] + 0.04, dec[i] + 0.05, magd[i].astype('U4'), size=8)
      if ("oname" in what):
        for i in range(n):
          ax3.text(ra[i] + 0.04, dec[i]-0.15, names[i].astype('U10'), size=8)
      if ("date" in what and date):
        ax3.set_title(date)
      ax3.axis([ramax + 0.5, ramin-0.5, decmin-0.5, decmax + 0.5])
      ax3.axis([ramax + 1.5, ramin-1.5, decmin-1.5, decmax + 1.5])
      ax3.set_xlabel('RA (deg)')
      ax3.set_ylabel('Dec (deg)')
      print(f'Saving sky{file_suffix}')
      # Reposition colorbar axis to match main plot width
      plt.tight_layout()
      pos = ax3.get_position()
      poscb = ax3cb.get_position()
      cb_height = 0.02
      cb_pad = 0.07
      ax3cb.set_position([
                          pos.x0,
                          pos.y0 - cb_height - cb_pad,
                          pos.width,
                          cb_height
                          ])
      fig3.savefig(f'sky{file_suffix}.png', dpi=300, bbox_inches='tight')
      if pdf:
          fig3.savefig(f'sky{file_suffix}.pdf', dpi=300, bbox_inches='tight')
      sleep(0.5)
      plt.close(fig3)


    #
    if "noshow" not in what:
        plt.show()
    else:
        plt.close()


if __name__ == '__main__':
    print(sys.argv)
    parser = argparse.ArgumentParser(prog="plot_all_times",
                                     description="Plot our objects and observed fields on all observed nights.",
                                     epilog="Will generate a lot of plots.")
    parser.add_argument('ast_dir', nargs='?',
                        type=str, help='Where does the astrometry live?')
    parser.add_argument('all_list', default='all.list', nargs='?',
                        type=str, help='Filename containing list of all objects.')
    parser.add_argument('-w', '--what', default='skyfownoshowsavedatecold',
                        type=str, help='Various other arguments packed into one string.')
    parser.add_argument('-l', '--limits', default=None, nargs=4, type=float)
    parser.add_argument('-pa', '--plot_astrometry', action='store_true')
    parser.add_argument('-d', '--disc', action='store_true')
    parser.add_argument('-sd', '--start_date', default=None, type=str)
    parser.add_argument('-dr', '--date_range', default=None, type=int)
    parser.add_argument('-a', '--abgaeipred', action='store_true')

    args = parser.parse_args()
    with open(args.all_list, 'r', encoding='ascii') as al:
        object_list = [line.strip() for line in al.readlines()]
    if args.disc:
        plot_all(abgaeipredfile="abgaeipred_disc.all",
                 det_ast="ast.all", pointfile="PH2_disc.xml",
                 what=args.what, pdf=True,
                 field_colours="field_colours.txt",
                 limits=args.limits, plot_astrometry=args.plot_astrometry
                 )
    else:
        main(args.ast_dir, object_list, what=args.what, limits=args.limits,
             plot_astrometry=args.plot_astrometry,
             date_start_and_range=(args.start_date, args.date_range),
             convert_ast2abgaeipred=args.abgaeipred
             )
