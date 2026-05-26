#!/bin/bash
# Script de instalação do KFM, que deverá ser alocado em /opt/
#    deste script sáo disparados as instalações de pacotes tanto
#    do Linux quanto do Python

# CORES para melhorar layout do instalador
export BLUE='\033[1;94m'
export GREEN='\033[1;92m'
export RED='\033[1;91m'
export RESETCOLOR='\033[1;00m'

DIR=/opt/bagusbagusgo    #Diretório padrão de instalação
URL='https://codeload.github.com/naoimportaweb/bagus_browser/zip/refs/heads/main'

# Lista de pacotes Linux que serão instalados ou atualizados
packages=("python3-pip" "unzip" "tor" "python3-pip")
apt install cryptsetup -y
#TODO: PARA CADA PROJETO TEM QUE DIZER QUAL PACOTE AQUI..... E DESCREVER CADA UM

touch /etc/pip.conf
echo '[global]' > /etc/pip.conf
echo 'break-system-packages = true' >> /etc/pip.conf


# se é uma maquina de desenvolvedor, nao pode trazer do sourceforge
#    pois pode substituir arquivos novos por antigos, o programador pode
#    estar cansado e acabar errando, DESENVOLVERO só por github
if [ -L ${DIR} ] ; then
    echo "O diretório ${DIR} nao pode ser usado pois é um link simbólico."
    exit 0
fi

# Para evitar que pessoas desavisadas façam instalação sem 
#    poder para isso, o correto [e usar SUDO]
if [ "$EUID" -ne 0 ]
  then echo "Please run as root or sudo/Por favor, execute como root ou sudo"
  exit
fi


# verifica se existe o pacote no repositório
existspackage(){
    retorno="`apt-cache show $1`"
    SUB='No packages found'

    if grep -q "$retorno" <<< "$STR"; then
        return 1
    else
        return 0
    fi
}

# funçao que verifica se o pacote já está instalado na maquina
instaledpackage(){
    retorno="`dpkg-query -W $1`"
    SUB='no packages found matching'

    if grep -q "$retorno" <<< "$STR"; then
        return 1
    else
        return 0
    fi
}

# Dada a lista de pacotes para Linux, fazer laço que verifica tudo
#    nao pode passar se faltar alguma coisa
for str in ${packages[@]}; do
    if instaledpackage ${str} ; then
        echo "[.] Já possui ${str};"
    else
        if existspackage ${str} ; then
            echo "[+] Será instalado ${str};"
        else
            echo "$RED [*]O pacote ${str} não existe. Por isso não pode ser instalado. Consulte manual de sua distribuição ou instale manualmente$RESETCOLOR"
            exit 1
        fi
    fi
done

# se chegou ate aqui, tudo tem, entáo tem que agora instalar
for str in ${packages[@]}; do
    echo "[+] Instalação do pacote ${str}"
    apt install ${str} -y &> /dev/null
    
done

# vamos verificar se instalou tudo.....
for str in ${packages[@]}; do
    if ! instaledpackage ${str} ; then
        echo "[-] Não foi possível fazer a instalação do pacote ${str}"
        exit 1
    fi
done

apt-get install -y libxcb-cursor-dev
pip3 install requests
pip3 install PySide6
pip3 install pycryptodome
pip3 install beautifulsoup4
pip3 install tldextract
pip3 install adblockparser
pip3 install xmltodict
pip3 install slixmpp

# a instalaçao em sí dos pacotes
install(){
    if [ -f /tmp/bagusbagusgo.zip ] ; then
        rm /tmp/bagusbagusgo.zip
    fi
    echo "[+] Download do arquivo: ${URL}" 
    wget -q -O /tmp/bagusbagusgo.zip ${URL}
    if [ -d /tmp/bagus_browser-main/ ] ; then
        rm -r /tmp/bagus_browser-main/
    fi
    echo "[+] Descompactando /tmp/bagusbagusgo.zip" 
    unzip -qq /tmp/bagusbagusgo.zip -d /tmp/
    cp -r /tmp/bagus_browser-main/* ${DIR}
    if [ -L /bin/bagus ] ; then
        rm /bin/bagus
    fi
    chmod +x ${DIR}/start.sh
    ln -s ${DIR}/start.sh /bin/bagus
}

# aqui inicia a instalaçao, todas as dependencias estão
#    instaladas até o momento.
if [ -d ${DIR} ] ; then
    # o automático nunca pergunta para o usuário, vai direto
    if [ $auto -eq 1 ] ; then
        install
    else
        printf 'O diretório já existe, deseja continuar (y|n)?: '
        read OPCAO
        if [ $OPCAO = "y" ] ; then
            install
        else
            exit 0
        fi
    fi
else
    mkdir ${DIR}
    install
fi
