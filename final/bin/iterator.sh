#!/bin/bash
#
# Collect period failures into a single file.

# The file receiving the accumulated info
FILE=~/tmp/period-failures.csv

# Header line
echo "simId,trialNum,scenario,periods" > $FILE

COMMAND=\
"if [ -e \"{expDir}/exe/failed_periods.txt\" ]; then\
   periods=\`cat \"{expDir}/exe/failed_periods.txt\"\`;\
   echo \"{simId},{trialNum},{scenario},\$periods\" >> $FILE;\
fi"

gt iterate -S base -t 0-4 -c "$COMMAND"
