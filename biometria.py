import sys
import subprocess
import pkg_resources
import time
import os
import webbrowser
from datetime import datetime

pagina = 'https://URL_SITE.COM'
sistema = 'linux'
command = 'clear'
caminho = ''
if os.name in ('nt', 'dos'):
	# Rodando no Windows
	sistema = 'windows'
	command = 'cls'
	caminho = os.environ['APPDATA']+'/biometria_config.txt'
else:
	# Rodando no linux
	caminho = os.path.expanduser('~')+'/.biometria_config'
	
	# Verificar se o PIP está instalado
	try:
		import pip
	except:
		print('Será necessário instalar o PIP para gerenciar as dependências do script.')
        quit()

def clear_console():
	os.system(command)

# Verificando se as dependências estão disponíveis
required = {'requests', 'pynput', 'getpass4', 'cryptography', 'psutil'}
installed = {pkg.key for pkg in pkg_resources.working_set}
pkgg = 'fernet'
missing = required - installed
clear_console()
if missing:
	print('Existem dependências não disponíveis no sistema.')
    print('Será solicitado o login e senha do proxy para baixá-las')
	python = sys.executable
    clear_console()
    print('Baixando arquivos')
    for dependencia in missing:
        subprocess.check_call([python, '-m', 'pip', 'install', dependencia], stdout=subprocess.DEVNULL)
    print('Rode o programa novamente')
    quit()

clear_console()
import requests
import secrets
import psutil
from getpass4 import getpass
from pynput.keyboard import Key, Controller
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

backend = default_backend()
iterations = 100_000

def _derive_key(password: bytes, salt: bytes, iterations: int = iterations) -> bytes:
	kdf = PBKDF2HMAC(
		algorithm=hashes.SHA256(), length=32, salt=salt,
		iterations=iterations, backend=backend)
	return b64e(kdf.derive(password))

def password_encrypt(message: bytes, password: str, iterations: int = iterations) -> bytes:
	salt = secrets.token_bytes(16)
	key = _derive_key(password.encode(), salt, iterations)
	return b64e(
		b'%b%b%b' % (
			salt,
			iterations.to_bytes(4, 'big'),
			b64d(Fernet(key).encrypt(message)),
		)
	)

def password_decrypt(token: bytes, password: str) -> bytes:
	decoded = b64d(token)
	salt, iter, token = decoded[:16], decoded[16:20], b64e(decoded[20:])
	iterations = int.from_bytes(iter, 'big')
	key = _derive_key(password.encode(), salt, iterations)
	return Fernet(key).decrypt(token)

def realizarLogin():
	global sessao
	params = {'login':login, "password":senha}
	x = requests.post(url+'/login.fcgi', json = params)
	aux = x.json()
	if 'error' in aux:
		return False
	sessao = aux['session']
	return True

def verificarSessao():
	if sessao == '':
		return False
	params = {'sessao':sessao}
	x = requests.post(url+'/session_is_valid.fcgi?session='+sessao)
	return x.json()['session_is_valid']

def definirHorario():
	agora = datetime.now()
	data = agora.strftime("%d %m %Y %H %M %S").split()
	params = {'day': int(data[0]),'month': int(data[1]),'year': int(data[2]),'hour': int(data[3]),'minute': int(data[4]),'second': int(data[5])}
	requests.post(url+'/set_system_time.fcgi?session='+sessao, json = params)
	x = requests.post(url+'/system_information.fcgi?session='+sessao)
	retorno = datetime.fromtimestamp(x.json()['time'])
	return 'Hora do equipamento: ' + str(retorno) + ' - Hora atual: ' + str(agora.strftime("%Y-%m-%d %H:%M:%S"))
	
def getUltimoAcesso():
	global id_usuario
	params = {'object':'access_logs','limit':1,'order':['time', 'descending'],'where':{'access_logs': {'event':7}}}
	x = requests.post(url+'/load_objects.fcgi?session='+sessao, json = params)
	aux = x.json()['access_logs'][0]
	id_usuario = str(aux['user_id']).rjust(8, '0')
	return aux['id']

