import math

import numpy as np

objABCDE = open("../Orbits/LiDO_ABCDE.detections").readlines()[3:]
objTUV = open("../Orbits/LiDO_TUV.detections").readlines()[3:]
notes_all = open("../Orbits/notes_not_res.txt").readlines()[1:]
notes_res = open("../Orbits/notes_res.txt").readlines()[1:]
mixed_mode_resonances = open("../Orbits/mixed_mode_resonances.txt").readlines()
names = open("../Orbits/correspondence.txt").readlines()

restable = open("../PaperProducts/tab_resobjects.tex", "w")
objtable = open("../PaperProducts/tab_objects.tex", "w")


# restable.write(r"\begin{table}[h!]\n\setlength{\tabcolsep}{2.5pt}\n\caption{Resonant \lido Survey Objects}\n\label{tab:resobjects}\n\begin{center}\n\begin{tabular}{ c  c  c | c  c  c  c c c c c c c c c c | c c} \nSurvey Name & MPC Name & Resonance & S/I & RC & RA & KC & KA & $m_r$ & $H_w$ & $a$ & $e$ & $i$ & dist & arc length & nobs &Notes \\ \hline\n")
# objtable.write(r"\begin{table}[h!]\n\setlength{\tabcolsep}{2.5pt}\n\caption{\lido Survey Objects}\n\label{tab:objects}\n\begin{center}\n\begin{tabular}{ c  c  c | c  c  c  c c c c c c | c c} \nSurvey Name & MPC Name & Classification &S/I & $m_r$ & $H_r$ & $a$ & $e$ & $i$ & dist & arc length & nobs &Notes \\ \hline\n")


restable.write(r"""\begin{longrotatetable}
\setlength{\tabcolsep}{2pt}
\tablewidth{10in}
\tabletypesize{\footnotesize}
\begin{longtable}{ll|ccccccccc | l}
\caption{Resonant \lido Survey Objects} \label{tab:resobjects}\\
\hline\hline\\
Survey & MPC & Resonance & S/I & Res Frac& RC & RA &Island Frac& KC & KA & KFrac  &Notes \\
ID & designation &  &  & \% & $\degr$ & $\degr$ &\%& $\degr$ & $\degr$ & \% &  \\\hline \hline
\endhead
""")
objtable.write(r"""\begin{longrotatetable}
\setlength{\tabcolsep}{2pt}
\tablewidth{10in}
\tabletypesize{\footnotesize}
\begin{longtable}{ll|ccccccccccc | l}
\caption{All \lido Survey Objects} \label{tab:objects}\\
\hline\hline\\
Survey & MPC & Classification & S/I & $m_w$ & $H_w$ & $a$ & $e$ & $i$ & $q$ & dist & arc length & nobs &Notes\\
ID & designation &  &  & mag & mag & au &  & $\degr$ & au & au & years &  & \\\hline\hline
\endhead
""")


objs = objABCDE + objTUV
ap = " & "
pm = r"$\pm$"


def getmpcname(sname):
    mpc = ""
    for obj in names:
        if obj.split()[0] == sname:
            for n in obj.split():
                # if n[0]=='K':
                if "_" in n:
                    mpc += n.replace("_", " ")
                if "(" in n:
                    mpc = n.replace("_", " ") + " " + mpc
    return mpc


def getnote(sname, notelist):
    # notelist = open('../Orbits/notes.txt','r').readlines()
    note = ""
    for n in notelist:
        if len(n) > 1:
            if n.split()[0] == sname:
                note = note + n[len(n.split()[0]) + 1 :].strip("\n") + "  "
                # print(note)
    return note


def round_to_uncertainty(value: float, uncertainty: float) -> tuple[float, float]:
    """Round value and uncertainty to the most significant digit of the uncertainty."""
    decimal_places = -math.floor(math.log10(uncertainty))
    return round(value, decimal_places), round(uncertainty, decimal_places)


