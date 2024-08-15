import numpy as np


objABCDE = open('../Orbits/LiDO_ABCDE.detections').readlines()[3:]
objTUV = open('../Orbits/LiDO_TUV.detections').readlines()[3:]
notes = open('../Orbits/notes.txt').readlines()[1:]
names = open('../Orbits/correspondence.txt').readlines()

restable = open('../PaperProducts/resTable2.txt','w')
objtable = open('../PaperProducts/objsTable1.txt','w')


#restable.write("\\begin{table}[h!]\n\setlength{\\tabcolsep}{2.5pt}\n\caption{Resonant \lido Survey Objects}\n\label{tab:resobjects}\n\\begin{center}\n\\begin{tabular}{ c  c  c | c  c  c  c c c c c c c c c c | c c} \nSurvey Name & MPC Name & Resonance & S/I & RC & RA & KC & KA & $m_r$ & $H_r$ & $a$ & $e$ & $i$ & dist & arc length & nobs &Notes \\\\ \\hline\n")
restable.write("\\begin{longtable}{ll|cccccccccccccc | cc}\n\caption{Resonant \lido Survey Objects} \label{tab:resobjects}\\\\\n\\hline\\hline\\\\\nSurvey Name & MPC Name & Resonance & S/I & RC & RA & KC & KA & $m_r$ & $H_r$ & $a$ & $e$ & $i$ & dist & arc length & nobs &Notes \\\\ \\hline\n \endhead")
#objtable.write("\\begin{table}[h!]\n\setlength{\\tabcolsep}{2.5pt}\n\caption{\lido Survey Objects}\n\label{tab:objects}\n\\begin{center}\n\\begin{tabular}{ c  c  c | c  c  c  c c c c c c | c c} \nSurvey Name & MPC Name & Classification &S/I & $m_r$ & $H_r$ & $a$ & $e$ & $i$ & dist & arc length & nobs &Notes \\\\ \\hline\n")
objtable.write("\\begin{longtable}{ll|cccccccccc | cc}\n\caption{Non-Resonant \lido Survey Objects} \label{tab:objects}\\\\\n\\hline\\hline\\\\\nSurvey Name & MPC Name & Classification & S/I & $m_r$ & $H_r$ & $a$ & $e$ & $i$ & dist & arc length & nobs &Notes \\\\ \\hline\n \endhead")


objs = objABCDE + objTUV
ap = ' & '
pm = '$'+'\\'+'pm$'

def getmpcname(sname):
    mpc = ''
    for obj in names:
        if obj.split()[0]==sname:
            for n in obj.split():
                if n[0]=='K':
                    print(n)
                    mpc=n
    return(mpc)
    
def getnote(sname):
    note=''
    for n in notes:
        if n.split()[0]==sname:
            note = n[len(n.split()[0])+1:]
    return(note)

def getsigs(v,dv):
    sg = dv.count('0')
    vr = str(round(float(v), sg))
    return(vr)

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
    rescenter=''
    resamp=''
    kcen=''
    kamp=''
    note=getnote(tprop[5])
    tpos=tprop[18]+'          '
    if float(tprop[18])>100:
        tpos='z'+tpos
    if tprop[5][0]=='u':
        tpos='zz'+tpos
    #tnoline =tpos[:12]+tprop[5]+ap+mpcname+ap+tprop[2]+':'+tprop[3]+mm+ap+tprop[4]+ap+rescenter+ap+resamp+ap+kcen+ap+kamp+ap+tprop[6]+ap+tprop[9]+ap+tprop[18]+pm+tprop[19]+ap+tprop[20]+pm+tprop[21]+ap+tprop[22]+pm+tprop[23]+ap+tprop[10]+pm+tprop[11]+ap+tprop[13]+ap+tprop[12]+ap+note+'\\\\ \n'
    tnoline =tpos[:12]+tprop[5]+ap+mpcname+ap+tprop[2]+':'+tprop[3]+mm+ap+tprop[4]+ap+rescenter+ap+resamp+ap+kcen+ap+kamp+ap+tprop[6]+ap+tprop[9]+ap+av+ap+ev+ap+iv+ap+dv+ap+tprop[13]+ap+tprop[12]+ap+note+'\\\\ \n'

    
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

    
#restable.write("\end{tabular}\n\end{center}\n\\footnotesize{Orbits are barycentric. The uncertainty is on the final digit reported. XXX.}\n\\bigskip\n\\bigskip\n\end{table}")

restable.write("\hline\hline\n\end{longtable}\n\\footnotesize{Orbits are barycentric. The uncertainty is on the final digit reported. XXX.}")
objtable.write("\hline\hline\n\end{longtable}\n\\footnotesize{Orbits are barycentric. The uncertainty is on the final digit reported. XXX.}")



restable.close()
objtable.close()
