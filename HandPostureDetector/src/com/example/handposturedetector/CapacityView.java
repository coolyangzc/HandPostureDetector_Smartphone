package com.example.handposturedetector;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.view.View;

public class CapacityView extends View {

	public CapacityView(Context context) {
		super(context);
		
	}
	
	@Override
    protected void onDraw(Canvas canvas) {
		Paint paint = new Paint();
        paint.setColor(Color.BLACK);
        canvas.drawRect(0, 0, 1080, 1920, paint);
        super.onDraw(canvas);
	}

}
