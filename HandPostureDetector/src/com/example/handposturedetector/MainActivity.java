package com.example.handposturedetector;

import android.app.Activity;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.LinearLayout;

public class MainActivity extends Activity {

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		CapacityView cView = new CapacityView(this);
		LinearLayout topLayout = new LinearLayout(this);
		topLayout.addView(cView);
		setContentView(topLayout);
		//setContentView(R.layout.activity_main);
	}
}
