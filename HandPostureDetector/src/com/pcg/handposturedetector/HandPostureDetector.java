package com.pcg.handposturedetector;

import android.content.Context;
import android.graphics.Color;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.SystemClock;
import android.view.GestureDetector;
import android.view.MotionEvent;
import android.view.GestureDetector.SimpleOnGestureListener;

public class HandPostureDetector {
	
	private Context ctx;
	private int THRESHOLD;
	
	public double deltaOriY;
	
	public float[] gravity = new float[3], 
				   geomagnetic = new float[3],
				   orientation = new float[3],
				   matR = new float[9];
	
	public float[][] gravityCenter = new float[20][2];
	public float[] touchCenter = new float[2];
	
	private int[] capa = new int[16*28];
	public int colorNum;
	private int[] color = new int[16*28];
	private int[] capaSum = new int[20];
	private float[] vertical = new float[20];
	
	private SensorManager sensorManager;
	private SensorEventListener sensorEventListener;
	
	public GestureDetector gestureDetector;
	
	public HistoryValueContainer confidenceL = new HistoryValueContainer(2000, 0.01);
	public HistoryValueContainer confidenceR = new HistoryValueContainer(2000, 0.01);
	
	public String debugInfo = "";
	
	private HistoryValueContainer oriY = new HistoryValueContainer(500, 0.01);
	
	private final int W = 1080;
	private final int H = 1920;
	
	private final int[] dx = {0, 0, -1, 1};
	private final int[] dy = {1, -1, 0, 0};
	
