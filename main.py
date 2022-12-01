from calendar import week
from re import L
import traceback
import paramiko
from netmiko import ConnectHandler
import netmiko
import json
import datetime
import io
import os
import time

import exceptions
from logs import logs as logsClass
from userInterface import userInterface

# Mensagens de erro que serao mostradas no console
errorFormatacaoArquivoConfig = "Formato do arquivo incorreto!"
errorAberturaArquivoConfig = "Falha na abertura do arquivo!"
errorResultadosConflitantes = "Foi encontrado mais de um resultado na busca. A operacao nao foi executada!"
errorResultadoNaoEncontrado = "Nao foram encontrados resultados para a busca selecionada."
errorRetornoIncorreto = "O retorno da funcao nao foi o esperado ou foi incorreto"
errorConfirmacaoBusca = "A busca foi cancelada pelo usuario!"
errorConexaoNaoEstabelecida = "Nao foi possivel conectar ao dispositivo! Verifique se as informacoes passadas estao corretas."
errorExecucaoComandoBash = "Erro na execucao do comando configurado no dispositivo!"
errorAutenticacao = "Falha na autenticacao. Verifique as credenciais!"
errorConexaoInvalida = "Nao foi possivel conectar!"
errorRecursoTemporariamenteInvalido = "Nao foi possivel conectar! Recurso temporariamente invalido."
errorGenerico = "Um erro foi encontrado durante a execucao do script"
errorMessage = "O erro foi: "
textoValorPrioridade = "Digite o novo valor de prioridade: "
textoConfirmacaoBusca = "A busca sera feita baseado nos seguintes termos:\nTermo 01: textoAqui01\nTermo 02: textoAqui02"
textoExecucaoCorreta = "O script foi executado corretamente e o arquivo de saida esta pronto!"
textoFeedbackInicioConexao = "Iniciando conexao em: \"hostname\" (user@host:port)"
textoFeedbackFinalConexao = "Encerrando conexao em: \"hostname\" (user@host:port)"

choosenCommand = ""

delimiter = ","
delimiter1 = "\""
newLine = "\n"
flagOutputFile = False

#Informacoes de header que serao usadas no arquivo de log
header = "usuario execucao" + delimiter + "flag" + delimiter + "dia semana" + delimiter + "data (MM/DD/YYYY)" + delimiter + "horario" + delimiter + "comando" + delimiter + "hostname" + delimiter + "usuario remoto" + delimiter + "host" + delimiter + "porta" + delimiter + "sucesso execucao remoto" + delimiter + "erro" + newLine

hostsVerificados = 0
connectionInfoList = {}
connectionInfo = {}
connectionInfoFiltered = []
flag = True
logFile: io.TextIOWrapper = None
username = ""
logsList = []

ftp_client = None

#Formatacao de dados para serem mostradas no log
def getDatetimeFormated():
    dateTemp = datetime.datetime.now()
    return dateTemp.strftime("%A" + delimiter + "%m/%d/%Y" + delimiter + "%X")

def getWeekday():
    dateTemp = datetime.datetime.now()
    return dateTemp.strftime("%A")

def getDate():
    dateTemp = datetime.datetime.now()
    return dateTemp.strftime("%m/%d/%Y")

def getTime():
    dateTemp = datetime.datetime.now()
    return dateTemp.strftime("%X")
    
def checkSizeLogFile():
    filesize = os.path.getsize("logs.log")
    if filesize == 0:
        return True
    else:
        return False

#Abertura do arquivo de log
def openLogFile():
    global logFile
    logFile = open("logs.log", "a")

    #Verifica se o arquivo de log existe
    if checkSizeLogFile() == True:
        logFile.write(header)

#Escrita de informacoes no arquivo de log
def writeLogFile():
    for object in logsList:
        for attributes in object.obj:
            if attributes == "error":
                logFile.write(str(object.obj[attributes]))
            else:
                logFile.write(str(object.obj[attributes]) + delimiter)
        logFile.write(newLine)

#Fecha arquivo de log
def closeLogFile():
    global logFile
    if logFile:
        logFile.close()

#Faz a abertura de arquivo externo, onde os dados serao mostrados, para melhor compreensao e visualizacao
def openOutputFile():
    global outputFile
    outputFile = open("./saida.txt", "w")

#Encerramento do arquivo de saida externo
def closeOutputFile():
    outputFile.close()

#Faz a leitura de informacoes de conexao
def readConnectionInfo():
    try:
        infoFile = open("./values/data.json")
        global connectionInfo
        connectionInfo = json.load(infoFile)["data"]
        for i in connectionInfo:
            #Conexoes configuradas para nao serem executadas, nao serao lidas
            if (i["executable"] == True):
                connectionInfoFiltered.append(i)
    except:
        print("Erro na abertura do JSON de configuracao de hosts")

