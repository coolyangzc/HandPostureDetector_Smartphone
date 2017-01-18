package com.pcg.handposturedetector;

import android.app.Activity;
import android.os.Bundle;
import android.view.MotionEvent;
import android.widget.LinearLayout;

public class MainActivity extends Activity {
	
	private CapacityView cView = null;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		cView = new CapacityView(this);
		super.onCreate(savedInstanceState);
		LinearLayout topLayout = new LinearLayout(this);
		topLayout.addView(cView);
		setContentView(topLayout);
		//setContentView(R.layout.activity_main);
	}
	
	@Override
	public boolean onTouchEvent(MotionEvent event) {
		return cView.gestureDetector.onTouchEvent(event);
	}
}
