#include "src/Tools.h"
#include <iostream>

int main() {
    bg::saveToPng(bg::captureScreen(), L"output/screen.png");

    std::vector<HWND> windows;
    EnumWindows(bg::EnumWindowsProc, reinterpret_cast<LPARAM>(&windows));

    //bg::saveWindows(windows);

    //std::cout << windows.size() << std::endl;

    return 0;
}