def getsigs_old(v, dv):
    sg = dv.count("0")
    vr = str(round(float(v), sg))
    return vr


def getsigs(v, dv):
    if float(dv) == 0:
        return getsigs_old(v, dv)
    sg = -math.floor(math.log10(float(dv)))
    if sg < 0:
        # round to tens/hundreds etc — format as int
        factor = 10 ** (-sg)
        vr = str(round(float(v) / factor) * factor)
    else:
        vr = f"{float(v):.{sg}f}"
    return vr


def report_value(v, unc):
    value = float(v)
    uncertainty = float(unc)
    if uncertainty == 0:
        return value  # avoid log10(0) error

    # Determine the order of magnitude of the uncertainty
    order = math.floor(math.log10(abs(uncertainty)))

    # Round uncertainty to 1 significant digit
    first_digit = round(uncertainty, -order)

    # Determine decimal place to round value
    decimals = -order if order < 0 else 0

    # Round both value and uncertainty
    rounded_value = round(value, decimals)
    rounded_unc = round(uncertainty, decimals)

    return str(rounded_value), str(rounded_unc)


def report_vu(val, low, up):
    value = float(val)
    munc = value - float(low)
    punc = float(up) - value
    if punc <= 0:
        punc += 360
    uncertainty = np.min([munc, punc])
    rounded_value = getsigs(val, uncertainty)
    rounded_low = getsigs(value - float(low), uncertainty)
    rounded_high = getsigs(float(up) - value, uncertainty)
    return f"{rounded_value}$_{{-{rounded_low}}}^{{+{rounded_high}}}$"


def report_vu_old(val, low, up):
    value = float(val)
    uncertainty = np.min([value - float(low), float(up) - value])
    order = math.floor(math.log10(abs(uncertainty)))
    first_digit = round(uncertainty, -order)
    decimals = -order if order < 0 else 0
    rounded_value = round(value, decimals)
    rounded_low = round(value - float(low), decimals)
    rounded_high = round(float(up) - value, decimals)
    return f"{rounded_value}$_{{-{rounded_low}}}^{{+{rounded_high}}}$"


def get_res_stats(tprop):
    rst = open("res_stats.txt", "r").readlines()
    rcr, rar, kcr, kar, fracRes, fracKoz, rtotfrac = (
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
    )
    for tno in rst:
        if tno.split()[0] == tprop or tno.split()[0] == tprop[1:]:
            (
                name,
                rtotfrac1,
                rc,
                rcL,
                rcH,
                fracRes1,
                ra,
                raL,
                raH,
                kc,
                kcL,
                kcH,
                fracKoz1,
                ka,
                kaL,
                kaH,
            ) = tno.split()
            rtotfrac = str(round(float(rtotfrac1)))
            fracRes = str(round(float(fracRes1)))
            fracKoz = str(round(float(fracKoz1)))
            if fracKoz == "-999":
                fracKoz = "--"
            rcr = report_vu(rc, rcL, rcH)
            rar = report_vu(ra, raL, raH)
            if float(kc) < 0:
                kcr = "--"
                kar = "--"
            else:
                # kcr = f"{kc}$\pm${kcu}"
                # kar = f"{ka}$\pm${kau}"
                kcr = report_vu(kc, kcL, kcH)
                kar = report_vu(ka, kaL, kaH)
    return (rcr, rar, kcr, kar, fracRes, fracKoz, rtotfrac)


