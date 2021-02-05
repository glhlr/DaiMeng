#!/bin/sh
#=====================
#YuanHui.HE
#khler@163.com
#=====================
while :
do
echo "Current DIR is " /home/ubuntu/DaiMeng/program
stillRunning=$(ps -e |grep "python3 dmMain.py" |grep -v "grep")
if [ "$stillRunning" ] ; then
echo "dmMain正在运行"
#kill -9 $pidof /home/ubuntu/DaiMeng/program/dmMain.py
else
echo "dmMain.py service was not started"
echo "Starting service ..."
python3 dmMain.py &
echo "dmMain.py service was exited!"
fi
sleep 60
done


