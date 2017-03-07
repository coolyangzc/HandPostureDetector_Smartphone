#include "Common.h"
#include "SentonsViewer.h"
#include "opencv2\opencv.hpp"

#include <cstdio>
#include <fstream>
#include <iostream>

using namespace std;
using namespace cv;

SentonsViewer::SentonsViewer(string file = "")
{
    fileName = file;
}

SentonsViewer::~SentonsViewer()
{
    //dtor
}

void SentonsViewer::setFile(string file)
{
    fileName = file;
}

void drawTouch(double pos1, double pos2)
{

}

void SentonsViewer::display()
{
    ifstream fin(fileName.c_str());
    string s;
    rep(i, 3)
        getline(fin, s);
    int frame, n;
    double time, lastTime;
    Mat img(720, 1280, CV_8UC3);
    while (fin >> frame)
    {
        fin >> time;
        waitKey(time - lastTime);
        lastTime = time;
        img = Mat::zeros(720, 1280, CV_8UC3);
        fin >> n;
        rep(i, n)
        {

        }
        imshow(fileName, img);
    }
}
