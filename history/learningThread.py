# https://alissonmachado.com.br/python-threads
# https://www.bogotobogo.com/python/Multithread/python_multithreading_Enumerating_Active_threads.php

import threading
import time
import requests

def worker(message):
    for i in range(5):
        print("thread 01")
        print(message)
        time.sleep(1)
    
def funcao():
    time.sleep(2)
    print("thread 02")
    url = 'https://m.kabum.com.br/busca?string=rtx+3050'
    r = requests.get(url)
    f = open("saida01.txt", "a")
    f.write(str(r.text))
    print("fiz a request")
    # print(r.text)

    # for i in range(6):
    #     print("thread 02")
    #     print("to aqui" + str(i))
    #     # time.sleep(1)


t01 = threading.Thread(target=worker,args=("thread sendo executada",))
t02 = threading.Thread(target=funcao)
t01.start()
t02.start()
print("nro de threads: " + str(threading.active_count()))

while t01.is_alive() and t02.is_alive():
    print("Aguardando thread")
    time.sleep(5)

print ("Thread morreu")
print ("Finalizando programa")
