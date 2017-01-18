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
	
	
	private int[] capaVal = new int[28 * 16];
	
	public HandPostureDetector hDetector;
	
	
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
		
		//Register Sensors & Gesture Detector
		hDetector = new HandPostureDetector(ctx, THRESHOLD);
		
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
		hDetector.updateCapa(capaVal);
		hDetector.calc();
		
        int squareWidth = W / 16;
        int squareHeight = H / 28;
        int max = 0;
        for (int i = 0; i < capaVal.length; i++) {
            if (capaVal[i] > max) {
                max = capaVal[i];
            }
        }
        int colorGradient;
        
        for (int i = 0; i < 16; i++) {
            for (int j = 0; j < 28; j++) {
            	if (capaVal[i*28+j] <= THRESHOLD)
            		colorGradient = 0;
            	else
            		colorGradient = (int)((double)capaVal[i * 28 + j] / max * 255);
            	capaPaint.setColor(Color.rgb(colorGradient, colorGradient, colorGradient));
                canvas.drawRect(squareWidth * i, squareHeight * j, squareWidth * (i + 1), squareHeight * (j + 1), capaPaint);
            }
        }
        capaPaint.setColor(Color.RED);
        canvas.drawCircle(hDetector.gravityCenter[0] * squareWidth, 
        		hDetector.gravityCenter[1] * squareHeight, 32, capaPaint);
        
        capaPaint.setColor(Color.GREEN);
        canvas.drawCircle(hDetector.touchCenter[0], hDetector.touchCenter[1], 32, capaPaint);
        
        
        canvas.drawRoundRect(0, 0, 419, 268, 50, 50, picPaint);
        
        String debugInfo = "";
        
        debugInfo += String.format("%.0f", hDetector.orientation[0] / Math.PI * 180) + "\n";
        debugInfo += String.format("%.0f", hDetector.orientation[1] / Math.PI * 180) + "\n";
        debugInfo += String.format("%.0f", hDetector.orientation[2] / Math.PI * 180) + "\n";
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
