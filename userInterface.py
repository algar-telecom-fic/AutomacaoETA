class userInterface:
    def __init__(self, commands = {}, devices = []):
        self.commands = commands
        self.devices = devices
        self.internalCommands = []
        for i in self.commands:
            self.internalCommands.append(i["action"])
    
    def setDevices(self, devices = []):
        self.devices = devices
    
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
                print("Saida solicitada")
                return False

    def showHelp(self):
        print("Os comandos existentes sao: ")
        for i in self.internalCommands:
            print(i)
        print()
    
    def showPreRunCommands(self):
        print("\033[1;31m")
        print("Verifique os comandos e os dispositivos que serão conectados")
        print("\033[m")
        print("\033[1;33mComandos a serem executados:\033[m")
        for i in self.commands:
            print(i["commands"])

        print("\033[1;33mDispositivos que serão conectados:\033[m")
        for i in self.devices:
            print(i)
        while(True):
            val = input("Continuar? (S/N): ")
            if(val not in ["S", "s", "N", "n"]):
                print("Opcao Inválida")
            elif val == "N" or val == "n":
                return False
            else:
                return True
            
        
