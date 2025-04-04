#!/usr/bin/env python3

import numpy as np
import subprocess as sp
import sys
import json
import copy

def parse_existing_file(filename):
    elements = np.genfromtxt(filename, names=True, skip_header=2, dtype=None, encoding='utf-8')
    return elements

def printelements(new, filename):
    with open(filename, 'w') as elfile:
        print(f'# File: {filename}')
        elfile.write(f'# File: {filename}\n')
        print('#')
        elfile.write('#\n')
        print('# cl p  j   k sh     object  mag e_mag Filt Hsur dist  e_dist    Nobs   time  av_xres av_yres max_x  max_y       a          e_a        e        e_e      i      e_i      Omega e_Omega    omega   e_omega      tperi    e_tperi   RAdeg   DEdeg      JD        rate')
        elfile.write('# cl p  j   k sh     object  mag e_mag Filt Hsur dist  e_dist    Nobs   time  av_xres av_yres max_x  max_y       a          e_a        e        e_e      i      e_i      Omega e_Omega    omega   e_omega      tperi    e_tperi   RAdeg   DEdeg      JD        rate\n')
        for i in range(len(new)):#0011111111112222222222333333333344444444445555555555666666666677
            li = (#012345678901234567890123456789012345678901234567890123456789012345678901
                  f"{new[i]['cl']:>3} {new[i]['p']:>1} {new[i]['j']:>3} {new[i]['k']:>3} {new[i]['sh']:>2} " +
                  f"{new[i]['object']:>10} {float(new[i]['mag']):5.2f} {float(new[i]['e_mag']):5.2f} " +
                  f"{new[i]['Filt']:1} {new[i]['Hsur']:5.2f} " +
                  f"{new[i]['dist']:7.3f} {new[i]['e_dist']:7.3f} {new[i]['Nobs']:>4} {new[i]['time']/365.24:9.4f} " +
                  f"{float(new[i]['av_xres']):6.3f} {float(new[i]['av_yres']):6.3f} " +
                  f"{float(new[i]['max_x']):6.3f} {float(new[i]['max_y']):6.3f} " +
                  f"{new[i]['a']:11.6f} {new[i]['e_a']:10.4f} {new[i]['e']:9.6f} {new[i]['e_e']:9.6f} " +
                  f"{new[i]['i']:7.3f} {new[i]['e_i']:7.3f} {new[i]['Omega']:8.3f} {new[i]['e_Omega']:7.3f} " +
                  f"{new[i]['omega']:8.3f} {new[i]['e_omega']:9.3f} {new[i]['tperi']-2400000.5:10.3f} {new[i]['e_tperi']:10.3f} " +
                  f"{new[i]['RAdeg']:7.3f} {new[i]['DEdeg']:+7.3f} {new[i]['JD']:13.5f} {new[i]['rate']:5.2f}"
                  )
            print(li)
            elfile.write(li + '\n')

def run_fo(obj, ast_location):
    #epoch = "2023 01 01.5"
    with open(f'{ast_location}/{obj}.obs', 'r', encoding='ascii') as astfile:
        for line in astfile.readlines():
            if line[12]=='*':
                epoch = line[15:32]
                break
    result = sp.run(f'fo {ast_location}/{obj}.obs -tE "{epoch}" -h-1 -e /tmp/ephem.txt "EPHEM_START={epoch}" EPHEM_STEPS=1 EPHEM_STEP_SIZE=1s EPHEM_OPTIONS=10,16-17,39 "CONSOLE_OPTS=Sun 0 3 1" -e {obj}.eph',
                    shell=True, check=True, stdout=sp.PIPE)
    elements_json = json.load(open('/home/mikea/.find_orb/elements.json', 'r', encoding='utf-8'))
    ephem_json = json.load(open('/home/mikea/.find_orb/ephemeri.json', 'r', encoding='utf-8'))
    
    return elements_json, ephem_json

def parse_ephem(eph_json):
    ephem = eph_json["ephemeris"]["entries"]["0"]
    return ephem["delta"], ephem["sgDel"], ephem["mag"]

def parse_elements(obj, elements_json):
    if len(elements_json['objects'])!=1:
        print("Multiple designations!")
    obj2 = list(elements_json['objects'])[0]
    if obj!=obj2:
        print(f'WTF? {obj}!={obj2}')
    res= get_residuals(elements_json['objects'][obj2]['observations']['residuals'])
    elements = get_elements(elements_json['objects'][obj2]['elements'])
    return elements, res, obj2

def get_elements(els):
    if 'a sigma' not in els:
        els['a sigma'] = els['a']
    return [els[i] for i in ['a', 'a sigma', 'e', 'e sigma', 'i', 'i sigma', 'asc_node', 'asc_node sigma', 'arg_per', 'arg_per sigma', 'Tp', 'Tp sigma', 'H']]

def get_residuals(res):
    x_max, y_max = 0, 0
    x_sum, y_sum = 0, 0
    nobs = 0
    mags = []
    drate = 0
    djd = 0
    rad = 0
    decd = 0
    obs_jd = []
    for line in res:
        x_max = np.nanmax([line['dRA'], x_max])
        y_max = np.nanmax([line['dDec'], y_max])
        x_sum += line['dRA']**2
        y_sum += line['dDec']**2
        obs_jd.append(line['JD'])
        mags.append(np.nan if ('MagObs' not in line) else line['MagObs'])
        if line['discovery_asterisk']=='*' and not drate:  # Want rate at first *
            drate = line['TotalMotion'] * 60  # arcmin to arcsec
            rad = line['RA']
            decd = line['Dec']
            djd = line['JD']
        nobs += 1
    x_av = (x_sum**0.5)/nobs
    y_av = (y_sum**0.5)/nobs
    print(mags)
    mag_av = np.nanmean(mags)
    nmags = np.sum(np.invert(np.isnan(mags)))
    mag_sigma = np.nanstd(mags) + (0.1/nmags)
    arc = max(obs_jd) - min(obs_jd)
    return mag_av, mag_sigma, nobs, arc, x_max, y_max, x_av, y_av, rad, decd, djd, drate


def main(prevfile=None, newfile=None, ast_location=None):
    prevfile = prevfile if prevfile else sys.argv[1]
    newfile = newfile if newfile else sys.argv[2]
    ast_location = ast_location if ast_location else sys.argv[3]
    prev = parse_existing_file(prevfile)
    new = copy.deepcopy(prev)
    for i, obji in enumerate(prev['object']):
        print(obji)
        obj=obji[1:] if obji[0]=='u' else obji
        els_json, eph_json = run_fo(obj, ast_location)
        els, res, mpcdes = parse_elements(obj, els_json)
        (new[i]['mag'], new[i]['e_mag'], new[i]['Nobs'], new[i]['time'],
         new[i]['av_xres'], new[i]['av_yres'], new[i]['max_x'],
         new[i]['max_y'], new[i]['RAdeg'], new[i]['DEdeg'], new[i]['JD'],
         new[i]['rate']) = res[0:12]
        (new[i]['a'], new[i]['e_a'], new[i]['e'],
         new[i]['e_e'], new[i]['i'], new[i]['e_i'], new[i]['Omega'],
         new[i]['e_Omega'], new[i]['omega'], new[i]['e_omega'],
         new[i]['tperi'], new[i]['e_tperi'], new[i]['Hsur']) = els[0:13]
        eph = parse_ephem(eph_json)
        (new[i]['dist'], new[i]['e_dist']) = eph[0:2]
        print(new[i]['mag'], eph[2])
    print(new)
    
    printelements(new, newfile)


if __name__ == '__main__':
    main()
