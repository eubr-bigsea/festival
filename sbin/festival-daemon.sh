#!/usr/bin/env bash

# This script controls the festival server daemon initialization, status reporting
# and termination
# TODO: rotate logs

usage="Usage: festival-daemon.sh (start|startf|stop|status)"

# this sript requires the command parameter
if [ $# -le 0 ]; then
  echo $usage
  exit 1
fi

# parameter option
cmd_option=$1

# set festival_home if unset
if [ -z "${FESTIVAL_HOME}" ]; then
  export FESTIVAL_HOME="$(cd "`dirname "$0"`"/..; pwd)"
fi
echo $FESTIVAL_HOME

# get log directory
if [ "$FESTIVAL_LOG_DIR" = "" ]; then
  export FESTIVAL_LOG_DIR="${FESTIVAL_HOME}/logs"
fi
mkdir -p "$FESTIVAL_LOG_DIR"

# get pid directory
if [ "$FESTIVAL_PID_DIR" = "" ]; then
  export FESTIVAL_PID_DIR=/tmp
fi
mkdir -p "$FESTIVAL_PID_DIR"

# log and pid files
log="$FESTIVAL_LOG_DIR/festival-server-$USER-$HOSTNAME.out"
pid="$FESTIVAL_PID_DIR/festival-server-$USER.pid"

case $cmd_option in

   (start)
      # set python path
      PYTHONPATH=$FESTIVAL_HOME:$PYTHONPATH python $FESTIVAL_HOME/festival/manage.py \
         db upgrade || true
      PYTHONPATH=$FESTIVAL_HOME:$PYTHONPATH nohup -- python $FESTIVAL_HOME/festival/app.py \
         -c $FESTIVAL_HOME/conf/festival-config.yaml >> $log 2>&1 < /dev/null &
      festival_server_pid=$!

      # persist the pid
      echo $festival_server_pid > $pid

      echo "Festival server started, logging to $log (pid=$festival_server_pid)"
      ;;

   (startf)
      trap "$0 stop" SIGINT SIGTERM
      # set python path
      PYTHONPATH=$FESTIVAL_HOME:$PYTHONPATH python $FESTIVAL_HOME/festival/manage.py \
         db upgrade || true
      PYTHONPATH=$FESTIVAL_HOME:$PYTHONPATH python $FESTIVAL_HOME/festival/app.py \
         -c $FESTIVAL_HOME/conf/festival-config.yaml &
      festival_server_pid=$!

      # persist the pid
      echo $festival_server_pid > $pid

      echo "Festival server started, logging to $log (pid=$festival_server_pid)"
      wait
      ;;

   (stop)

      if [ -f $pid ]; then
         TARGET_ID="$(cat "$pid")"
         if [[ $(ps -p "$TARGET_ID" -o comm=) =~ "python" ]]; then
            echo "stopping festival server, user=$USER, hostname=$HOSTNAME"
            (pkill -SIGTERM -P "$TARGET_ID" && \
               kill -SIGTERM "$TARGET_ID" && \
               rm -f "$pid")
         else
            echo "no festival server to stop"
         fi
      else
         echo "no festival server to stop"
      fi
      ;;

   (status)

      if [ -f $pid ]; then
         TARGET_ID="$(cat "$pid")"
         if [[ $(ps -p "$TARGET_ID" -o comm=) =~ "python" ]]; then
            echo "festival server is running (pid=$TARGET_ID)"
            exit 0
         else
            echo "$pid file is present (pid=$TARGET_ID) but festival server not running"
            exit 1
         fi
      else
         echo festival server not running.
         exit 2
      fi
      ;;

   (*)
      echo $usage
      exit 1
      ;;
esac
