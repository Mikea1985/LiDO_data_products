#!/home/malexand/.anaconda3/envs/lidoconda3/bin/python3

import glob
import re
import subprocess as sp
import sys

import numpy as np
from astropy.time import Time


def get_time(expno_p_ccdno):
    """
    Get the time for the center of the exposure
    """
    expno = expno_p_ccdno.split("p")[0].strip()
    ccdno = expno_p_ccdno.split("p")[1].strip()
    print(f"vcat vos:Kozai/MOP/dbimages/{expno}/ccd{ccdno}/{expno}p{ccdno}.mopheader")
    result = sp.run(
        f"vcat vos:Kozai/MOP/dbimages/{expno}/ccd{ccdno}/{expno}p{ccdno}.mopheader",
        shell=True,
        stdout=sp.PIPE,
        stderr=sp.PIPE,
    )
    for ccdi in np.arange(0, 40):
        ccdno = f"{ccdi:02.0f}"
        if result.returncode != 0:
            print(ccdno)
            result = sp.run(
                f"vcat vos:Kozai/MOP/dbimages/{expno}/ccd{ccdno}/{expno}p{ccdno}.mopheader",
                shell=True,
                stdout=sp.PIPE,
                stderr=sp.PIPE,
            )
    if result.returncode != 0:
        raise FileNotFoundError(result.stderr.decode())
    header = re.findall("." * 80, result.stdout.decode())
    header_dict = {}
    for h in header:
        if "=" in h:
            key = h.split("=")[0].strip()
            val = h.split("=")[1].strip()
            header_dict[key] = val
    return header_dict["MJD-OBSC"]


def mjd_to_mpc(mjd_in):
    """
    Convert an MJD date to a MPC formatted date.
    YYYY MM DD.dddddd
    """
    time = Time(mjd_in, format="mjd")
    ymd = f"{time.iso[:10].replace('-', ' ')}."
    decimals = f"{time.mjd:12.6f}".split(".")[1]
    mpc_date = ymd + decimals
    return mpc_date


def fix_one_line(line_in):
    """
    Fix the time in a single line.
    """
    expno_p_ccdno = line_in[85:95]
    try:
        mjd_obs = get_time(expno_p_ccdno)
        mpc_obs = mjd_to_mpc(mjd_obs)
        line_out = line_in[:15] + mpc_obs + line_in[32:]
    except (FileNotFoundError, IndexError):
        line_out = line_in
    return line_out


def time_diff(line1, line2):
    """
    Calculate the time between two lines.
    """
    year1 = line1[15:19]
    year2 = line2[15:19]
    month1 = line1[20:22]
    month2 = line2[20:22]
    day1 = line1[23:32]
    day2 = line2[23:32]
    if year1 != year2 or month1 != month2:
        diff = np.inf
    else:
        diff = (float(day2) - float(day1)) * 24 * 3600
    if (diff == 0) and (day2[-1] == " "):
        diff = np.nan
    return diff


def fix_one_file(filename, overwrite=False):
    """
    Fix everything for one file.
    """
    print(filename)
    with open(filename, "r", encoding="utf-8") as in_file:
        lines = in_file.readlines()
    with open(filename + "_fixed", "w", encoding="utf-8") as out_file:
        with open(
            filename.replace(".ast", ".diff"), "w", encoding="utf-8"
        ) as diff_file:
            for line in lines:
                fixed_line = fix_one_line(line)
                diff = time_diff(line, fixed_line)
                print(f"{line[85:95]}, {diff}")
                diff_file.write(
                    f"Delta_T = {diff:7.2f} s : {line[5:32]} : {fixed_line[5:32]}\n"
                )
                out_file.write(fixed_line)
    # if overwrite:
    #    shutil.move(filename + '_fixed', filename)


if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) > 1:
        file_patern = sys.argv[1]
    else:
        file_patern = "*.ast"
    if len(sys.argv) > 2:
        overwrite = True
    else:
        overwrite = False
    files = sorted(glob.glob(file_patern))
    print(files)

    for filename in files:
        fix_one_file(filename, overwrite)
