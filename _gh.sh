GIT_DIR_STRING=$(git rev-parse --git-dir 2>/dev/null)
MAX_ITEMS_SHOWN=8

usage()
{
gst_filename=$(basename $0)
echo -e "
usage: ${gst_filename} [-h|--help] [-v] [REF_NUM] [-n ITEM_LIMIT] [-s SEARCH_STRING]
       ${gst_filename} [-c REF_NUM] [-d REF_NUM]

  -h, --help           display help

  -v                   show all branch references in history

  REF_NUM              print the name of the branch referenced by REF_NUM

  -n ITEM_LIMIT        show the most recent branches limited by the number provided by ITEM_LIMIT

  -s SEARCH_STRING     display a list of matches of branch references in the history and display their corresponding REF_NUM

  -c REF_NUM           eq to \033[32mgit checkout \033[31m <BRANCH_REF> \033[m where \033[31m<BRANCH_REF>\033[m is replaced with the branch referenced by REF_NUM

  -d REF_NUM           delete all occurances of a branch reference in history
"
}

if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
  usage
  exit 0;
fi

# Used to determine if the parameter is an integer
SELECT_NUM=$(echo "$1" | egrep '^(\d+)$')

if [ "$GIT_DIR_STRING" == "" ]; then
  echo "fatal: Not a git repository";
else
  LINE=$(expr $1 2>/dev/null)
  FILE="$GIT_DIR_STRING/logs/HEAD"

  while getopts ":n:c:s:d:v" opt; do
    case "${opt}" in
    d)
      HEAD_FILE_TEXT=$(cat $FILE)
      # Backup file before modifying, but only if file is not empty
      HEAD_FILE_LENGTH=${#HEAD_FILE_TEXT}
      if [ $HEAD_FILE_LENGTH == 0 ]; then
        cp $GIT_DIR_STRING/logs/HEAD $GIT_DIR_STRING/logs/HEAD.bak
      fi
      BRANCH_TEXT=$(gh ${OPTARG} | xargs echo -n)
      HEAD_FILE_CLEANED=$(cat $FILE | egrep -v 'to (?='${BRANCH_TEXT}')') # v flag means get the results that don't match
      # Check if result succeeded before overwriting file
      if [ $? == '0' ]; then
        printf "$HEAD_FILE_CLEANED\n" > $FILE
      fi
      exit 0;
      ;;

    n)
      MAX_ITEMS_SHOWN=$(expr $(echo ${OPTARG} | egrep '^(\d+)$'))
      if [ $MAX_ITEMS_SHOWN == "" ]; then
        echo "Integer argument needed for '-n'"
        exit -1;
      fi
      ;;
    v)
      MAX_ITEMS_SHOWN=1000
      ;;
    s)
      echo ''
      gh -v | egrep -i ${OPTARG} | awk '{print "\033[31m"$1"\033[0m " $2;}'
      echo ''
      exit 0;
      ;;
    c)
      git checkout $(gh ${OPTARG})
      exit -1;
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      usage
      exit -1;
      ;;
    esac
  done


  # old method using sed to get the best match
  #RESULT_STRING=`sed -n 's/^.*from \(\S*\) to.*$/\1/p' $FILE | sed -n "$LINEp" 2>/dev/null`

  # First command (awk) gets last column if second last column matches "to"
  # Second command (sed) reverses the order.
  # Third command (awk) removes duplicates via associative array.
  RESULT_STRING=`awk '{if ($(NF-4) == "moving" && $(NF-3) == "from") {print $(NF);}}' $FILE | sed '1!G;h;$!d' | awk 'BEGIN {i=0;} { if (!($1 in ar) && !(match($1,"(^HEAD|^refs/)"))) { ar[$1]; list[i++]=$1; } } END {for (i = 1; i in list; i++) {print list[i]; }  }'`

  MATCHES=${RESULT_STRING}
  MATCHES=($RESULT_STRING)
  TMP_COUNT=0

  if [ "$1" == "" ] || [ "$1" == "-v" ] || [ "$1" == "-n" ]; then
    if [ "$RESULT_STRING" == "" ]; then
      echo "No checkout history";
    else
      for RESULT in "${MATCHES[@]}"
      do
        if [ "${TMP_COUNT}" -le $MAX_ITEMS_SHOWN ]; then
          echo "${TMP_COUNT}. $RESULT"
          TMP_COUNT=$(expr $TMP_COUNT + 1)
        fi
      done
    fi
  # elif [ "$1" == "0" ];
    # then
      # git checkout HEAD
  # elif [ "${#MATCHES[@]}" == 1 ];
    # then
      # git checkout "${MATCHES[$LINE]}"
  elif [ "$SELECT_NUM" != "" ]; then
    if [ "$SELECT_NUM" -le "${#MATCHES[@]}" ]; then
      echo "${MATCHES[$SELECT_NUM]}"
    else
      echo "Invalid selection, unable to reference";
      exit -1;
    fi
  fi # SELECT_NUM
fi # GIT_DIR_STRING