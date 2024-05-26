#include "Tools.h"
#include <iostream>
#include <locale>
#include <codecvt>

void bg::saveWindow(std::vector<Window> &windows) {
    std::ofstream file("output/windows.txt");
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open file");
    }

    for (auto &w: windows) {
        file << w.x << "," << w.y << "," << w.width << "," << w.height << ","
             << reinterpret_cast<uintptr_t>(w.currentWindow) << ","
             << reinterpret_cast<uintptr_t>(w.nextWindow) << ","
             << std::wstring_convert<std::codecvt_utf8<wchar_t>>().to_bytes(w.windowName)
             << std::endl;
    }

    file.close();
}

std::wstring bg::getWindowTitle(HWND hwnd) {
    if (hwnd == nullptr) {
        return L"";
    }

    int length = GetWindowTextLengthW(hwnd) + 1;

    std::wstring title(length, L'\0');

    GetWindowTextW(hwnd, &title[0], length);

    return title.substr(0, title.find(L'\0'));
}

#pragma clang diagnostic push
#pragma ide diagnostic ignored "ConstantFunctionResult"

BOOL CALLBACK bg::EnumWindowsProc(HWND hwnd, LPARAM lParam) {
    if (!IsWindowVisible(hwnd)) {
        return TRUE;
    }

    auto windows = reinterpret_cast<std::vector<Window> *>(lParam);

    RECT rect;
    GetWindowRect(hwnd, &rect);

    HWND hwndNext = GetWindow(hwnd, GW_HWNDPREV);

    int width = rect.right - rect.left;
    int height = rect.bottom - rect.top;

    windows->push_back({rect.left, rect.top, width, height, hwnd, hwndNext,
                        getWindowTitle(hwnd)});

    HDC hdcScreen = GetDC(nullptr);
    HDC hdcWindow = GetDC(hwnd);
    HDC hdcMem = CreateCompatibleDC(hdcScreen);
    HBITMAP hBitmap = CreateCompatibleBitmap(hdcScreen, width, height);
    SelectObject(hdcMem, hBitmap);

    PrintWindow(hwnd, hdcMem, PW_CLIENTONLY);

    DeleteObject(hBitmap);
    DeleteDC(hdcMem);
    ReleaseDC(hwnd, hdcWindow);
    ReleaseDC(nullptr, hdcScreen);

    return TRUE;
}

#pragma clang diagnostic pop