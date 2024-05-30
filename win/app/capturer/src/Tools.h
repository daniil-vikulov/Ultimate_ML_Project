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

    class GdiInitializer {
    private:
        ULONG_PTR _gdiPlusToken{};
    public:
        GdiInitializer();

        ~GdiInitializer();
    };

    void saveWindows(std::vector<HWND> &windows);

    ///@brief returns window's title based on its descriptor
    std::wstring getWindowTitle(HWND hwnd);

    ///@brief callback function, which saves descriptors of all visible windows into a std::vector
    ///@param lParam - std::vector<HWND> *windows
    BOOL CALLBACK EnumWindowsProc(HWND hwnd, LPARAM lParam);

    PBITMAPINFO createBitmapInfo(HBITMAP hBitmap);

    bool saveBitmap(HDC hdc, HBITMAP hBitmap, const std::wstring &filePath);

    bool saveToPng(HBITMAP hBitmap, const std::wstring &filePath);

    HBITMAP captureWindow(HWND hwnd);

    HBITMAP captureScreen();
}