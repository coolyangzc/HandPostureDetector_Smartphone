package com.pcg.sharedplatform;

import java.io.File;
import java.io.IOException;
import java.io.FileOutputStream;
import java.io.FileNotFoundException;

public class TouchDataThread implements Runnable {
	
	private volatile Thread thread;
	private String userName, taskName;
	private Process ps = null, kill_ps = null;
	
	@Override
	public void run() {
		try {
			try {
				File path = new File("cmd/");
				if (!path.exists())
					path.mkdir();
				FileOutputStream fos = new FileOutputStream(new File("cmd/" + userName + "_" + taskName + ".txt"));
				String strcmd = "cd sdcard\nsh touch.sh " + userName + " " + taskName;
				fos.write(strcmd.getBytes());
				fos.close();
			} catch (FileNotFoundException e) {
				e.printStackTrace();
			} catch (IOException e) {
				e.printStackTrace();
			}
			try {
				ps = Runtime.getRuntime().exec("cmd /c adb shell < cmd\\" + userName + "_" + taskName + ".txt");
				ps.waitFor();
			} catch (IOException e) {
				e.printStackTrace();
			}
		} catch (InterruptedException e) {
			System.out.println("TouchDataThread - successful interrupt");
			return;
		}
		System.out.println("TouchDataThread - unexcepted finish");
	}
	
	public void start(String userName, String taskName) {
		if (thread == null) {
			this.userName = userName;
			this.taskName = taskName;
			thread = new Thread(this);
			thread.start();
		}
	}
	
	public void finish() {
		try {
			kill_ps = Runtime.getRuntime().exec("cmd /c adb shell \"set `ps | grep getevent`; kill -9 $2\"");
			kill_ps.waitFor();
		} catch (IOException e) {
			e.printStackTrace();
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		ps.destroy();
		ps = null;
		kill_ps.destroy();
		kill_ps = null;
		thread.interrupt();
		thread = null;
	}
	
}
