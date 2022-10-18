from os import times


timeSingleThread = "timeSingleThread.txt"
timeMultiThread = "timeMultiThread.txt"

def readTimeSingleThread():
    f = open(timeSingleThread, "r")
    i = 0
    somaTempo = 0
    for x in f:
        i += 1
        somaTempo = somaTempo + float(x)
    f.close()
    return (somaTempo/i)

def readTimeMultiThread():
    f = open(timeMultiThread, "r")
    i = 0
    somaTempo = 0
    for x in f:
        i += 1
        somaTempo = somaTempo + float(x)
    f.close()
    return (somaTempo/i)

def compareBetween():
    tempoSingle = (readTimeSingleThread())
    tempoMulti = (readTimeMultiThread())

    if tempoSingle < tempoMulti:
        print("tempo SingleThread menor")
        print(str(tempoMulti - tempoSingle) + " segundos mais rapido")
    elif tempoSingle > tempoMulti:
        print("tempo MultiThread menor")
        print(str(tempoSingle - tempoMulti) + " segundos mais rapido")
    else:
        print("tempos iguais")


def main():
    # print("1 - conexao singlethread")
    # print("2 - conexao multithread")
    # print("3 - comparacao singlethread vs multithread")
    # choose = int(input("Digite a escolha: "))
    choose = 3

    if choose == 1:
        readTimeSingleThread()
    elif choose == 2:
        readTimeMultiThread()
    elif choose == 3:
        compareBetween()
    else:
        print("Erro! Opcao invalida")

if __name__ == "__main__":
    main()