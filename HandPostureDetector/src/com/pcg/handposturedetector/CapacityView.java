package com.pcg.handposturedetector;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.StringTokenizer;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.BitmapShader;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Shader.TileMode;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.util.Log;
import android.view.GestureDetector;
import android.view.MotionEvent;
import android.view.GestureDetector.SimpleOnGestureListener;
import android.view.View;

public class CapacityView extends View implements Runnable {
	
	private Context ctx;
	private final int W = 1080;
	private final int H = 1920;
	private final int THRESHOLD = 64;
	private Paint capaPaint = null, picPaint = null, textPaint = null;
	private Bitmap bitmap = null;
	private BitmapShader v_l, v_r, no;
	
	private Process ps = null;
	private SensorManager sensorManager;
	private SensorEventListener sensorEventListener;
	private float[] gravity = new float[3], 
					geomagnetic = new float[3],
					orientation = new float[3],
					matR = new float[9];
	private float touchX, touchY;
	
	private int[] capaVal = new int[28 * 16];
	
	public GestureDetector gestureDetector;
	
	public CapacityView(Context context) {
		super(context);
		ctx = context;
		
		initialize();
				
		Thread thread = new Thread(this);
		thread.start();
	}
	
	private void initialize() {
		//Setup Paints
		capaPaint = new Paint();
		capaPaint.setStyle(Paint.Style.FILL);
		picPaint = new Paint();
		picPaint.setAntiAlias(true);
		picPaint.setColor(Color.WHITE);
		picPaint.setAlpha(200);
		textPaint = new Paint();
		textPaint.setColor(Color.YELLOW);
		textPaint.setTextSize(64);
		
		//Load Resources
		BitmapFactory.Options opts = new BitmapFactory.Options();
		opts.inSampleSize = 2;
		bitmap = BitmapFactory.decodeResource(getResources(), R.drawable.v_l, opts);
		v_l = new BitmapShader(bitmap, TileMode.CLAMP, TileMode.CLAMP);
		bitmap = BitmapFactory.decodeResource(getResources(), R.drawable.v_r, opts);
		v_r = new BitmapShader(bitmap, TileMode.CLAMP, TileMode.CLAMP);
		no = null;
		
		//Register Sensors
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
		
		//Gesture Detector
		SimpleOnGestureListener onGestureListener = new SimpleOnGestureListener() {
			
			@Override
			public boolean onSingleTapUp(MotionEvent e) {
				touchX = e.getX();
				touchY = e.getY();
	            return true;
	        }
		};
		gestureDetector = new GestureDetector(ctx, onGestureListener);
		
	}
	
	private String getFrame() {
        String line, frame = "";
        try {
			ps = new ProcessBuilder(new String[] {"aptouch_daemon_debug", "diffdata"}).start();
			ps.waitFor();
			BufferedReader bufferedreader = new BufferedReader(new InputStreamReader(ps.getInputStream()));
	        while ((line = bufferedreader.readLine()) != null)
	            frame = frame + line + "\n";
	        ps.destroy();
	        ps = null;
		} catch (IOException e) {
			e.printStackTrace();
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
        return frame;
    }
	
	private void parseFrame(String frame) {
		StringTokenizer st = new StringTokenizer(frame);
        int i = 0;
        while (st.hasMoreTokens()) {
            capaVal[i] = Math.abs(Integer.parseInt(st.nextToken()));
            i++;
        }
	}
	
	@Override
    protected void onDraw(Canvas canvas) {
		super.onDraw(canvas);
        int squareWidth = W / 16;
        int squareHeight = H / 28;
        int max = 0;
        for (int i = 0; i < capaVal.length; i++) {
            if (capaVal[i] > max) {
                max = capaVal[i];
            }
        }
        int colorGradient;
        float x = 0, y = 0, sum = 0;
        for (int i = 0; i < 16; i++) {
            for (int j = 0; j < 28; j++) {
            	if (capaVal[i*28+j] <= THRESHOLD)
            		colorGradient = 0;
            	else
            		colorGradient = (int)((double)capaVal[i * 28 + j] / max * 255);
            	capaPaint.setColor(Color.rgb(colorGradient, colorGradient, colorGradient));
                canvas.drawRect(squareWidth * i, squareHeight * j, squareWidth * (i + 1), squareHeight * (j + 1), capaPaint);
                x += colorGradient * (i + 0.5f);
                y += colorGradient * (j + 0.5f);
                sum += colorGradient;
            }
        }
        x /= sum;
        y /= sum;
        float dirX = 0, dirY = 0;
        for (int i = 0; i < 16; i++) {
            for (int j = 0; j < 28; j++) {
            	if (capaVal[i*28+j] <= THRESHOLD)
            		continue;
            	float dx = x - i;
            	float dy = y - j;
            	if (dx*dy >=0) dx = Math.abs(dx);
            	else dx = - Math.abs(dx);
            	dirX += dx * capaVal[i*28+j];
            	dirY += dy * capaVal[i*28+j];
            }
        }
        x = x * squareWidth;
        y = y * squareHeight;
        capaPaint.setColor(Color.RED);
        canvas.drawCircle(x, y, 32, capaPaint);
        
        capaPaint.setColor(Color.GREEN);
        canvas.drawCircle(touchX, touchY, 32, capaPaint);
        
        if (dirX >= 0)
        	picPaint.setShader(v_r);
        else
        	picPaint.setShader(v_l);
        if (sum <= 1000)
        	picPaint.setShader(no);
        canvas.drawRoundRect(0, 0, 419, 268, 50, 50, picPaint);
        
        String debugInfo = "";
        SensorManager.getRotationMatrix(matR, null, gravity, geomagnetic);
        SensorManager.getOrientation(matR, orientation);
        debugInfo += String.format("%.0f", orientation[0] / Math.PI * 180) + "\n";
        debugInfo += String.format("%.0f", orientation[1] / Math.PI * 180) + "\n";
        debugInfo += String.format("%.0f", orientation[2] / Math.PI * 180) + "\n";
        canvas.drawText(debugInfo, 10, 330, textPaint);
	}

	
	
	@Override
	public void run() {
		long startTime = System.currentTimeMillis();
		int frameCount = 0;
		while (true) {
            parseFrame(getFrame());
            postInvalidate();
            frameCount++;
            Log.d("frame", "frame rate = " + (frameCount * 1000 / (System.currentTimeMillis() - startTime)));
		}
	}

}