#Leitura do arquivo que contem os comandos pre-definidos
def readCommandsFile():
    try:
        commandsJson = open("./values/commands.json")
        global commandsCisco
        commandsCisco = json.load(commandsJson)["cisco"]
        # print(commandsCisco)
    except:
        print("Erro na abertura do arquivo de comandos JSON")

#Definicao de flag para sucesso ou fracasso de operacao
def setFlag(flagParam):
    global flag
    flag = flagParam
    logsList[len(logsList)-1].obj["flag"] = flagParam

#Define valores que serao escritos no log
def setValuesLogs(userRequest = "", flag = "", weekday = "", date = "", time = "", command = "", hostname = "", userRemote = "", host = "", port = "", success = "", error = ""):
    if userRequest:
        logsList[len(logsList)-1].obj["userRequest"] = userRequest
    if weekday:
        logsList[len(logsList)-1].obj["weekday"] = weekday
    if date:
        logsList[len(logsList)-1].obj["date"] = date
    if time:
        logsList[len(logsList)-1].obj["time"] = time
    if command:
        logsList[len(logsList)-1].obj["command"] = command
    if hostname:
        logsList[len(logsList)-1].obj["hostname"] = hostname
    if userRemote:
        logsList[len(logsList)-1].obj["userRemote"] = userRemote
    if host:
        logsList[len(logsList)-1].obj["host"] = host
    if port:
        logsList[len(logsList)-1].obj["port"] = port
    if error:
        logsList[len(logsList)-1].obj["error"] = error
    if flag or not flag:
        logsList[len(logsList)-1].obj["flag"] = flag
    if success or not success:
        logsList[len(logsList)-1].obj["success"] = success

#inicia a conexao a um determinado host
def connectHost():
    global connectionInfoList, hostsVerificados
    if(hostsVerificados >= len(connectionInfoFiltered)):
        return False
    connectionInfoList = connectionInfoFiltered[hostsVerificados]
    logsList.append(logsClass())
    setValuesLogs(userRequest=username, weekday=getWeekday(), date=getDate(), time=getTime())

    global deviceName
    deviceName = connectionInfoList["hostname"]
    
    #mostra mensagem de inicio de conexao
    print("\n\n" + textoFeedbackInicioConexao
        .replace("hostname", connectionInfoList["hostname"])
        .replace("user", connectionInfoList["username"])
        .replace("host", connectionInfoList["host"])
        .replace("port", connectionInfoList["port"])
    )
    setValuesLogs(hostname=connectionInfoList["hostname"], host=connectionInfoList["host"], port=connectionInfoList["port"], userRemote=connectionInfoList["username"])
    try:
        #Faz a criacao de objeto que contem informacoes de conexao de um determinado equipamento, seguindo padrao NetMiko
        #https://github.com/ktbyers/netmiko/blob/develop/PLATFORMS.md
        obj = {
            "device_type": connectionInfoList["device_type"],
            "host": connectionInfoList["host"],
            "port": connectionInfoList["port"],
            "username": connectionInfoList["username"],
            "password": connectionInfoList["password"],
            # "fast_cli": False
        }

        global commandChoosen
        commandChoosen = connectionInfoList["commands"]
        
        #inicia-se conexao
        global ssh
        ssh = ConnectHandler(**obj)
        setFlag(True)
        setValuesLogs(flag = flag, success=True)
        return True
    #Tratamento de erro
    except Exception as err:
        if type(err) == netmiko.exceptions.NetmikoTimeoutException:
            tempString = str(err)
            tempString = tempString.replace("\n", " ")
            tempString = tempString.replace("  ", " ")
            setValuesLogs(success=False, error=tempString)
            raise netmiko.exceptions.NetmikoTimeoutException(tempString)
        print(err)
        setFlag(False)
        setValuesLogs(flag = flag, command=False, success=False, error=err)
        print(logsList[len(logsList)-1].printResult())
        print(err)
        hostsVerificados += 1
        return False

#Faz a execucao dos comandos escolhidos
def executeCommandHostCisco():
    ssh.enable()
    commands = ""

    for i in commandsCisco:
        global commandChoosen
        if(i["commands"] == commandChoosen):
            commands = i["commands"]
            break
    if(commands == ""):
        raise exceptions.ResultadosNaoEncontradosError("Comando para execucao no equipamento, nao encontrado!")

    tempString = ""
    tempString += newLine + deviceName + newLine
    tempString += ("Comando: " + str(commands) + newLine)
    setValuesLogs(command=commands)

    #envia os comandos que serao executados
    stdout = ssh.send_config_set(commands[:-1])
    ssh.config_mode()
    #Faz o envio do comando para aplicacao de alteracoes no equipamento
    stdout += newLine + newLine + ssh.send_command_timing(commands[-1:][0])
    
    print(ssh.find_prompt())
    
    #Tratamento de erro
    if stdout.find("Invalid input detected at '^' marker.") == -1:
        setValuesLogs(success=True)
        tempString += stdout + newLine
    else:
        raise exceptions.ExecucaoComandoBashError(stdout + "Houve erro na execucao do comando. Verifique se esta escrito corretamente.")

    #Faz a escrita de informacoes na tela, ou no arquivo de saida
    if flagOutputFile == True:
        outputFile.write(tempString)
    else:
        print(stdout)

