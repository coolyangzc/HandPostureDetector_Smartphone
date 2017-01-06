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
getevent -lt >/sdcard/ExpData/${userName}/${taskName}/TouchData.txt