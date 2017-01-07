package com.pcg.sharedplatform;

import java.io.IOException;

public class CapacityDataThread_LittleV {
	private String userName, taskName;
	private Process ps = null;
	private boolean running = false;
	
	public void start(String userName, String taskName) {
		if (running) {
			System.out.println("Reject - CapacityDataThread_LittleV Still Running");
			return;
		}
		this.userName = userName;
		this.taskName = taskName;
		try {
			ps = Runtime.getRuntime().exec("cmd /c adb shell cd sdcard;sh capacity_LittleV.sh " + userName + " " + taskName);
			ps.waitFor();
		} catch (IOException e) {
			e.printStackTrace();
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		running = true;
		ps.destroy();
		ps = null;
		System.out.println("CapacityDataThread_LittleV Start");
	}
	
	public void finish() {
		try {
			ps = Runtime.getRuntime().exec("cmd /c adb shell aptouch_daemon_debug logtofile off");
			ps.waitFor();
			ps = Runtime.getRuntime().exec("cmd /c adb shell set `ls -t data/log/dmd_log/`; "
					+ "cp data/log/dmd_log/$1 sdcard/ExpData/" + userName + "/" + taskName);
			ps.waitFor();
		} catch (IOException e) {
			e.printStackTrace();
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		running = false;
		ps.destroy();
		ps = null;
		System.out.println("CapacityDataThread_LittleV Finish");
	}
}
