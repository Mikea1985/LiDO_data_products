rm abgaeipred_dsc.all

ln -s ../ast.all .
cat ast.all | grep "*.C" | grep -v published | colrm 1 9 | colrm 6 5 | colrm 4 5 | colrm 9 9 | colrm 11 11 | colrm 13 | sort | uniq | while read line
do
    field=`echo $line | awk '{print $1}'`
    date=`echo $line | awk '{print $2}'`
    echo $field
    echo $date
    for i in {00..39}
    do
        cat ../abgaeipred_${date}.3877.all | grep -A5 "${i}${field} at" | grep -v "\-\-" >> abgaeipred_disc.all
    done
done