def realizarConexao():
	global id_ultimo, id_atual
	if(testarConexao() == False):
		print('IP indisponível. O script será encerrado')
		quit()
	else:
		print('IP alcançável')

	print('\nRealizando conexão...')
	if(realizarLogin() == False):
		print('Ocorreu um erro ao estabelecer a conexão')
		quit()
	print(definirHorario())

	id_ultimo = getUltimoAcesso()
	id_atual = id_ultimo

	print('Iniciando monitoramento em breve\nO Firefox será aberto automaticamente')
	abrirFirefox()
	print('Monitorando acesso. Não feche esta janela')
	print('Para encerrar o processo, utilize CTRL+C')

def pingStatus():
	try:
		x = requests.get(url, timeout=2, verify=False)
		if(x.status_code == 200):
			return True
		else:
			return False
	except:
		return False

def testarConexao():
	teste = 0
	while teste < 10:
		teste += 1
		print('Testando conexão com o IP '+ip)
		if(pingStatus() == False):
			if(teste == 10):
				return False
			else:
				print('IP não responde. Será realizada uma nova tentativa de conexão em 2 minutos\n')
				time.sleep(120)
		else:
			teste = 10
			return True

def abrirFirefox():
    global pagina
	time.sleep(1.5)
	webbrowser.open(pagina)
	time.sleep(1.5)
	keyboard.press(Key.f11)
	keyboard.release(Key.f11)

def encerrarFirefox():
	for process in (process for process in psutil.process_iter() if process.name().startswith("firefox")):
		process.kill()

# Verificar se arquivo com os dados existe
login = ''
ip = ''
senha = ''
if(os.path.exists(caminho)):
	f = open(caminho, "r")
	ip = f.readline().rstrip()
	login = f.readline().rstrip()
	pw = f.readline().rstrip()
	senha = password_decrypt(pw.encode(), pkgg).decode()
	f.close()
else:
	ip = input('IP do terminal: ')
	login = input('Login de acesso WEB do terminal: ')
	senha = getpass('Senha de acesso WEB do terminal: ')
	f = open(caminho, "w")
	f.write(ip+'\n')
	f.write(login+'\n')
	pw = password_encrypt(senha.encode(), pkgg).decode('utf-8')
	f.write(pw+'\n')
	f.close()

sessao = ''
url = 'http://'+ ip
id_ultimo = 0
id_atual = 0
id_usuario = ''
inicio = int(time.time())
keyboard = Controller()

realizarConexao()

while True:
	time.sleep(0.5)
	
	try:
		# Verificar o ID do último acesso
		# Caso seja diferente do anterior, o valor será digitado
		id_atual = getUltimoAcesso()
		if id_ultimo != id_atual:
			id_ultimo = id_atual
			keyboard.type(id_usuario)
			keyboard.press(Key.enter)
			keyboard.release(Key.enter)
	except:
		clear_console()
		print('\n\nOcorreu um erro de comunicação com o leitor biométrico.\nSerá realizada uma nova conexão em 15 segundos')
		encerrarFirefox()
		time.sleep(15)
		realizarConexao()
		inicio = int(time.time())
	
	try:
		# Verificar se a conexão à Biometria ainda é válida
		# O teste é realizado caso já tenha passado 300 segundos (5 minutos)
		hr = int(time.time())
		if(hr - inicio) > 300:
			if(verificarSessao() != True):
				realizarLogin()
				time.sleep(1.5)
			inicio = hr
	except:
		clear_console()
		print('\n\nOcorreu um erro de comunicação com o leitor biométrico.\nSerá realizada uma nova conexão em 15 segundos')
		encerrarFirefox()
		time.sleep(15)
		realizarConexao()
		inicio = int(time.time())
