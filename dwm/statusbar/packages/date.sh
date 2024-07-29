#! /bin/bash
# DATE 获取日期和时间的脚本

tempfile=$(
  cd $(dirname $0)
  cd ..
  pwd
)/temp

this=_date
icon_color="^c#25513e^^b#00ff900x88^"
text_color="^c#25513e^^b#00ff900x99^"
signal=$(echo "^s$this^" | sed 's/_//')

update() {
  time_text="$(date '+%m/%d %H:%M')"
  case "$(date '+%I')" in
  "01") time_icon="" ;;
  "02") time_icon="" ;;
  "03") time_icon="" ;;
  "04") time_icon="" ;;
  "05") time_icon="" ;;
  "06") time_icon="" ;;
  "07") time_icon="" ;;
  "08") time_icon="" ;;
  "09") time_icon="" ;;
  "10") time_icon="" ;;
  "11") time_icon="" ;;
  "12") time_icon="" ;;
  esac

  icon=" $time_icon "
  text=" $time_text "

  sed -i '/^export '$this'=.*$/d' $tempfile
  printf "export %s='%s%s%s%s%s'\n" $this "$signal" "$icon_color" "$icon" "$text_color" "$text" >>$tempfile
}

notify() {
  _cal=$(cal --color=always | sed 1,2d | sed 's/..7m/<b><span color="#ff79c6">/;s/..0m/<\/span><\/b>/')
  _todo=$(cat ~/.todo.md | sed 's/\(- \[x\] \)\(.*\)/<span color="#ff79c6">\1<s>\2<\/s><\/span>/' | sed 's/- \[[ |x]\] //')
  notify-send "󰨲  Calendar" "\n$_cal\n————————————————————\n$_todo" -r 9527
}

click() {
  case "$1" in
  L) notify ;;
  esac
}

case "$1" in
click) click $2 ;;
notify) notify ;;
*) update ;;
esac
