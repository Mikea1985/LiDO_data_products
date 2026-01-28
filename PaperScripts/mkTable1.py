import numpy as np
import math

objABCDE = open('../Orbits/LiDO_ABCDE.detections').readlines()[3:]
objTUV = open('../Orbits/LiDO_TUV.detections').readlines()[3:]
notes = open('../Orbits/notes.txt').readlines()[1:]
names = open('../Orbits/correspondence.txt').readlines()

restable = open('../PaperProducts/resTable2.txt','w')
objtable = open('../PaperProducts/objsTable1.txt','w')


#restable.write("\\begin{table}[h!]\\n\setlength{\\tabcolsep}{2.5pt}\n\caption{Resonant \lido Survey Objects}\n\label{tab:resobjects}\n\\begin{center}\n\\begin{tabular}{ c  c  c | c  c  c  c c c c c c c c c c | c c} \nSurvey Name & MPC Name & Resonance & S/I & RC & RA & KC & KA & $m_r$ & $H_r$ & $a$ & $e$ & $i$ & dist & arc length & nobs &Notes \\\\ \\hline\n")
#objtable.write("\\begin{table}[h!]\n\setlength{\\tabcolsep}{2.5pt}\n\caption{\lido Survey Objects}\n\label{tab:objects}\n\\begin{center}\n\\begin{tabular}{ c  c  c | c  c  c  c c c c c c | c c} \nSurvey Name & MPC Name & Classification &S/I & $m_r$ & $H_r$ & $a$ & $e$ & $i$ & dist & arc length & nobs &Notes \\\\ \\hline\n")


restable.write("\\begin{longrotatetable}\n\\setlength{\\tabcolsep}{2pt}\n\\tablewidth{10in}\n\\tabletypesize{\\footnotesize}\n\\begin{longtable}{ll|ccccccccccccccccc | l}\n\\caption{Resonant \\lido Survey Objects} \\label{tab:resobjects}\\\\\n\\hline\\hline\\\\\nSurvey & MPC & Resonance & S/I & Res Frac& RC & RA &Island Frac& KC & KA & KFrac & $m_r$ & $H_r$ & $a$ & $e$ & $i$ & dist & arc length & nobs &Notes \\\\ \nName & Name &  &  & \\% & $\\degr$ & $\\degr$ &\\%& $\\degr$ & $\\degr$ & \\% & mag & mag & au &  & $\\degr$ & au & years &  & \\\\\\hline \\hline\n \\endhead\n")
objtable.write("\\begin{longrotatetable}\n\\setlength{\\tabcolsep}{2pt}\n\\tablewidth{10in}\n\\tabletypesize{\\footnotesize}\n\\begin{longtable}{ll|cccccccccc | l}\n\\caption{Non-Resonant \\lido Survey Objects} \\label{tab:objects}\\\\\n\\hline\\hline\\\\\nSurvey & MPC & Classification & S/I & $m_r$ & $H_r$ & $a$ & $e$ & $i$ & dist & arc length & nobs &Notes \\\\\nName & Name &  &  & mag & mag & au &  & $\\degr$ & au & years &  & \\\\\\hline\\hline\n \\endhead\n")


objs = objABCDE + objTUV
ap = ' & '
pm = '$'+'\\'+'pm$'

def getmpcname(sname):
    mpc = ''
    for obj in names:
        if obj.split()[0]==sname:
            for n in obj.split():
                if n[0]=='K':
                    #print(n)
                    mpc=n
    return(mpc)
    
def getnote(sname):
    notelist = open('../Orbits/notes.txt','r').readlines()
    note=''
    for n in notelist:
        if len(n)>1:
            if n.split()[0]==sname:
                note = note+ n[len(n.split()[0])+1:].strip('\n')+'  '
                print(note)
    return(note)

def getsigs(v,dv):
    sg = dv.count('0')
    vr = str(round(float(v), sg))
    return(vr)

