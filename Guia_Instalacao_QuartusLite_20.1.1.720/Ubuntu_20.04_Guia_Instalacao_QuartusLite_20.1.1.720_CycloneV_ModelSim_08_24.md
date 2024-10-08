Ubuntu 20.04 LTS (Focal Fossa)
================================

Por: Marco Antonio Soares de Mello Alves (Laboratório de Arquitetura de
Computadores)

Dúvidas:

> **Email: marcoasma@insper.edu.br**

Quartus Prime e ModelSim
========================

Execute no terminal os comandos a seguir, o Quartus necessita de
dependências da arquitetura i384:

``` {.sourceCode .bash}
$ sudo dpkg --add-architecture i386
$ sudo apt-get update
$ sudo pip install PyGObject
$ sudo apt-get install gcc make libxft2:i386 libxext6:i386 \
  libncurses5:i386 libstdc++6:i386 libpng-dev \
  libpng16-16:i386 libpng16-16 python-gobject libnotify-bin
$ sudo apt install libxft2 libxft2:i386 lib32ncurses6
$ sudo apt install libxext6
$ sudo apt install libxext6:i386
```

Instale o canberra-gtk-module:
``` {.sourceCode .bash}
$ sudo apt-get install libcanberra-gtk-module
```

### [Libpng12](http://www.bitsnbites.eu/installing-intelaltera-quartus-in-ubuntu-17-10/)

> The simplest way is to build and install libpng12 from source
> (requires build-essential). Install build-essential (to get gcc etc):
> sudo apt install build-essential [Download the source code from
> sourceforge](https://sourceforge.net/projects/libpng/files/libpng12/1.2.59/libpng-1.2.59.tar.xz/download)
> (select a suitable version and tar archive). Unpack the tar archive to
> /tmp Build and install:

``` {.sourceCode .bash}
$ cd $HOME/Downloads/libpng-1.2.59
$ ./configure --prefix=/usr/local
$ make
$ sudo make install
$ sudo ldconfig
```

Instalando
----------

Faça o download dos arquivos a seguir (salve na mesma todos os
arquivos):

-   Quartus Lite 20.1 :
    https://downloads.intel.com/akdlm/software/acdsinst/20.1std.1/720/ib_installers/QuartusLiteSetup-20.1.1.720-linux.run

-   ModelSim :
    https://downloads.intel.com/akdlm/software/acdsinst/20.1std.1/720/ib_installers/ModelSimSetup-20.1.1.720-linux.run

-   Cyclone V (Chip usado no curso) :
    https://downloads.intel.com/akdlm/software/acdsinst/20.1std.1/720/ib_installers/cyclonev-20.1.1.720.qdz

Abra o terminal na pasta que os arquivos foram salvos e execute os dois
comandos a seguir:

``` {.sourceCode .bash}
$ chmod +x QuartusLiteSetup-20.1.1.720-linux.run
$ ./QuartusLiteSetup-20.1.1.720-linux.run
```

> Grave o caminho na qual o **Quartus** foi instalado, ele será
> utilizado na próxima etapa.

> Se o Quartus falhar na instalação, mova o modelsim dessa pasta e
> instale novamente. Depois será necessário instalar o modelsim a parte.

Modelsim
--------

1.  Editar vco

Vamos editar o arquivo `vco` que está na pasta do modelsim (exe:
`$HOME/intelFPGA_lite/20.1/modelsim_ase/vco`):

``` {.sourceCode .bash}
$ sudo sed -i '209 a\        4.[0-9]*)             vco="linux" ;;' $HOME/intelFPGA_lite/20.1/modelsim_ase/vco
```

2.  Libfreetype 6.10.1 (versão 2.6)

``` {.sourceCode .bash}
$ cd ~/Downloads
$ wget https://github.com/Insper/Z01-tools/raw/master/Extra/Libfreetype-6.10.1-lib32.tar.gz
$ mkdir $HOME/intelFPGA_lite/20.1/modelsim_ase/lib32
$ tar zxf Libfreetype-6.10.1-lib32.tar.gz -C $HOME/intelFPGA_lite/20.1/modelsim_ase/lib32
```

<!-- Adicione ao final do `bashrc` a seguinte linha:

``` {.sourceCode .diff}
export LD_LIBRARY_PATH=$HOME/intelFPGA_lite/20.1/modelsim_ase/lib32
```
--> 
Configurando o USB Blaster
--------------------------

#### [libudev1:i386](https://forums.intel.com/s/question/0D50P00003yySE5SAM/newbie-usb-blaster-on-ubuntu-linux-xenial-1604-wont-probe-chain?language=en_US)

Para o gravador Jtag blaster funcionar no Ubuntu 18 LTS

``` {.sourceCode .bash}
$ sudo apt-get install libudev1:i386
$ sudo ln -sf /lib/x86_64-linux-gnu/libudev.so.1 /lib/x86_64-linux-gnu/libudev.so.0
```

Execute o comando a seguir para criar o arquivo de regra:

``` {.sourceCode .bash}
$ sudo gedit /etc/udev/rules.d/51-altera-usb-blaster.rules
```

Adicione as seguintes linhas a esse arquivo criado e salve:

``` {.sourceCode .diff}
SUBSYSTEM=="usb", ATTR{idVendor}=="09fb", ATTR{idProduct}=="6001", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="09fb", ATTR{idProduct}=="6002", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="09fb", ATTR{idProduct}=="6003", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="09fb", ATTR{idProduct}=="6010", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="09fb", ATTR{idProduct}=="6810", MODE="0666"
```

Recarrege o as permissões via o comando a seguir:

``` {.sourceCode .bash}
$ sudo service udev restart
```

Configurando variáveis de ambiente
----------------------------------

Adicione ao final do `bashrc` as seguintes linhas:

``` {.sourceCode .diff}
export ALTERAPATH=$HOME/intelFPGA_lite/20.1
export PATH=$PATH:${ALTERAPATH}/quartus/bin
export PATH=$PATH:${ALTERAPATH}/modelsim_ase/linuxaloem/
export PATH=$PATH:${ALTERAPATH}/modelsim_ase/lib32
export VUNIT_MODELSIM_PATH=${ALTERAPATH}/modelsim_ase/linuxaloem/
export VUNIT_SIMULATOR=modelsim
export QSYS_ROOTDIR="$ALTERAPATH/quartus/sopc_builder/bin"
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${ALTERAPATH}/modelsim_ase/lib32
```

Se você alterou o caminho de instalação na etapa do `Quartus`, deve
modificar a primeira linha inserindo o caminho da instalação.

Validando
=========

> Reinicie o computador (ou máquina virtual) para concluir a instalação

1.  **Quartus:** Escreva `quartus` no terminal, o mesmo deve abrir a
    janela do Quartus
2.  **Programador:** Com a FPGA plugadae ligada no pc, digite `jtagconfig` ele
    deve aparecer o device.

