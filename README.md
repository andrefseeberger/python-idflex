# python-idflex

<img src="imb/biometria.jpg" alt="Biometria"/>

> Integração do iDFlex da Control ID, utilizando Python e a API oficial


## 🏁 Objetivo
Realizar a leitura do ID do usuário identificado com sucesso em um equipamento iDFlex Pro, e escrever este ID em uma página WEB.

O ID deverá ser ajustado para conter 8 caracteres, sendo completado com zeros à esquerda.


## 💻 Pré-requisitos
Python 3 (https://www.python.org/downloads/)
Módulo PIP

Bibliotecas adicionais:
* requests
* pynput
* getpass4
* cryptography
* psutil

Windows 
```
py -m pip install requests pynput getpass4 cryptography psutil
```

Linux
```
python3 -m pip install requests pynput getpass4 cryptography psutil
```

Caso esteja utilizando um proxy, adicionar:
```
--proxy=htpp://USUARIO:SENHA@URL_PROXY:PORTA
```

Editar a variável `pagina` do arquivo `biometria.py`.
```
As demais informações serão solicitadas na primeira vez que o código for executado
```



## 🚀 Funcionamento 
1. Ao executar o código pela primeira vez, será solitado `login`, `senha` e `IP` para acesso ao equipamento. São os mesmos dados utilizados para conexão via WEB
> As informações serão salvas no arquivo `biometria_config.txt` na pasta do usuário (`%APPDATA%` no Windows e `~` no Linux)

2. Será verificado se o leitor está alcançável, utilizando um PING.
> Caso não esteja, serão realizadas 9 novas tentativas, a cada 2 minutos.

3. É realizada uma conexão ao equipamento via API, sendo retornado um ID de sessão
> A cada 5 minutos é realizado um teste para verificar se o ID ainda é válido. Caso não seja, o Firefox é fechado e o programa retorna ao estágio 2.

4. É aberta uma nova página do Firefox, na URL indicada na variável `pagina`

5. A cada `500ms` é feita uma verificação do ID da última identificação válida no equipamento, retornando o ID do usuário correspondente.
> O ID do usuário é digitado na página WEB, seguindo de um `ENTER`


## 💬 Informações
> API oficial: https://www.controlid.com.br/docs/access-api-pt/

