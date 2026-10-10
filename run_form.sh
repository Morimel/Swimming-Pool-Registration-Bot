#!/bin/zsh
# Usage: ./run_form.sh            -> real booking
#        DRY_RUN=1 ./run_form.sh  -> fill the form but don't submit
cd "$(dirname "$0")" || exit 1
export HEADLESS="${HEADLESS:-1}"
echo "=== $(date '+%F %T')" >> form.log
./form-bot/venv/bin/python -u form_book.py 2>&1 | tee -a form.log
exit ${pipestatus[1]}
