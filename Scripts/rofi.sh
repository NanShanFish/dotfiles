# 打印菜单
call_menu() {
  echo -e ' notes\n cpp\n setting\n󰂯 bluetooth\n⏻ poweroff\n󰑓 reboot'
  # [ "$(sudo docker ps | grep v2raya)" ] && echo ' close v2raya' || echo ' open v2raya'
  [ "$(ps aux | grep picom | grep -v 'grep\|rofi\|nvim')" ] && echo ' close picom' || echo ' open picom'
}

# 执行菜单
execute_menu() {
  case $1 in
  ' notes')
    neovide ~/Documents/markdown &
    ;;
  ' cpp')
    neovide ~/Documents/cpp &
    ;;
  ' setting')
    eww open eww &
    ;;
  '󰂯 bluetooth')
    sh ~/Scripts/bluetooth.sh &
    ;;
  ' open picom')
    coproc (picom --experimental-backends --config ~/Scripts/config/picom.conf >/dev/null 2>&1)
    ;;
  ' close picom')
    killall picom
    ;;
  '⏻ poweroff')
    poweroff
    ;;
  '󰑓 reboot')
    reboot
    ;;
  esac
}

execute_menu "$(call_menu | rofi -dmenu -matching prefix -p "")"
