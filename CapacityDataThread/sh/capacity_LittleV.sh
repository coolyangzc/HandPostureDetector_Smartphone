userName=$1;
taskName=$2;
if [ ! -d "ExpData" ]; then
	mkdir ExpData
fi
if [ ! -d "ExpData/${userName}" ]; then
	mkdir ExpData/${userName}
fi
if [ ! -d "ExpData/${userName}/${taskName}" ]; then
	mkdir ExpData/${userName}/${taskName}
fi
aptouch_daemon_debug logtofile on