def report_value(v, unc):
    value=float(v)
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
    value=float(val)
    uncertainty = np.min([value - float(low), float(up)-value])
    order = math.floor(math.log10(abs(uncertainty)))
    first_digit = round(uncertainty, -order)
    decimals = -order if order < 0 else 0
    rounded_value = round(value, decimals)
    rounded_low = round(value-float(low), decimals)
    rounded_high = round(float(up)-value, decimals)
    return(f"{rounded_value}$_{{-{rounded_low}}}^{{+{rounded_high}}}$")

def get_res_stats(tprop):
    rst = open('res_stats.txt','r').readlines()
    rcr, rar, kcr, kar, fracRes, fracKoz,rtotfrac = '--','--','--','--','--','--','--'
    for tno in rst:
        if tno.split()[0]==tprop or tno.split()[0]==tprop[1:]:
            name, rtotfrac1, rc, rcL,rcH,fracRes1, ra, raL, raH, kc, kcL, kcH, fracKoz1, ka,kaL,kaH = tno.split()
            rtotfrac = str(round(float(rtotfrac1)))
            fracRes = str(round(float(fracRes1)))
            fracKoz = str(round(float(fracKoz1)))
            if fracKoz == '-999':
                fracKoz = '--'
            rcr = report_vu(rc, rcL, rcH)
            rar = report_vu(ra, raL, raH)
            if float(kc)<0:
                kcr='--'
                kar = '--'
            else:
                #kcr = f"{kc}$\\pm${kcu}"
                #kar = f"{ka}$\\pm${kau}"
                kcr = report_vu(kc,kcL,kcH)
                kar = report_vu(ka,kaL,kcH)
    return(rcr,rar,kcr,kar,fracRes,fracKoz,rtotfrac)

def mktable_res(tno,rest):
    tprop = tno.split()
    mm=''
    av=getsigs(tprop[18],tprop[19])
    ev=getsigs(tprop[20],tprop[21])
    iv=getsigs(tprop[22],tprop[23])
    dv=getsigs(tprop[10],tprop[11])
    mpcname=getmpcname(tprop[5])
    if tprop[0]=='rmm':
        mm=':m:n'
    rc,ra,kc,ka,rfrac,kfrac,rtotfrac = get_res_stats(tprop[5])
    rescenter=rc
    resamp=ra
    kcen=kc
    kamp=ka
    note=getnote(tprop[5]) 
    tpos=tprop[18]+'          '
    if float(tprop[18])>100:
        tpos='z'+tpos
    if tprop[5][0]=='u':
        tpos='zz'+tpos
    #tnoline =tpos[:12]+tprop[5]+ap+mpcname+ap+tprop[2]+':'+tprop[3]+mm+ap+tprop[4]+ap+rescenter+ap+resamp+ap+kcen+ap+kamp+ap+tprop[6]+ap+tprop[9]+ap+tprop[18]+pm+tprop[19]+ap+tprop[20]+pm+tprop[21]+ap+tprop[22]+pm+tprop[23]+ap+tprop[10]+pm+tprop[11]+ap+tprop[13]+ap+tprop[12]+ap+note+'\\\\ \n'
    tnoline =tpos[:12]+tprop[5]+ap+mpcname+ap+tprop[2]+':'+tprop[3]+mm+ap+tprop[4]+ap+rtotfrac+ap+rescenter+ap+resamp+ap+rfrac+ap+kcen+ap+kamp+ap+kfrac+ap+tprop[6]+ap+tprop[9]+ap+av+ap+ev+ap+iv+ap+dv+ap+tprop[13]+ap+tprop[12]+ap+note+'\\\\ \n'

    
    #restable.write('test\n')
    rest.append(tnoline)
    

