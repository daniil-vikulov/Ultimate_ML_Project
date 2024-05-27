#include "src/Tools.h"
#include <iostream>

int main() {
    std::vector<HWND> windows;
    EnumWindows(bg::EnumWindowsProc, reinterpret_cast<LPARAM>(&windows));

    std::cout << windows.size() << std::endl;

    return 0;
}