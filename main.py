import traceback
import exceptions
import paramiko
import json
import datetime
import io
import os

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

command = "ls"

delimiter = ","
delimiter1 = "\""
newLine = "\n"

header = "usuario execucao" + delimiter + "dia semana" + delimiter + "data" + delimiter + "horario" + delimiter + "comando" + delimiter + "hostname" + delimiter + "usuario remoto" + delimiter + "host" + delimiter + "porta" + delimiter + "sucesso execucao remoto" + newLine

hostsVerificados = 0
connectionInfoList = {}
connectionInfo = {}
flag = True
logFile: io.TextIOWrapper = None
username = ""

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

def getDatetimeFormated():
    dateTemp = datetime.datetime.now()
    return dateTemp.strftime("%A" + delimiter + "%m/%d/%Y" + delimiter + "%X")

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

def writeLogFile(flagParam=None, content = []):
    global logFile
    logFile.write(username + delimiter + getDatetimeFormated() + delimiter + delimiter1 + command + delimiter1 + delimiter)
    if not content:
        logFile.write(str(flagParam) + newLine)
    else:
        logFile.write(content[0] + delimiter + content[1] + delimiter + content[2] + delimiter + content[3] + delimiter)
        logFile.write(str(flagParam) + newLine)

def closeLogFile(flagParam):
    writeLogFile(flagParam)
    global logFile
    logFile.close()

def checkExecutionFlag():
    if flag == False:
        return closeLogFile(flag)
    else:
        return closeLogFile(flag)

def setFlag(flagParam):
    global flag
    flag = flagParam
    print(flag)
    checkExecutionFlag()

def readConnectionInfo():
    infoFile = open("./values/data.json")
    global connectionInfo
    connectionInfo = json.load(infoFile)["data"]

def connectHost():
    global connectionInfoList, hostsVerificados
    connectionInfoList = connectionInfo[hostsVerificados]
    if connectionInfoList["executable"] == False:
        hostsVerificados += 1
        return False
    else:
        print(textoFeedbackInicioConexao
            .replace("hostname", connectionInfoList["hostname"])
            .replace("user", connectionInfoList["user"])
            .replace("host", connectionInfoList["host"])
            .replace("port", connectionInfoList["port"])
        )
        ssh.connect(connectionInfoList["host"], connectionInfoList["port"], connectionInfoList["user"], connectionInfoList["password"])
        return True

def executeCommandHost():
    stdin, stdout, stderr = ssh.exec_command(command)
    lines = stdout.readlines()
    linesErr = stderr.readlines()
    if(linesErr):
        raise exceptions.ExecucaoComandoBashError(linesErr)
    else:
        print(lines)

def closeConnectionHost():
    print(textoFeedbackFinalConexao
        .replace("hostname", connectionInfoList["hostname"])
        .replace("user", connectionInfoList["user"])
        .replace("host", connectionInfoList["host"])
        .replace("port", connectionInfoList["port"])
    )
    ssh.close()
    writeLogFile(flag, content=[connectionInfoList["hostname"], connectionInfoList["user"], connectionInfoList["host"], connectionInfoList["port"]])
    global hostsVerificados
    hostsVerificados += 1

def readFiles():
    readConnectionInfo()

def repeatConnections():
    for i in range(len(connectionInfo)):
        if connectHost() == True:
            executeCommandHost()
            closeConnectionHost()
        
def main():
    try:
        global username
        username = input("Digite seu nome: ")
        openLogFile()
        readFiles()
        repeatConnections()
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
        # print(traceback.format_exc())
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