def mktable1(tno,objt):
    tprop = tno.split()
    av=getsigs(tprop[18],tprop[19])
    ev=getsigs(tprop[20],tprop[21])
    iv=getsigs(tprop[22],tprop[23])
    dv=getsigs(tprop[10],tprop[11])
    mpcname=getmpcname(tprop[5])
    note=getnote(tprop[5]) 
    tpos=tprop[18]+'          '
    if float(tprop[18])>100:
        tpos='z'+tpos
    if tprop[5][0]=='u':
        tpos='zz'+tpos
    classif='fail'
    if tprop[0]=='xxx':
        classif='Untracked'
        tpos='z'+tpos
    if tprop[0]=='sca':
        classif='Scattering'
    if tprop[0]=='det':
        classif='Detached'
    if tprop[0]=='cla':
        if float(tprop[18])<39.5:
            classif='Inner Hot Classical'
        elif float(tprop[18])<47.7:
            classif='Main Hot Classical'
        else:
            classif='Extended Hot Classical'
    tnoline =tpos[:12]+tprop[5]+ap+mpcname+ap+classif+ap+tprop[4]+ap+tprop[6]+ap+tprop[9]+ap+av+ap+ev+ap+iv+ap+dv+ap+tprop[13]+ap+tprop[12]+ap+note+'\\\\ \n'
    
    #restable.write('test\n')
    objt.append(tnoline)


rest=[]
objt=[]
    
for ob in objs:
    if ob[0] =='r':
        mktable_res(ob,rest)
    else:
        mktable1(ob,objt)


rest.sort()
uch=False
for r in rest:
    if uch==False:
        if r[12]!='u':
            restable.write(r[12:])
        else:
            restable.write("\\hline\n")
            restable.write(r[12:])
            uch=True
    else:
        restable.write(r[12:])

objt.sort()
uch=False
xxx=False
for b in objt:
    if uch==False:
        if b[12]=='u':
            objtable.write("\\hline\n")
            uch=True
        #objtable.write(b[12:])
    if xxx==False:
        if b[26]=='U':
            objtable.write("\\hline\n")
            xxx=True
    objtable.write(b[12:])
                   

#for b in objt:
#    objtable.write(b[12:])

obj_caption = """\footnotesize{
Orbital parameters and other information about every object detected in \lido.
The uncertainty for orbital elements is on the final digit reported.
`Survey Name' is the internal designation that the \lido team gave the object.
`MPC Name' is the provisional designation assigned by the Minor Planet Center\footnote{This column will be filled in upon acceptance for publication.}.
`Classification` is the objects class, as determined in \autoref{sec:classify}.
`S/I' indicates whether an object is Securely or Insecurely classified; the first (capital) letter refers to the primary classification, and the second (lower case) letter refers to the classification of whether an object is also a Kozai resonator, while an X indicates a lost object that could not be classified.
`$m_w$ mag' is the average of the three apparent magnitude measurements from the discovery triplets.
`$H_w$ mag' is the absolute magnitude of the object on the discovery night.
`$a$', `$e$', `$i$' and `dist' are the barycentric semi-major axis, eccentricity, inclination and distance at discovery. 
`arc lenth' is the observed arc length and `nobs' is the number of measurements.
`Notes' contain any additional notes, such as when objects were observed with telescopes other than CFHT.
}"""
res_caption = """\footnotesize{
Additional information to the information presented in \autoref{tab:objects} for the resonant object. 
`Survey Name' is the internal designation that the \lido team gave the object.
`MPC Name' is the provisional designation assigned by the Minor Planet Center\footnote{This column will be filled in upon acceptance for publication.}.
`Resonance` is the objects class, as determined in \autoref{sec:classify}.
`S/I' indicates whether an object is Securely or Insecurely classified; the first (capital) letter refers to the primary classification, and the second (lower case) letter refers to the classification of whether an object is also a Kozai resonator.
`Res Frac' is the percentage of the 201 clones that showed resonant behavious.
`RC' is the resonant center (the angle around which the resonant angle librates).
`RA' is the amplitude (peak to valley) of the resonant angle libration.
`Island Frac' is the percentage of the resonant clones that resonate within the same resonance island.
`KC' is the center value of $\omega$ for objects that feature Kozai resonance.
`KA' is the amplitude of Kozai resonance.
`KFrac' is the fraction of resonance clones that show Kozai resonant behavior. 
}"""
restable.write("\\hline\\hline\n\\end{longtable}\n"+res_caption+"\n\\end{longrotatetable}")
objtable.write("\\hline\\hline\n\\end{longtable}\n"+obj_caption+"\n\\end{longrotatetable}")



restable.close()
objtable.close()
