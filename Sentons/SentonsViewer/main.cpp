#include "SentonsViewer.h"
#include "opencv2\opencv.hpp"

using namespace cv;
int main()
{
    SentonsViewer viewer("in.txt");
    viewer.display();
    return 0;
}
