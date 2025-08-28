Ativando a Licença para o simulador Questa-Intel® FPGA
----------------------------------------------------------

#### 1. Acesse o Intel® FPGA Self-Service Licensing Center

[https://licensing.intel.com/](https://licensing.intel.com/)

#### 2. Clique em Enroll para criar uma conta

![self_service_license_center](imgs_questaLicense/self_service_license_center.png)

#### 3. Siga os passos para criação de uma conta

![create_account](imgs_questaLicense/create_account.png)

#### 4. Após a criação, você poderá solicitar a licença

**OBS:** Pode acontecer que você só consiga fazer o acesso para solicitar a licença após 2 horas.

![create_account_OK](imgs_questaLicense/create_account_OK.png)

#### 5. Acesse sua conta

**OBS:** algumas etapas de verificação e autenticação deverão ser solicitadas.

![self_service_sing_in](imgs_questaLicense/self_service_sing_in.png)

#### 6. Clique em Computers and License Files  Active Computers

![active_license_1](imgs_questaLicense/active_license_1.png)

#### 7. Clique em New

![active_license_new](imgs_questaLicense/active_license_new.png)

#### 8. Preencha conforme a imagem abaixo

**OBS:** O campo Primary Computer ID deverá ser preenchido com o MAC Address da placa de rede da sua máquina, sem os caraceteres que os Números e Letrtas (- ou ).

![active_license_mac_address](imgs_questaLicense/active_license_mac_address.png)

#### 9. Acesse a opção Sign up for Evaluation or No-Cost Licenses

![selecionar_licenca](imgs_questaLicense/selecionar_licenca.png)

#### 10. Selecione a opção do Questa, conforme a imagem abaixo e clique em next

![selecionar_licenca_questa](imgs_questaLicense/selecionar_licenca_questa.png)

#### 11. Selecione o ComputadorMAC para o qual a licença será gerada, aceite os termos e clique em Generate

![selecionar_licenca_computer](imgs_questaLicense/selecionar_licenca_computer.png)

#### 12. Após isso, você receberá uma confirmação de que a licença foi enviada para seu e-mail

![seleciona_licenca_email](imgs_questaLicense/seleciona_licenca_email.png)

#### 13. Faça o download da licença

![selecionar_licenca_baixar](imgs_questaLicense/selecionar_licenca_baixar.png)

**OBS:** Renomei o arquivo .dat para license.dat.

#### 14. Crie uma pasta/diretório de nome 'license_questa' em

**WINDOWS** - 'C:\intelFPGA_lite\23.1std/'

**LINUX** - '~/intelFPGA_lite/23.1std/'

mova o arquivo license.dat (o arquivo q foi renomeado) para a pasta criada 'license_questa'.

#### 15 .Variáveis de Ambiente

Após isso, basta fazer com que a licença seja reconhecida pelas variáveis de ambientes do seu sistema operacional (Windows ou Linux)

###### WINDOWS

Abra o Windows PowerShell como administrador e execute o seguinte comando para configurar o LM_LICENSE_FILE nas variáveis de ambiente

```
setx LM_LICENSE_FILE C:\intelFPGA_lite\23.1std\license_questa\license.dat;
```

###### LINUX

Execute o comando abaixo no terminal

```
export LM_LICENSE_FILE=~/intelFPGA_lite/23.1std/license_questa/license.dat
 ```   

#### Renovação da Licença

A licença do software expira em 12 meses após a ativação. Para renovar um arquivo de licença expirado, revisite o [SSLC](httpsfpgasupport.intel.comLicensinglicenseindex.html) . Você pode renovar uma licença somente para a versão que você ativou.

#### FONTE

[httpswww.intel.comcontentwwwusendocsprogrammable68347224-2and-software-license.html](httpswww.intel.comcontentwwwusendocsprogrammable68347224-2and-software-license.html)
