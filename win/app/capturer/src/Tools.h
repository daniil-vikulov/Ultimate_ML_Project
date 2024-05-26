#include <Windows.h>
#include <string>
#include <vector>
#include <fstream>

namespace bg {
    struct Window {
        int x, y, width, height;
        HWND currentWindow, nextWindow;
        std::wstring windowName;
    };

    void saveWindow(std::vector<Window> &windows);

    std::wstring getWindowTitle(HWND hwnd);

    BOOL CALLBACK EnumWindowsProc(HWND hwnd, LPARAM lParam);
}