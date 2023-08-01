#!/bin/bash
: "${1?Must provide a Jira ticket ID with nodes in maintenance pool}"
: "${2?Must provide an active BKC Checker}"
JIRA_ID=$1
BKCCHECKER=$2
export JIRA_ID='$1'
export BKCCHECKER='$2'
echo $1 > jira.txt
echo $2 > bkc.txt
if python -c "import tqdm, xlsxwriter" &> /dev/null; then
    python x.py
else
    pip install --proxy="http://proxy-us.intel.com:911" tqdm
    pip install --proxy="http://proxy-us.intel.com:911" xlsxwriter
    python x.py
fi