#Faz o encerramento da conexao criada
def closeConnectionHost():
    print(textoFeedbackFinalConexao
        .replace("hostname", connectionInfoList["hostname"])
        .replace("user", connectionInfoList["username"])
        .replace("host", connectionInfoList["host"])
        .replace("port", connectionInfoList["port"])
    )
    ssh.disconnect()
    logsList[len(logsList)-1].obj["flag"] = flag
    logsList[len(logsList)-1].obj["hostname"] = connectionInfoList["hostname"]
    logsList[len(logsList)-1].obj["userRemote"] = connectionInfoList["username"]
    logsList[len(logsList)-1].obj["host"] = connectionInfoList["host"]
    logsList[len(logsList)-1].obj["port"] = connectionInfoList["port"]
    global hostsVerificados
    hostsVerificados += 1

#Busca o usuario que esta conectado atualmente a maquina
def getUsernameInput():
    global username
    username = os.environ.get('USER')

def readFiles():
    readConnectionInfo()
    readCommandsFile()

#Faz a repeticao das conexoes, para os equipamentos desejados
def repeatConnections():
    for i in range(len(connectionInfo)):
        if connectHost() == True:
            if connectionInfo[i]["device_type"].find("cisco") != -1:
                executeCommandHostCisco()

            closeConnectionHost()
        
def main():
    try:
        readFiles()
        UI = userInterface(commands=commandsCisco)

        #menu para interacao com usuario
        if UI.menu() == False:
            exit(0)

        global flagOutputFile
        if UI.outputFileChoose() == False:
            flagOutputFile = False
        else:
            flagOutputFile = True
            openOutputFile()

        for idx, elem in enumerate(connectionInfoFiltered):
            connectionInfoFiltered[idx]["commands"] = UI.chooseCommand()
            print(elem)
        for idx, elem in enumerate(connectionInfoFiltered):
            print(elem)
        if choosenCommand != False:
            #Executa operacoes escolhidas
            openLogFile()
            getUsernameInput()
            UI.setDevices(connectionInfoFiltered)
            continueCommand = UI.showPreRunCommands()
            if continueCommand == False:
                exit(0)
            repeatConnections()
            if flagOutputFile == True:
                closeOutputFile()

    #Tratamento de erros
    except FileNotFoundError as error:
        setFlag(False)
        print(traceback.format_exc())
        print(error.args[1])
        print(errorAberturaArquivoConfig)
    except SyntaxError as error:
        setFlag(False)
        print(error.args[1])
        print(traceback.format_exc())
        print(errorFormatacaoArquivoConfig)
    # handling errors from paramiko
    except paramiko.AuthenticationException as error:
        setFlag(False)
        print(traceback.format_exc())
        print(error)
        print(errorAutenticacao)
    except paramiko.ssh_exception.NoValidConnectionsError as error:
        setFlag(False)
        print(traceback.format_exc())
        print(error)
        print(errorConexaoInvalida)
    except BlockingIOError as error:
        setFlag(False)
        print(error)
        print(errorRecursoTemporariamenteInvalido)
    
    # handling errors from netmiko
    except netmiko.exceptions.NetmikoTimeoutException as err:
        setFlag(False)
        print(err)
        print(errorConexaoNaoEstabelecida)

    except exceptions.ResultadosConflitantesError:
        setFlag(False)
        print(traceback.format_exc())
        print(errorResultadosConflitantes)
    except exceptions.ResultadosNaoEncontradosError as error:
        setFlag(False)
        print(traceback.format_exc())
        print(errorResultadoNaoEncontrado)
        print(errorMessage, end="")
        print(error)
    except exceptions.RetornoIncorretoError:
        setFlag(False)
        print(traceback.format_exc())
        print(errorResultadoNaoEncontrado)
    except exceptions.ConfirmacaoNegadaError:
        setFlag(False)
        print(traceback.format_exc())
        print(errorConfirmacaoBusca)
    except exceptions.ConexaoNaoEstabelecida as err:
        setFlag(False)
        print(traceback.format_exc())
        print(errorConexaoNaoEstabelecida)
    except exceptions.ExecucaoComandoBashError as error:
        setFlag(False)
        print(traceback.format_exc())
        print("\n===========ERRO===========")
        print("Erro na execucao do comando configurado no dispositivo!")
        print(error)
        print("==========================\n")
    except SystemExit:
        print("Encerrando programa")
    except:
        setFlag(False)
        print(traceback.format_exc())
        print(errorGenerico)
    finally:
        writeLogFile()
        closeLogFile()

if __name__ == "__main__":
    main()