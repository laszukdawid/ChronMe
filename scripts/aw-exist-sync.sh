# Hey,
# I know you don't know me, and mum said not to trust strangers,
# but this time we should really make an exception. Ok?
# You see that --> {PROJECT_ROOT} <-- ? (ignore arrows, they're for the drama effect)
# Please go ahead and update them with your project root directory.
PROJECT_ROOT=
cd $PROJECT_ROOT
log_file=~/.chronme/`date +%y-%m-%d`
echo "####################  Starting  ####################" >> $log_file
echo "Date: `date`" >> $log_file
env "PYTHONIOENCODING=UTF-8" "PYTHONUNBUFFERED=1" $PROJECT_ROOT/venv/bin/python $PROJECT_ROOT/src/aw-exist-sync.py >> $log_file
