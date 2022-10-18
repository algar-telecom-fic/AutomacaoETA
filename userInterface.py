import sys

class userInterface:
    def __init__(self, commands = {}):
        self.commands = commands
        self.internalCommands = []
        for i in self.commands:
            self.internalCommands.append(i["action"])
    
    def menu(self):
        while(True):
            print("Selecione uma opcao abaixo: ")
            print(" 1 - Selecionar comando")
            print(" 8 - Ajuda")
            print(" 9 - Sair")
            escolha = int(input("Opcao: "))

            if(escolha == 1):
                while(True):
                    commandInput = input("Digite o comando que deseja executar: ")
                    if(commandInput not in self.internalCommands):
                        print("Comando Invalido!")
                    else:
                        return commandInput
            elif(escolha == 8):
                self.showHelp()
            elif(escolha == 9):
                sys.exit(0)

    def showHelp(self):
        print("Os comandos existentes sao: ")
        for i in self.internalCommands:
            print(i)
        print()
