echo '


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
--------------------|-----------|-----------|------|-----|' > PH2_disc.xml

ln -s ../ast.all .
cat ast.all | grep "*.C" | grep -v published | while IFS= read line
do
    exp=`echo "$line" | colrm 1 85 | colrm 8`
    field=`echo "$line" | colrm 13 | colrm 1 9`
    cat ../PH2_20*xml | grep "$exp" | sed "s/$exp    /${exp}_$field/"
done | sort | uniq >> PH2_disc.xml

echo "]]></CSV></DATA>" >> PH2_disc.xml
echo "  </TABLE>" >> PH2_disc.xml
echo "</ASTRO>" >> PH2_disc.xml

