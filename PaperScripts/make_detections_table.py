import numpy as np
import subprocess as sp
import sys

def parse_existing_file(filename):
    elements = np.genfromtxt(filename, names=True, skip_header=2, dtype=None)
    return elements

def printelements(names, mmagd, hmagd, d, sd, indc, arc, a, sa, e, se, inc, sinc, Onode, sOnode, oargp, soargp, t0, st0, filename):
    with open(filename, 'w') as elfile:
        print(f'# File: {filename}')
        elfile.write(f'# File: {filename}\n')
        print('#')
        elfile.write('#\n')
        print('# cl p  j   k sh     object  mag e_mag Filt Hsur dist  e_dist    Nobs   time  av_xres av_yres max_x  max_y       a          e_a        e        e_e      i      e_i      Omega e_Omega    omega   e_omega      tperi    e_tperi   RAdeg   DEdeg      JD        rate')
        elfile.write('# cl p  j   k sh     object  mag e_mag Filt Hsur dist  e_dist    Nobs   time  av_xres av_yres max_x  max_y       a          e_a        e        e_e      i      e_i      Omega e_Omega    omega   e_omega      tperi    e_tperi   RAdeg   DEdeg      JD        rate\n')
        for i in range(n):#0011111111112222222222333333333344444444445555555555666666666677
            li = (#012345678901234567890123456789012345678901234567890123456789012345678901
                  f'??? ? ??? ??? ?? ' +
                  f"{names[i]:>10} {mmagd[i]:5.2f} ????? w {hmagd[i]:5.2f} " +
                  f"{d[i]:7.3f} {sd[i]:7.3} {indc[i]:>4} {arc[i]/365.24:9.4f} " +
                  f"?????? ?????? ?????? ?????? " +
                  f"{a[i]:11.6f} {sa[i]:10.4f} {e[i]:9.6f} {se[i]:9.6f} " +
                  f"{inc[i]:7.3f} {sinc[i]:7.3f} {Onode[i]:8.3f} {sOnode[i]:7.3f} " +
                  f"{oargp[i]:8.3f} {soargp[i]:9.3f} {t0[i]-2400000.5:10.3f} {st0[i]:10.3f} " +   
                  f"??????? ??????? ????????????? ?????"
                  )
            print(li)
            elfile.write(li + '\n')

def run_fo(obj):
    epoch = "2023 01 01.5"
    sp.run('fo -tE "{epoch}" -h-1', shell=True)
    elements_json = json.load(open('/home/mikea/.find_orb/elements.json'))
    if len(a['objects'])!=1:
        print("Multiple designations!")
    obj2 = list(elements_json['objects'])[0]
    x_max, y_max, x_av, y_av, totalmotion = get_residuals(elements_json['objects'][obj]['observations']['residuals'])
    elements = get_elements(elements_json['objects'][obj]['elements'])


def get_elements(els):
    return [els[i] for i in ['a', 'a sigma', 'e', 'e sigma', 'i', 'i sigma', 'asc_node', 'asc_node sigma', 'arg_per', 'arg_peri sigma', 'Tp', 'Tp sigma', 'H']]

def get_residuals(res):
    x_max, y_max = 0, 0
    x_sum, y_sum = 0, 0
    nobs = 0
    for line in res:
        x_max = np.nanmax([line['dRA'], x_max])
        y_max = np.nanmax([line['dDec'], y_max])
        x_sum += line['dRA']**2
        y_sum += line['dDec']**2
        nobs += 1
    x_av = (x_sum**0.5)/nobs
    y_av = (y_sum**0.5)/nobs
    return x_max, y_max, x_av, y_av

def main():
    prevfile = sys.argv[1]
    newfile = sys.argv[2]
    prev = parse_existing_file(prevfile)
    for obj in prev['object']:
        if obj[0]=='u':
            obj=obj[1:]



if __name__ == '__main__':
    main()
