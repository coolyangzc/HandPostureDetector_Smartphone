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
	private double deltaOriY;
	
	public float[] gravityCenter = new float[2];
	public float[] gravity = new float[3], 
				   geomagnetic = new float[3],
				   orientation = new float[3],
				   matR = new float[9];
	
	public float[] touchCenter = new float[2];
	
	private int[] capa = new int[16*28];
	
	private SensorManager sensorManager;
	private SensorEventListener sensorEventListener;
	
	public GestureDetector gestureDetector;
	
	public HistoryValueContainer confidenceL = new HistoryValueContainer(2000, 0.01);
	public HistoryValueContainer confidenceR = new HistoryValueContainer(2000, 0.01);
	
	public String debugInfo = "";
	
	private HistoryValueContainer oriY = new HistoryValueContainer(500, 0.01);
	
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
				
	            return true;
	        }
		};
		gestureDetector = new GestureDetector(ctx, onGestureListener);
	}
	
	public void updateCapa(int[] capaVal) {
		System.arraycopy(capaVal, 0, capa, 0, capa.length);
	}
	
	public void calc() {
		SensorManager.getRotationMatrix(matR, null, gravity, geomagnetic);
        SensorManager.getOrientation(matR, orientation);
        
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
        for (int i = 0; i < 16; i++) {
            for (int j = 0; j < 28; j++) {
            	if (capa[i*28+j] <= THRESHOLD)
            		continue;
            	dx = x - i;
            	dy = y - j;
            	dirL += capa[i*28+j] * Math.abs(dx * 0.7071 + dy * -0.7071);
            	dirR += capa[i*28+j] * Math.abs(dx * 0.7071 + dy * 0.7071);
            }
        }
        gravityCenter[0] = x;
        gravityCenter[1] = y;
        deltaOriY = orientation[2] - oriY.value;
        long curTime = SystemClock.elapsedRealtime();
        oriY.update(orientation[2], curTime);
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
