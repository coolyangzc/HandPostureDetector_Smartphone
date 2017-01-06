package com.pcg.sharedplatform;

import java.util.Scanner;

public class Main {
	public static void main(String[] args) {
		TouchDataThread cthr = new TouchDataThread();
		System.out.println("Begin");
		cthr.start("YZC", "Task1");
		System.out.println("Pass");
		Scanner sc = new Scanner(System.in);
		sc.next();
		cthr.finish();
		System.out.println("Finish");
		
		sc = new Scanner(System.in);
		sc.next();
		System.out.println("Begin");
		cthr.start("YZC", "Task2");
		System.out.println("Pass");
		sc = new Scanner(System.in);
		sc.next();
		cthr.finish();
		System.out.println("Finish");
	}
}

