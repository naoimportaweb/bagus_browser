
sudo /bin/bash {BROWSER_PATH}/bash/create.sh {USERNAME}
[ ! -f /tmp/{USERNAME}/ad_hosts_block.txt ] && wget -O /tmp/{USERNAME}/ad_hosts_block.txt https://raw.githubusercontent.com/naoimportaweb/bagus_browser/refs/heads/main/lists/ad_hosts_block.txt  || echo "Lista de bloqueios existe"


