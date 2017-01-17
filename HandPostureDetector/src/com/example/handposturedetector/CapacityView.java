package com.example.handposturedetector;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.StringTokenizer;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.util.Log;
import android.view.View;

public class CapacityView extends View implements Runnable {
	
	private final int W = 1080;
	private final int H = 1920;
	private final int THRESHOLD = 50;
	private Process ps = null;
	
	int[] capaVal = new int[28 * 16];
	
	
	public CapacityView(Context context) {
		super(context);
		Thread thread = new Thread(this);
		thread.start();
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
		Paint paint = new Paint();
        paint.setColor(Color.WHITE);
        paint.setTextSize(50);
        paint.setTextAlign(Paint.Align.LEFT);
        //canvas.drawText(this.getMeasuredHeight() + ", " + this.getMeasuredWidth(), 500, 500, paint);

        paint.setStyle(Paint.Style.FILL);
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
                paint.setColor(Color.rgb(colorGradient, colorGradient, colorGradient));
                canvas.drawRect(squareWidth * i, squareHeight * j, squareWidth * (i + 1), squareHeight * (j + 1), paint);
            }
        }
        super.onDraw(canvas);
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
