#!/bin/bash 

#!/bin/bash 

function oops {
	echo
	echo -n '*** oops, '$1' ***'
	echo
	exit 86
}

python3 src/stpolls_main_analyze.py

SUFFIX='poll_plots'

if [ -d $SUFFIX ]; then
    rm -rf $SUFFIX
    if [ $? -ne 0 ]; then
        exit 86
    fi
fi
mkdir $SUFFIX
if [ $? -ne 0 ]; then
    exit 86
fi

python3 src/stpolls_main_plot.py