	HandPostureDetector(Context context, int THR) {
		ctx = context;
		THRESHOLD = THR;
		sensorEventListener = new SensorEventListener() {
		
			@Override
			public void onSensorChanged(SensorEvent event) {
				switch(event.sensor.getType()) {
				case Sensor.TYPE_ACCELEROMETER:
					gravity[0] = event.values[0];
					gravity[1] = event.values[1];
					gravity[2] = event.values[2];
					break;
				case Sensor.TYPE_MAGNETIC_FIELD:
					geomagnetic[0] = event.values[0];
					geomagnetic[1] = event.values[1];
					geomagnetic[2] = event.values[2];
					break;
				}
			}
		
			@Override
			public void onAccuracyChanged(Sensor sensor, int accuracy) {
				// TODO Auto-generated method stub
				
			}
		};
		sensorManager = (SensorManager)ctx.getSystemService(ctx.SENSOR_SERVICE);
		sensorManager.registerListener(sensorEventListener, 
				sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER), 
				SensorManager.SENSOR_DELAY_FASTEST);
		sensorManager.registerListener(sensorEventListener, 
				sensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD), 
				SensorManager.SENSOR_DELAY_FASTEST);
		
		SimpleOnGestureListener onGestureListener = new SimpleOnGestureListener() {
			
			@Override
			public boolean onSingleTapUp(MotionEvent e) {
				touchCenter[0] = e.getX();
				touchCenter[1] = e.getY();
				
				double rotY = orientation[2] / Math.PI * 180;
				
				int conf = 5;
				long eTime = e.getEventTime();
				if (touchCenter[1] < W / 2)
					conf *= 2;
				if (touchCenter[0] < W / 3) {
					if (rotY > 5) 
						for (int i=0; i<conf; ++i)
							confidenceR.update((rotY - 5) / 10, eTime);
					else if (rotY < 0)
						for (int i=0; i<conf; ++i)
							confidenceL.update(-rotY / 5, eTime);
				}
				if (touchCenter[0] > W / 3 * 2) {
					if (rotY > 0) 
						for (int i=0; i<conf; ++i)
							confidenceR.update(rotY / 5, eTime);
					else if (rotY < -5)
						for (int i=0; i<conf; ++i)
							confidenceL.update(-(rotY + 5) / 10, eTime);
				}
				
	            return true;
	        }
		};
		gestureDetector = new GestureDetector(ctx, onGestureListener);
	}
	
	public void updateCapa(int[] capaVal) {
		System.arraycopy(capaVal, 0, capa, 0, capa.length);
	}
	
	private void colorGrid(int x, int y, int c) {
		int id = x*28+y;
		color[id] = c;
		capaSum[c] += capa[id];
		gravityCenter[c][0] += capa[id] * (x+0.5f);
		gravityCenter[c][1] += capa[id] * (y+0.5f);
		for(int k=0; k<4; k++) {
			int nx = x + dx[k];
			int ny = y + dy[k];
			if (nx >= 0 && nx < 16 && ny >=0 && ny < 28)
				if (color[nx*28+ny] == -1 && capa[nx*28+ny] > THRESHOLD)
					colorGrid(nx, ny, c);
		}
	}
	
	private void calcVertical(int c) {
		vertical[c] = 0;
		float x = gravityCenter[c][0], y = gravityCenter[c][1];
		for (int i = 0; i < 16; i++) {
            for (int j = 0; j < 28; j++) {
            	if (color[i*28+j] != c)
            		continue;
            	vertical[c] += Math.abs(y-j) * capa[i*28+j];
            	vertical[c] -= Math.abs(x-i) * capa[i*28+j];
            }
        }
		vertical[c] /= capaSum[c];
	}
	
	public void calc() {
		SensorManager.getRotationMatrix(matR, null, gravity, geomagnetic);
        SensorManager.getOrientation(matR, orientation);
        long curTime = SystemClock.uptimeMillis();
        float x = 0, y = 0, sum = 0;
        for (int i = 0; i < 16; i++) {
            for (int j = 0; j < 28; j++) {
            	if (capa[i*28+j] <= THRESHOLD)
            		continue;
                x += capa[i*28+j] * (i + 0.5f);
                y += capa[i*28+j] * (j + 0.5f);
                sum += capa[i*28+j];
            }
        }
        x /= sum;
        y /= sum;
        float dirL = 0, dirR = 0, dx, dy;
        colorNum = 0;
        for (int i = 0; i < 16 * 28; i++)
        	color[i] = -1;
        for (int i = 0; i < 16; i++)
        	for(int j = 0; j < 28; j++)
        		if (capa[i*28+j] > THRESHOLD && color[i*28+j] == -1) {
        			capaSum[colorNum] = 0;
        			gravityCenter[colorNum][0] = gravityCenter[colorNum][1] = 0;
        			
        			colorGrid(i, j, colorNum);
        			
        			gravityCenter[colorNum][0] /= capaSum[colorNum];
        			gravityCenter[colorNum][1] /= capaSum[colorNum];
        			colorNum++;
        		}
        for (int i = 0; i < colorNum; ++i)
        	if (capaSum[i] > 1000 && gravityCenter[i][1] > 20) {
        		calcVertical(i);
        		if (vertical[i] < 0.5)
        			continue;
        		if (gravityCenter[i][0] < 3)
        			for(int k=0; k<10; ++k) {
        				confidenceL.update(Math.min(1, (vertical[i] - 0.5) / 0.25), curTime);
        				confidenceR.update(0, curTime);
        			}
        		else if (gravityCenter[i][0] > 13)
        			for(int k=0; k<10; ++k) {
        				confidenceR.update(Math.min(1, (vertical[i] - 0.5) / 0.25), curTime);
        				confidenceL.update(0, curTime);
        			}
        	}
        for (int i = 0; i < 16; i++) {
            for (int j = 0; j < 20; j++) {
            	if (capa[i*28+j] <= THRESHOLD)
            		continue;
            	dx = i - x;
            	dy = j - y;
            	dirL += capa[i*28+j] * Math.abs(dx * 0.7071 + dy * -0.7071);
            	dirR += capa[i*28+j] * Math.abs(dx * 0.7071 + dy * 0.7071);
            }
        }
        deltaOriY = orientation[2] - oriY.value;
        
        oriY.update(orientation[2], curTime);
        
        //Mystic
        dirL *= 1.2f;
        if (dirL * dirR != 0) {
	        if (dirL > dirR) {
	        	confidenceL.update(Math.min(1, (dirL - dirR) / dirR * 2),  curTime);
	        	confidenceR.update(0, curTime);
	        } else {
	        	confidenceR.update(Math.min(1, (dirR - dirL) / dirL * 2),  curTime);
	        	confidenceL.update(0, curTime);
	        }
        } else {
        	confidenceL.update(0, curTime);
        	confidenceR.update(0, curTime);
        }
        debugInfo = String.format("%.1f", confidenceL.value) + "  " +
        			String.format("%.1f", confidenceR.value) + "  ";
	}
}
