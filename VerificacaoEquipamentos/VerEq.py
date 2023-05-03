from netmiko import ConnectHandler
from os import system
from time import sleep

system('cls')
# Ler dados do arquivo TXT
with open('devices.txt') as f:
    devices = []
    for line in f:
        ip_address, username, password, device_type = line.strip().split(';')
        device = {
            'device_type': device_type,
            'ip': ip_address,
            'username': username,
            'password': password,
        }
        devices.append(device)

# Função para verificar e habilitar/desabilitar o protocolo Telnet
def verificar_telnet(device):
    # Conecta ao dispositivo
    with ConnectHandler(**device) as ssh:
        # Verifica se o protocolo Telnet está ativo
        output = ssh.send_command('show run | i telnet')
        if 'telnet' in output:
            print(f'O protocolo Telnet está ativo em {device["ip"]}.')
            # Pergunta ao usuário se deseja desabilitar o protocolo
            escolha = input('Deseja desabilitar o protocolo Telnet? (s/n) ')
            if escolha.lower() == 's':
                print('Desabilitando o protocolo Telnet...')
                ssh.send_config_set(['line vty 0 4','transport input ssh'])
                print('Protocolo telnet desabilitado...')
                sleep(5)
        else:
            print(f'O protocolo Telnet está inativo em {device["ip"]}.')
            # Pergunta ao usuário se deseja habilitar o protocolo
            escolha = input('Deseja habilitar o protocolo Telnet? (s/n) ')
            if escolha.lower() == 's':
                print('Habilitando o protocolo Telnet...')
                ssh.send_config_set(['line vty 0 4','transport input telnet ssh'])
                print('Protocolo telnet habilitado...')
                sleep(5)
        system('cls')

# Loop principal
while True:
    system('cls')
    # Exibe lista de dispositivos e pede para o usuário escolher um
    print('Dispositivos disponíveis:')
    for i, device in enumerate(devices):
        print(f'{i+1} - {device["ip"]}')
    escolha = input('Escolha um dispositivo (ou digite "sair" para encerrar o programa): ')
    
    # Sai do programa se o usuário escolher "sair"
    if escolha.lower() == 'sair':
        break
    
    # Tenta converter a escolha do usuário para um número inteiro
    try:
        escolha = int(escolha)
    except ValueError:
        print('Escolha inválida.')
        continue
    
    # Verifica se o número escolhido é válido
    if escolha < 1 or escolha > len(devices):
        print('Escolha inválida.')
        continue
    
    # Chama a função para verificar o dispositivo escolhido
    device = devices[escolha-1]
    verificar_telnet(device)