def mktable_res(tno, rest):
    tprop = tno.split()
    av = getsigs(tprop[18], tprop[19])
    ev = getsigs(tprop[20], tprop[21])
    iv = getsigs(tprop[22], tprop[23])
    dv = getsigs(tprop[10], tprop[11])
    trksub = tprop[5]
    mpcname = getmpcname(trksub)
    cls = f"{tprop[2]}:{tprop[3]}"
    if tprop[0] == "rmm":
        cls += ":m:n"
        for line in mixed_mode_resonances:
            if trksub.lstrip("u") in line:
                cls = line.split(" ", maxsplit=1)[1].rstrip("\n")
    rc, ra, kc, ka, rfrac, kfrac, rtotfrac = get_res_stats(trksub)
    if float(av) > 56:  # Timescale too short for detecting Kozai in distant objects
        kc, ka, kfrac = ("--", "--", "--")
    rescenter = rc
    resamp = ra
    kcen = kc
    kamp = ka
    note = getnote(trksub, notes_res)
    tpos = tprop[18] + "          "
    if float(tprop[18]) > 100:
        tpos = "z" + tpos
    if trksub[0] == "u":
        tpos = "zz" + tpos
    # tnoline =tpos[:12]+trksub+ap+mpcname+ap+cls+ap+tprop[4]+ap+rescenter+ap+resamp+ap+kcen+ap+kamp+ap+tprop[6]+ap+tprop[9]+ap+tprop[18]+pm+tprop[19]+ap+tprop[20]+pm+tprop[21]+ap+tprop[22]+pm+tprop[23]+ap+tprop[10]+pm+tprop[11]+ap+tprop[13]+ap+tprop[12]+ap+note+'\\ \n'
    tnoline = (
        tpos[:12]
        + trksub
        + ap
        + mpcname
        + ap
        + cls
        + ap
        + tprop[4]
        + ap
        + rtotfrac
        + ap
        + rescenter
        + ap
        + resamp
        + ap
        + rfrac
        + ap
        + kcen
        + ap
        + kamp
        + ap
        + kfrac
        + ap
        + note
        + r"\\"
        + " \n"
    )

    # restable.write('test\n')
    rest.append(tnoline)


def mktable1(tno, objt):
    tprop = tno.split()
    trksub = tprop[5]
    sma = float(tprop[18])
    usma = float(tprop[19])
    ecc = float(tprop[20])
    uecc = float(tprop[21])
    qperi = sma * (1 - ecc)
    uqperi = (((1 - ecc) * usma) ** 2 + (-sma * uecc) ** 2) ** 0.5
    av = getsigs(tprop[18], tprop[19])
    ev = getsigs(tprop[20], tprop[21])
    iv = getsigs(tprop[22], tprop[23])
    dv = getsigs(tprop[10], tprop[11])
    qv = getsigs(qperi, uqperi)
    mpcname = getmpcname(trksub)
    note = getnote(trksub, notes_all)
    tpos = tprop[18] + "          "
    if float(tprop[18]) > 100:
        tpos = "z" + tpos
    if trksub[0] == "u":
        tpos = "zz" + tpos
    classif = "fail"
    if tprop[0] == "xxx":
        classif = "Untracked"
        tpos = "z" + tpos
    if tprop[0] == "sca":
        classif = "Scattering"
    if tprop[0] == "det":
        classif = "Detached"
    if tprop[0] == "cen":
        classif = "Centaur"
    if tprop[0] == "res":
        classif = f"{tprop[2]}:{tprop[3]}"
    if tprop[0] == "rmm":
        classif = f"{tprop[2]}:{tprop[3]}:m:m"
        for line in mixed_mode_resonances:
            if trksub.lstrip("u") in line:
                classif = line.split(" ", maxsplit=1)[1].rstrip("\n")
    if tprop[0] == "cla":
        if float(tprop[18]) < 39.5:
            classif = "Inner Hot Classical"
        elif float(tprop[18]) < 47.7:
            classif = "Main Hot Classical"
        else:
            classif = "Extended Hot Classical"
    tnoline = (
        tpos[:12]
        + trksub
        + ap
        + mpcname
        + ap
        + classif
        + ap
        + tprop[4]
        + ap
        + tprop[6]
        + ap
        + tprop[9]
        + ap
        + av
        + ap
        + ev
        + ap
        + iv
        + ap
        + qv
        + ap
        + dv
        + ap
        + tprop[13]
        + ap
        + tprop[12]
        + ap
        + note
        + r"\\"
        + " \n"
    )

    # restable.write('test\n')
    objt.append(tnoline)


