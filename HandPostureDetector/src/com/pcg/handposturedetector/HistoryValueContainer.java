package com.pcg.handposturedetector;

import java.util.LinkedList;
import java.util.Queue;

public class HistoryValueContainer {
	
	public double value = 0;
	
	public Queue<Double> values = new LinkedList<Double>();
	private Queue<Double> timestamps = new LinkedList<Double>();
	
	private double ms, lowWeight;
	
	HistoryValueContainer(double ms, double lowWeight) {
		this.ms = ms;
		this.lowWeight = lowWeight;
	}
	
	public void update(double newValue, double timestamp_ms) {
		values.offer(newValue);
		timestamps.offer(timestamp_ms);
		while (timestamp_ms - timestamps.peek() > ms) {
			values.poll();
			timestamps.poll();
		}
		double k = 2 * (1.0 / values.size() - lowWeight) / (values.size() - 1);
		double now = lowWeight;
		value = 0;
		for (Double x: values) {
			value += x * now;
			now += k; 
		}
	}
	
}
