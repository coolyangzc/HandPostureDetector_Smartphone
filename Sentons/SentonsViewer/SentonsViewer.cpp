#include "Common.h"
#include "SentonsViewer.h"


#include <cstdio>
#include <fstream>
#include <iostream>

using namespace std;
using namespace cv;


const int UP_MM= 116;
const int UP_PIXEL = 100;
const int DOWN_PIXEL = 620;
const int LEFT_PIXEL = 200;
const int RIGHT_PIXEL = 520;
SentonsViewer::SentonsViewer(string file = "")
{
    fileName = file;
    initImg = Mat(720, 720, CV_8UC3, Scalar(255, 255, 255));
    line(initImg, Point(LEFT_PIXEL, UP_PIXEL), Point(RIGHT_PIXEL, UP_PIXEL), Scalar(0, 0, 0), 1);
    line(initImg, Point(LEFT_PIXEL, DOWN_PIXEL), Point(RIGHT_PIXEL, DOWN_PIXEL), Scalar(0, 0, 0), 1);
    line(initImg, Point(LEFT_PIXEL, UP_PIXEL), Point(LEFT_PIXEL, DOWN_PIXEL), Scalar(0, 0, 0), 1);
    line(initImg, Point(RIGHT_PIXEL, UP_PIXEL), Point(RIGHT_PIXEL, DOWN_PIXEL), Scalar(0, 0, 0), 1);
}

SentonsViewer::~SentonsViewer()
{
    //dtor
}

void SentonsViewer::setFile(string file)
{
    fileName = file;
}

void SentonsViewer::readOneTouch(ifstream& fin)
{
    int barID, trackID, x, forceLvl;
    double posC, posU, posD;
    fin >> barID >> trackID >> forceLvl >> posC >> posU >> posD;
    posU = (1 - posU / UP_MM) * (DOWN_PIXEL - UP_PIXEL) + UP_PIXEL;
    posD = (1 - posD / UP_MM) * (DOWN_PIXEL - UP_PIXEL) + UP_PIXEL;

    if (barID == 0)
        x = RIGHT_PIXEL;
    else
        x = LEFT_PIXEL;
    line(img, Point(x, posU), Point(x, posD), Scalar(255, 0, 0), 3);

}

void SentonsViewer::display()
{
    ifstream fin(fileName.c_str());
    string s;
    rep(i, 3)
        getline(fin, s);

    int frame, n;
    double time, lastTime = 0, restTime = 0;

    while (fin >> frame)
    {
        fin >> time;
        restTime += time - lastTime;
        if (restTime < 1)
        {
            waitKey(1);
            restTime = 0;
        }
        else
        {
            waitKey(int(restTime));
            restTime -= int(restTime);
        }
        lastTime = time;
        img = initImg.clone();
        fin >> n;
        rep(i, n)
            readOneTouch(fin);
        imshow(fileName, img);
    }
}
