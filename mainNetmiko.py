from calendar import week
import traceback
import paramiko
from netmiko import ConnectHandler
import netmiko
import sys
import json
import datetime
import io
import os
import time

import exceptions
from logs import logs as logsClass
from userInterface import userInterface

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

commandsCisco = [
    {
        "action": "show network info",
        "commands": ["show ip interface brief", "show running-config"]
        # "commands": ["show ip interface brief"]
    },
    # {
    #     "action": "show ip address",
    #     "commands": ["ip address print"]
    # },
]

choosenCommand = ""

# command = ["ip address print", "export"]
# command = ["file print detail"]

delimiter = ","
delimiter1 = "\""
newLine = "\n"

header = "usuario execucao" + delimiter + "flag" + delimiter + "dia semana" + delimiter + "data (MM/DD/YYYY)" + delimiter + "horario" + delimiter + "comando" + delimiter + "hostname" + delimiter + "usuario remoto" + delimiter + "host" + delimiter + "porta" + delimiter + "sucesso execucao remoto" + delimiter + "erro" + newLine

hostsVerificados = 0
connectionInfoList = {}
connectionInfo = {}
connectionInfoFiltered = []
flag = True
logFile: io.TextIOWrapper = None
username = ""
logsList = []

# ssh = paramiko.SSHClient()
# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ftp_client = None

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

def openLogFile():
    global logFile
    logFile = open("logs.log", "a")
    if checkSizeLogFile() == True:
        logFile.write(header)

def writeLogFile():
    for object in logsList:
        for attributes in object.obj:
            if attributes == "error":
                logFile.write(str(object.obj[attributes]))
                # print(object.obj[attributes], end="")
            else:
                logFile.write(str(object.obj[attributes]) + delimiter)
                # print(object.obj[attributes], end=",")
        # print()
        logFile.write(newLine)


def closeLogFile():
    global logFile
    if logFile:
        logFile.close()

def readConnectionInfo():
    try:
        infoFile = open("./values/data.json")
        global connectionInfo
        connectionInfo = json.load(infoFile)["data"]
        # print("to aqui")
        # global connectionInfoFiltered
        for i in connectionInfo:
            if (i["executable"] == True):
                connectionInfoFiltered.append(i)
        # print(json.load(infoFile)["data"][0]["executable"])
    except:
        print("Erro na abertura do JSON de configuracao de hosts")

def setFlag(flagParam):
    global flag
    flag = flagParam
    logsList[len(logsList)-1].obj["flag"] = flagParam

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
    
def connectHost():
    global connectionInfoList, hostsVerificados
    if(hostsVerificados >= len(connectionInfoFiltered)):
        return False
    connectionInfoList = connectionInfoFiltered[hostsVerificados]
    # if connectionInfoList["executable"] == False:
    #     hostsVerificados += 1
    #     return False
    # else:
    logsList.append(logsClass())
    setValuesLogs(userRequest=username, weekday=getWeekday(), date=getDate(), time=getTime())

    print("\n\n" + textoFeedbackInicioConexao
        .replace("hostname", connectionInfoList["hostname"])
        .replace("user", connectionInfoList["username"])
        .replace("host", connectionInfoList["host"])
        .replace("port", connectionInfoList["port"])
    )
    setValuesLogs(hostname=connectionInfoList["hostname"], host=connectionInfoList["host"], port=connectionInfoList["port"], userRemote=connectionInfoList["username"])
    try:
        obj = {
            "device_type": connectionInfoList["device_type"],
            "host": connectionInfoList["host"],
            "port": connectionInfoList["port"],
            "username": connectionInfoList["username"],
            "password": connectionInfoList["password"]
        }
        # print(obj)
        # try:
        global ssh
        ssh = ConnectHandler(**obj)
        setFlag(True)
        setValuesLogs(flag = flag, success=True)
        return True
        # except netmiko.exceptions.NetmikoTimeoutException as err:
        #     print("ola")
        #     raise exceptions.ConexaoNaoEstabelecida(err)
        # except Exception as err:
        #     # setFlag(False)
        #     # print(traceback.format_exc())
        #     # print(errorConexaoNaoEstabelecida)
        #     raise Exception(err)
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
        # ssh.close()
        print(err)
        hostsVerificados += 1
        return False

def executeCommandHostCisco():
    try:
        for i in commandsCisco:
            if(i["action"] == choosenCommand):
                commands = i["commands"]
                break
        if(commands == ""):
            raise exceptions.ResultadosNaoEncontradosError("Comando para execucao no equipamento, nao encontrado!")

        for j in commands:
            print("\nComando: " + j)
            setValuesLogs(command=commands)
            stdout = ssh.send_command(j)
            if stdout.find("Invalid input detected at '^' marker.") == -1:
                setValuesLogs(success=True)
                print(stdout)
            else:
                raise exceptions.ExecucaoComandoBashError(stdout)
    except Exception as err:
        setValuesLogs(success=False, error=err)
        raise Exception(err)


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
    # print(logsList[len(logsList)-1].printResult())
    # writeLogFile(flag, content=[connectionInfoList["hostname"], connectionInfoList["user"], connectionInfoList["host"], connectionInfoList["port"]])
    global hostsVerificados
    hostsVerificados += 1

def getUsernameInput():
    global username
    # username = input("Digite seu nome: ")
    username = os.environ.get('USER')

def readFiles():
    readConnectionInfo()

def repeatConnections():
    for i in range(len(connectionInfo)):
        if connectHost() == True:
            if connectionInfo[i]["device_type"].find("cisco") != -1:
                executeCommandHostCisco()

            # executeCommandHost()
            closeConnectionHost()
        
def main():
    try:
        UI = userInterface(commands=commandsCisco)
        global choosenCommand
        choosenCommand = UI.menu()
        if choosenCommand != False:
            start = time.time()
            openLogFile()
            getUsernameInput()
            readFiles()
            UI.setDevices(connectionInfoFiltered)
            continueCommand = UI.showPreRunCommands()
            if continueCommand == False:
                exit(0)
            repeatConnections()
            end = time.time()
            f = open("timeSingleThread.txt", "a")
            f.write(str(end-start) + "\n")
    except FileNotFoundError as error:
        setFlag(False)
        print(traceback.format_exc())
        print(error.args[1])
        print(errorAberturaArquivoConfig)
    except SyntaxError as error:
        setFlag(False)
        print(error.args[1])
        # print(traceback.format_exc())
        print(errorFormatacaoArquivoConfig)
    # handling errors from paramiko
    except paramiko.AuthenticationException as error:
        setFlag(False)
        # print(traceback.format_exc())
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
        # print(traceback.format_exc())
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
        # writeLogFile(flag, content=[connectionInfoList["hostname"], connectionInfoList["user"], connectionInfoList["host"], connectionInfoList["port"]])
    finally:
        writeLogFile()
        closeLogFile()

if __name__ == "__main__":
    main()