rest = []
objt = []

for ob in objs:
    if ob[0] == "r":
        mktable_res(ob, rest)
        mktable1(ob, objt)
    else:
        mktable1(ob, objt)


rest.sort()
uch = False
for r in rest:
    if uch == False:
        if r[12] != "u":
            restable.write(r[12:])
        else:
            restable.write(r"\hline" + "\n")
            restable.write(r[12:])
            uch = True
    else:
        restable.write(r[12:])

objt.sort()
uch = False
xxx = False
for b in objt:
    if uch == False:
        if b[12] == "u":
            objtable.write(r"\hline" + "\n")
            uch = True
        # objtable.write(b[12:])
    if xxx == False:
        if b[26] == "U":
            objtable.write(r"\hline" + "\n")
            xxx = True
    objtable.write(b[12:])


# for b in objt:
#    objtable.write(b[12:])


obj_caption = r"""\footnotesize{
Orbital parameters and other information about every object detected in \lido.
The uncertainty for orbital elements is on the final digit reported.
`Survey ID' is the internal designation that the \lido team gave the object.
`MPC designation' is the provisional designation assigned by the Minor Planet Center, as well as the permanent IAU designation in the two cases where that is available.
`Classification` is the objects class, as determined in \autoref{sec:classify}.
`S/I' indicates whether an object is Securely or Insecurely classified; the first (capital) letter refers to the primary classification, and the second (lower case) letter refers to whether the classification of Kozai or non-Kozai is secure or insecure, while an X indicates a lost object that could not be classified.
`$m_w$ mag' is the average of the three apparent magnitude measurements from the discovery triplets.
`$H_w$ mag' is the absolute magnitude of the object on the discovery night.
`$a$', `$e$', `$i$', `$q$', `dist' are the barycentric semi-major axis, eccentricity, inclination, perihelion distance and distance at discovery. 
`arc lenth' is the observed arc length and `nobs' is the number of measurements.
`Notes' contain any additional notes, such as when objects were observed with telescopes other than CFHT.
}"""
res_caption = r"""\footnotesize{
Additional information to the information presented in \autoref{tab:objects} for the resonant object. 
`Survey ID' is the internal designation that the \lido team gave the object.
`MPC designation' is the provisional designation assigned by the Minor Planet Center, as well as the permanent IAU designation in the cases where that is available.
`Resonance` is the objects class, as determined in \autoref{sec:classify}.
`S/I' indicates whether an object is Securely or Insecurely classified; the first (capital) letter refers to the primary classification, and the second (lower case) letter refers to whether the classification of Kozai or non-Kozai is secure or insecure, while an X indicates a lost object that could not be classified.
`Res Frac' is the percentage of the 201 clones that showed resonant behavious.
`RC' is the resonant center (the angle around which the resonant angle librates).
`RA' is the amplitude (peak to valley) of the resonant angle libration.
`Island Frac' is the percentage of the resonant clones that resonate within the same resonance island.
`KC' is the center value of $\omega$ for objects that feature Kozai resonance.
`KA' is the amplitude of Kozai resonance.
`KFrac' is the fraction of resonant clones that show Kozai resonant behavior for the entire 30~Myr integration. 
}"""
restable.write(
    r"\hline\hline"
    + "\n"
    + r"\end{longtable}"
    + "\n"
    + res_caption
    + "\n"
    + r"\end{longrotatetable}"
)
objtable.write(
    r"\hline\hline"
    + "\n"
    + r"\end{longtable}"
    + "\n"
    + obj_caption
    + "\n"
    + r"\end{longrotatetable}"
)


restable.close()
objtable.close()
