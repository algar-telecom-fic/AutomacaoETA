from calendar import week
import traceback
import paramiko
import json
import datetime
import io
import os
import time

import exceptions
from logs import logs as logsClass

errorFormatacaoArquivoConfig = "Formato do arquivo incorreto!"
errorAberturaArquivoConfig = "Falha na abertura do arquivo!"
errorResultadosConflitantes = "Foi encontrado mais de um resultado na busca. A operacao nao foi executada!"
errorResultadoNaoEncontrado = "Nao foram encontrados resultados para a busca selecionada."
errorRetornoIncorreto = "O retorno da funcao nao foi o esperado ou foi incorreto"
errorConfirmacaoBusca = "A busca foi cancelada pelo usuario!"
errorExecucaoComandoBash = "Erro na execucao do comando configurado no dispositivo!"
errorAutenticacao = "Falha na autenticacao. Verifique as credenciais!"
errorConexaoInvalida = "Nao foi possivel conectar!"
errorRecursoTemporariamenteInvalido = "Nao foi possivel conectar! Recurso temporariamente invalido."
errorGenerico = "Um erro foi encontrado durante a execucao do script"
textoValorPrioridade = "Digite o novo valor de prioridade: "
textoConfirmacaoBusca = "A busca sera feita baseado nos seguintes termos:\nTermo 01: textoAqui01\nTermo 02: textoAqui02"
textoExecucaoCorreta = "O script foi executado corretamente e o arquivo de saida esta pronto!"
textoFeedbackInicioConexao = "Iniciando conexao em: \"hostname\" (user@host:port)"
textoFeedbackFinalConexao = "Encerrando conexao em: \"hostname\" (user@host:port)"

command = ["ip address print", "export"]
# command = ["file print detail"]

delimiter = ","
delimiter1 = "\""
newLine = "\n"

header = "usuario execucao" + delimiter + "flag" + delimiter + "dia semana" + delimiter + "data (MM/DD/YYYY)" + delimiter + "horario" + delimiter + "comando" + delimiter + "hostname" + delimiter + "usuario remoto" + delimiter + "host" + delimiter + "porta" + delimiter + "sucesso execucao remoto" + delimiter + "erro" + newLine

hostsVerificados = 0
connectionInfoList = {}
connectionInfo = {}
flag = True
logFile: io.TextIOWrapper = None
username = ""
logsList = []

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
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
    writeLogFile()
    global logFile
    logFile.close()

def setFlag(flagParam):
    global flag
    flag = flagParam
    logsList[len(logsList)-1].obj["flag"] = flagParam

def readConnectionInfo():
    try:
        infoFile = open("./values/data.json")
        global connectionInfo
        connectionInfo = json.load(infoFile)["data"]
    except:
        print("Erro na abertura do JSON de configuracao de hosts")

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
    connectionInfoList = connectionInfo[hostsVerificados]
    if connectionInfoList["executable"] == False:
        hostsVerificados += 1
        return False
    else:
        logsList.append(logsClass())
        setValuesLogs(userRequest=username, weekday=getWeekday(), date=getDate(), time=getTime())
        # print(logsList[len(logsList)-1].printResult())

        print(textoFeedbackInicioConexao
            .replace("hostname", connectionInfoList["hostname"])
            .replace("user", connectionInfoList["user"])
            .replace("host", connectionInfoList["host"])
            .replace("port", connectionInfoList["port"])
        )
        setValuesLogs(hostname=connectionInfoList["hostname"], host=connectionInfoList["host"], port=connectionInfoList["port"], userRemote=connectionInfoList["user"])
        try:
            ssh.connect(connectionInfoList["host"], connectionInfoList["port"], connectionInfoList["user"], connectionInfoList["password"])
            global ftp_client
            ftp_client = ssh.open_sftp()
            setFlag(True)
            setValuesLogs(flag = flag, success=True)
            return True
        except Exception as err:
            setFlag(False)
            setValuesLogs(flag = flag, command=False, success=False, error=err)
            print(logsList[len(logsList)-1].printResult())
            ssh.close()
            print(err)
            hostsVerificados += 1
            return False

def executeCommandHost():
    for j in command:
        # ftp_client.get('/file/RouterOS-20220809-1420.backup','/home/gabriel/Documents/github/AutomacaoETA/saida.txt')
        # saida.txt
        setValuesLogs(command=j)
        stdin, stdout, stderr = ssh.exec_command(j)
        lines = stdout.readlines()
        linesErr = stderr.readlines()
        if(linesErr):
            raise exceptions.ExecucaoComandoBashError(linesErr)
        else:
            setValuesLogs(success=True)
            print(lines)

def closeConnectionHost():
    print(textoFeedbackFinalConexao
        .replace("hostname", connectionInfoList["hostname"])
        .replace("user", connectionInfoList["user"])
        .replace("host", connectionInfoList["host"])
        .replace("port", connectionInfoList["port"])
    )
    ssh.close()
    logsList[len(logsList)-1].obj["flag"] = flag
    logsList[len(logsList)-1].obj["hostname"] = connectionInfoList["hostname"]
    logsList[len(logsList)-1].obj["userRemote"] = connectionInfoList["user"]
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
            executeCommandHost()
            closeConnectionHost()
        
def main():
    try:
        start = time.time()
        openLogFile()
        getUsernameInput()
        readFiles()
        repeatConnections()
        closeLogFile()
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
    
    except exceptions.ResultadosConflitantesError:
        setFlag(False)
        print(traceback.format_exc())
        print(errorResultadosConflitantes)
    except exceptions.ResultadosNaoEncontradosError:
        setFlag(False)
        print(traceback.format_exc())
        print(errorResultadoNaoEncontrado)
    except exceptions.RetornoIncorretoError:
        setFlag(False)
        print(traceback.format_exc())
        print(errorResultadoNaoEncontrado)
    except exceptions.ConfirmacaoNegadaError:
        setFlag(False)
        print(traceback.format_exc())
        print(errorConfirmacaoBusca)
    except exceptions.ExecucaoComandoBashError as error:
        setFlag(False)
        # print(traceback.format_exc())
        print("\n===========ERRO===========")
        print("Erro na execucao do comando configurado no dispositivo!")
        print(error)
        print("==========================\n")
    except:
        # setFlag(False)
        print(traceback.format_exc())
        print(errorGenerico)


if __name__ == "__main__":
    main()