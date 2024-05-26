#include "src/Tools.h"

int main() {
    std::vector<bg::Window> windows;
    EnumWindows(bg::EnumWindowsProc, reinterpret_cast<LPARAM>(&windows));
    saveWindow(windows);

    return 0;
}