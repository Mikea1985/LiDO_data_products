#!/usr/bin/env python3

import numpy as np
import subprocess as sp
import sys
import json
import copy
import glob

def base62():
    VALID_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    conv = {}
    for i, j in enumerate(VALID_CHARS):
        conv[j] = str(i)
    return conv

def unpack_provid(packed):
    if not packed.strip():
        return ''
    conv = base62()
    conv["0"] = ''
    unpacked=f"{conv[packed[0]]}{packed[1:3]} {packed[3]}{packed[6]}{conv[packed[4]]}{packed[5]}"
    if len(unpacked)==8 and unpacked[-1]=="0":
        unpacked = unpacked[:-1]
    return unpacked

def unpack_permid(packed):
    if not packed.strip():
        return ''
    conv = base62()
    if packed[0]=="~":
        sum4 = int(conv[packed[4]])
        sum4 += 62*int(conv[packed[3]])
        sum4 += 62**2*int(conv[packed[2]])
        sum4 += 62**3*int(conv[packed[1]])
        unpacked = f"{620000 + sum4}"
    else:
        unpacked = f"{conv[packed[0]]}{conv[packed[1]]}{conv[packed[2]]}{conv[packed[3]]}{conv[packed[4]]}"

    while unpacked[0] == "0":
        unpacked = unpacked[1:]

    return unpacked


def get_ast_info(ast_location):
    for filename in glob.glob(ast_location + '/*.ast'):
        print(filename)
        psv_lines = {'269_header.txt': [], 'T09_header.txt': [], 'T15_header.txt': [],
                     'T14_r_header.txt': [], 'T14_w_header.txt': [], 'Other': []}
        with open(filename, 'r', encoding='ascii') as ofile:
            olines = ofile.readlines()
        for line in olines:
            #print(line)
            if line[0] == '!':
                continue
            psv, stn, ymd, ref = line_to_psv(line)
            if stn=='269':
                psv_lines['269_header.txt'].append(psv)
            elif stn=='T09':
                psv_lines['T09_header.txt'].append(psv)
            elif stn=='T15':
                psv_lines['T15_header.txt'].append(psv)
            elif (stn=='T14') & (ymd<'2020'):
                psv_lines['T14_r_header.txt'].append(psv)
            elif (stn=='T14') & (ymd>='2020'):
                psv_lines['T14_w_header.txt'].append(psv)
            elif ref:
                psv_lines['Other'].append(psv)
            else:
                raise ValueError(f"Don't recognize {stn} at {ymd}")
        with open(filename.replace('.ast', '.psv'), 'w') as pfile:
            print("# version=2022", file=pfile)
            for h in ['T14_w_header.txt', 'T14_r_header.txt', 'T15_header.txt',
                      'T09_header.txt', '269_header.txt']:
                if psv_lines[h]:
                    with open(h, 'r') as hfile:
                        header = hfile.read()
                    print(header, file=pfile)
                    for psv in psv_lines[h]:
                        print(psv, file=pfile)


def line_to_psv(line):
    permid = unpack_permid(line[0:5])
    trksub = line[5:12]
    provid = unpack_provid(trksub) if trksub[0]=="K" else '       '
    star = line[12]
    note1 = line[13]
    note2 = line[14]
    mode = 'CMO' if note2=='B' else 'CCD' if note2=='C' else '   '
    ymd = line[15:25].replace(' ', '-')
    decimal_day = float('0'+line[25:32])
    hourf = decimal_day * 24
    hour = int(hourf)
    minsf = (hourf-hour) * 60
    mins = int(minsf)
    sec = (minsf-mins) * 60
    obstime = f'{ymd}T{hour:02.0f}:{mins:02.0f}:{sec:05.2f}Z'
    rah = line[32:34]
    ram = line[35:37]
    ras = line[38:44]
    ra = (float(ras)/3600. + float(ram)/60 + float(rah)) * 15
    decsign = line[44]
    decd = line[45:47]
    decm = line[48:50]
    decs = line[51:56]
    dec = (float(decs)/3600 + float(decm)/60 + float(decd)) * (float(decsign + '1'))
    mag1 = line[65:70]
    band = line[70]
    cat = line[71]
    ref = line[72:77]
    stn = line[77:80]
    expid = line[82:95]
    xpix = line[111:118]
    ypix = line[119:126]
    # Most of our lines say 0.2, but scatter is more like 0.1
    # Some have 0.1 or 0.4 for being worse or better.
    # Scale these uncertainty by factor 2.
    if line[127:131]=='----':
        rmsra = ''
        rmsdec = ''
    else:
        rmsra = float(line[127:131])/2
        rmsdec = float(line[127:131])/2
    mag2 = line[134:139]
    rmsmag = '    ' if line[140:144]=='----' else line[140:144]
    try:
        tst = float(mag2)
        mag = mag2
    except Exception:
        mag = mag1
    if star=='*':
        if ref.strip():
            disc='*'
        else:
            if permid.strip() or provid.strip():
                disc='+'
            else:
                disc='*'
    else:
        disc = ''
    rmstime = '0.1'
    astcat = 'Gaia2' if stn in ['T14'] else 'PS1_DR2'
    photcat = '' if not mag.strip() else 'PS1_DR2'
    notes = note1
    remarks = f"Previously published in {ref}" if ref.strip() else ""
    return make_psv(permid, provid, trksub, mode, stn, obstime, rmstime,
                   ra, rmsra, dec, rmsdec, astcat, mag, rmsmag, band, photcat,
                   disc, notes, remarks), stn, ymd, ref.strip()

def make_psv(permid, provid, trksub, mode, stn, obstime, rmstime,
             ra, rmsra, dec, rmsdec, astCat, mag, rmsmag, band, photcat,
             disc, notes, remarks):
    psv = f"{permid:>7} | {provid:<10} | {trksub:<7} | {mode:<3}  | {stn:<4} | {obstime:<23} | {rmstime:<7} | {ra:>10.6f} | {rmsra:<5} | {dec:>+10.6f} | {rmsdec:<6} | {astCat:<7} | {mag:<5} | {rmsmag:<6} | {band:<4} | {photcat:<8} | {disc:<4} | {notes:<5} | {remarks}"
    return psv




def main(ast_location=None):
    ast_location = ast_location if ast_location else sys.argv[1]
    get_ast_info(ast_location)
    
if __name__ == '__main__':
    main()
