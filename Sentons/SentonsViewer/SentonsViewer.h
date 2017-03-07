#ifndef SENTONSVIEWER_H
#define SENTONSVIEWER_H

#include <string>

class SentonsViewer
{
    public:
        SentonsViewer(std::string fileName);
        ~SentonsViewer();
        void setFile(std::string fileName);
        void display();
    private:
        std::string fileName;
        void drawTouch(double pos1, double pos2);
};

#endif // SENTONSVIEWER_H
