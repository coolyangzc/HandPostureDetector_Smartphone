#ifndef SENTONSVIEWER_H
#define SENTONSVIEWER_H

#include <string>
#include "opencv2\opencv.hpp"

class SentonsViewer
{
    public:
        SentonsViewer(std::string fileName);
        ~SentonsViewer();
        void setFile(std::string fileName);
        void display();
    private:
        std::string fileName;
        cv::Mat img, initImg;
        void readOneTouch(std::ifstream& fin);
};

#endif // SENTONSVIEWER_H
