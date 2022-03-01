import traceback
import exceptions

errorFormatacaoArquivoConfig = "Formato do arquivo incorreto!"
errorAberturaArquivoConfig = "Falha na abertura do arquivo!"
errorResultadosConflitantes = "Foi encontrado mais de um resultado na busca. A operacao nao foi executada!"
errorResultadoNaoEncontrado = "Nao foram encontrados resultados para a busca selecionada."
errorRetornoIncorreto = "O retorno da funcao nao foi o esperado ou foi incorreto"
errorConfirmacaoBusca = "A busca foi cancelada pelo usuario!"
errorGenerico = "Um erro foi encontrado durante a execucao do script"
textoValorPrioridade = "Digite o novo valor de prioridade: "
textoConfirmacaoBusca = "A busca sera feita baseado nos seguintes termos:\nTermo 01: textoAqui01\nTermo 02: textoAqui02"
textoExecucaoCorreta = "O script foi executado corretamente e o arquivo de saida esta pronto!"

# valorPreferencia = 50

def readInputFile(inputFilePath, primarySearchParam, secondarySearchParam, newValuePriority):
    inputFile = open(inputFilePath)
    qtdConfigEncontradas = 0
    fileContent = []
    for i, x in enumerate(inputFile):
        if(x.find(primarySearchParam) != -1 and x.find(secondarySearchParam) != -1):
            qtdConfigEncontradas += 1
            # print(x)
            # print(f"linha {i}")
            x = x[:x.rfind(" ")+1] + str(newValuePriority)
        fileContent.append(x.replace("\n", ""))
    return [fileContent, qtdConfigEncontradas]

def writeOutputFile(outputFilePath, fileContent):
    outputFile = open(outputFilePath, "w")
    for x in fileContent:
        outputFile.write(x + "\n")
    outputFile.close()
    return 1

def checkResultsInputFile(qtdConfigEncontradas):
    if(qtdConfigEncontradas == 1):
        return 1
    elif(qtdConfigEncontradas == 0):
        raise exceptions.ResultadosNaoEncontradosError
    else:
        raise exceptions.ResultadosConflitantesError

def main():
    try:
        configFile = open("./config/config.txt")
        configFileInput = configFile.readline()
        configFileOutput = configFile.readline()
        primarySearchParam = configFile.readline()
        secondarySearchParam = configFile.readline()
        if(configFileInput.find("inputFile:") != -1 and configFileOutput.find("outputFile:") != -1 and primarySearchParam.find("primarySearchParam:") != -1 and secondarySearchParam.find("secondarySearchParam:") != -1):
            inputFilePath = configFileInput.replace("inputFile:", "").replace("\n", "")
            outputFilePath = configFileOutput.replace("outputFile:", "").replace("\n", "")
            primarySearchParam = primarySearchParam.replace("primarySearchParam:", "").replace("\n", "")
            secondarySearchParam = secondarySearchParam.replace("secondarySearchParam:", "").replace("\n", "")
            
            print(textoConfirmacaoBusca.replace("textoAqui01", primarySearchParam).replace("textoAqui02", secondarySearchParam))
            confirmacaoBusca = input("Confirma os termos de busca? [S/N]: ")
            if(confirmacaoBusca.lower() == "n"):
                raise exceptions.ConfirmacaoNegadaError
            
            newValuePriority = int(input(textoValorPrioridade))

            returnReadFileFunction = readInputFile(inputFilePath, primarySearchParam, secondarySearchParam, newValuePriority)
            
            checkResults = checkResultsInputFile(returnReadFileFunction[1])
            if(checkResults == 1):
                if(writeOutputFile(outputFilePath, returnReadFileFunction[0]) == 1):
                    print(textoExecucaoCorreta)
            else:
                raise exceptions.RetornoIncorretoError
        else:
            configFile.close()
            raise SyntaxError
        
    except FileNotFoundError: 
        print(traceback.format_exc())
        print(errorAberturaArquivoConfig)
    except SyntaxError:
        print(traceback.format_exc())
        print(errorFormatacaoArquivoConfig)
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
    except:
        print(traceback.format_exc())
        print(errorGenerico)

if __name__ == "__main__":
    main()