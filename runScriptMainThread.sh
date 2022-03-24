#https://linuxhint.com/30_bash_script_examples/#top
echo "quantidade de testes: "
read limit
echo "Execucoes:"
echo " 1- SingleThread"
echo " 2- MultiThread"
read choose
if [ $choose -eq 1 ];
#SingleThread
then 
    for ((i = 0; i < $limit; i++)) do
        python3 main.py > saida.txt
        echo "Single - execucao: $i"
    done
    python3 compareTime.py
elif [ $choose -eq 2 ];
#MultiThread
then
    for ((i = 0; i < $limit; i++)) do
        # python3 main.py > saida.txt
        python3 mainMultiThread.py
        echo "Multi - execucao: $i"
    done
    python3 compareTime.py

else
    echo "opcao invalida"
fi