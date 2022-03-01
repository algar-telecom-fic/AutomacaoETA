import traceback
import exceptions
import paramiko
import json

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

hosts = []
ports = []
hostnames = []
users = []
passwords = []
credentials = []
variavelTeste = []
hostsVerificados = 0
connectionInfoList = {}

connectionInfo = {}

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

def readHosts():
    hostFile = open("./values/hosts.txt", "r")
    for x in hostFile:
        hosts.append(x.strip())
    # print(hosts)
    hostFile.close()

def readPorts():
    portsFile = open("./values/ports.txt")
    for x in portsFile:
        ports.append(x.strip())
    # print(ports)
    portsFile.close()

def readHostnames():
    hostnamesFile = open("./values/hostnames.txt")
    for x in hostnamesFile:
        hostnames.append(x.strip())
    # print(hostnames)
    hostnamesFile.close()

def readCredentials():
    credentialsFile = open("./values/credentials.txt")
    for x in credentialsFile:
        temp = x.split()
        users.append(temp[0])
        passwords.append(temp[1])
    # print(credentials)
    credentialsFile.close()

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
    global hostsVerificados
    hostsVerificados += 1
    # variavelTeste.append(True)

def readFiles():
    readConnectionInfo()
    # readHosts()
    # readPorts()
    # readHostnames()
    # readCredentials()

def repeatConnections():
    for i in range(len(connectionInfo)):
        if connectHost() == True:
            executeCommandHost()
            closeConnectionHost()
        
def main():
    try:
        readFiles()
        repeatConnections()
    except FileNotFoundError as error:
        # print(traceback.format_exc())
        print(error.args[1])
        print(errorAberturaArquivoConfig)
    except SyntaxError as error:
        print(error.args[1])
        # print(traceback.format_exc())
        print(errorFormatacaoArquivoConfig)
    
    except paramiko.AuthenticationException as error:
        # print(traceback.format_exc())
        print(error)
        print(errorAutenticacao)
    except paramiko.ssh_exception.NoValidConnectionsError as error:
        # print(traceback.format_exc())
        print(error)
        print(errorConexaoInvalida)
    except BlockingIOError as error:
        print(error)
        print(errorRecursoTemporariamenteInvalido)
    
    except exceptions.ResultadosConflitantesError:
        print(traceback.format_exc())
        print(errorResultadosConflitantes)
    except exceptions.ResultadosNaoEncontradosError:
        print(traceback.format_exc())
        print(errorResultadoNaoEncontrado)
    except exceptions.RetornoIncorretoError:
        print(traceback.format_exc())
        print(errorResultadoNaoEncontrado)
    except exceptions.ConfirmacaoNegadaError:
        print(traceback.format_exc())
        print(errorConfirmacaoBusca)
    except exceptions.ExecucaoComandoBashError as error:
        # print(traceback.format_exc())
        print("\n===========ERRO===========")
        print("Erro na execucao do comando configurado no dispositivo!")
        print(error)
        print("==========================\n")
    except:
        print(traceback.format_exc())
        print(errorGenerico)

if __name__ == "__main__":
    main()