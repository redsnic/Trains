# script to execute the ASP an MZN solvers on a folder
# $1 = OUTPUT folder
# $2 = INPUT folder

inputF=$2
outputF=$1

if [ -d $inputF ]
then
    echo "input folder found: $inputF"
else
    echo "input folder not found"
    exit 255
fi
     
if [ -d $outputF ]
then
    echo "output folder found, rewriting results if needed: $outputF"
else
    mkdir $outputF
    echo "created output folder"
fi

echo "starting, timeout set to 300s ( 5 mins )"

for f in `ls $inputF` 
do
    echo "executing MZN for $outputF/`basename $f .in` ..."
    timeout --kill-after=300 300 python2.7 MinizincEncoding.py $outputF/`basename $f .in` < $inputF/$f || echo "TIMEOUT" > $outputF/`basename $f .in`.solMZN
    echo "executing ASP for $outputF/`basename $f .in` ..."
    timeout --kill-after=300 300 python2.7 ASPEncodingv3.py $outputF/`basename $f .in` < $inputF/$f || echo "TIMEOUT" > $outputF/`basename $f .in`.solASP
done
echo "completed!"
