#include "Tools.h"
#include <iostream>
#include <locale>
#include <codecvt>
#include <gdiplus.h>

///@brief automatically initializes GdiPlus on program startup and releases on termination
[[maybe_unused]] bg::GdiInitializer initializer;

bg::GdiInitializer::GdiInitializer() {
    Gdiplus::GdiplusStartupInput startupInput;
    Gdiplus::GdiplusStartup(&_gdiPlusToken, &startupInput, nullptr);
}

bg::GdiInitializer::~GdiInitializer() {
    Gdiplus::GdiplusShutdown(_gdiPlusToken);
}

void bg::saveWindows(std::vector<HWND> &windows) {
    std::ofstream file(L"output/windows.txt");
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open file");
    }

    for (int i = 0; i < windows.size(); ++i) {
        std::wstring bitmapPath = L"output/";
        bitmapPath += std::to_wstring(i);
        bitmapPath += L".png";

        HWND hwnd = windows[i];

        RECT rect;
        GetClientRect(hwnd, &rect);

        HWND aboveHwnd = GetWindow(hwnd, GW_HWNDPREV); // If the window is most-top, aboveHwnd equals to hwnd

        int width = rect.right - rect.left;
        int height = rect.bottom - rect.top;

        if (width > 100 && height > 100) {
            saveToPng(captureWindow(hwnd), bitmapPath);
        }

        file << rect.left << "," << rect.top << "," << width << "," << height
             << ","
             << reinterpret_cast<uintptr_t>(hwnd) << ","
             << reinterpret_cast<uintptr_t>(aboveHwnd) << ","
             << std::wstring_convert<std::codecvt_utf8<wchar_t>>().to_bytes(getWindowTitle(hwnd))
             << std::endl;
    }

    file.close();
}

void bg::saveWindow(HWND hwnd, const wchar_t *file) {
    RECT rect;
    GetClientRect(hwnd, &rect);

    std::cout << rect.left << ' ' << rect.top << ' ' << rect.right << ' ' << rect.bottom << std::endl;

    HWND aboveHwnd = GetWindow(hwnd, GW_HWNDPREV); // If the window is most-top, aboveHwnd equals to hwnd

    int width = rect.right - rect.left;
    int height = rect.bottom - rect.top;

    if (width > 100 && height > 100) {
        saveToPng(captureWindow(hwnd), file);
    }
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

int counter = 0;

BOOL CALLBACK bg::EnumWindowsProc(HWND hwnd, LPARAM lParam) {

    if (!IsWindowVisible(hwnd)) {
        return TRUE;
    }

    //auto windows = reinterpret_cast<std::vector<HWND> *>(lParam);

    std::wstring path = std::to_wstring(counter++);
    path += L".png";

    saveWindow(hwnd, path.c_str());
    //windows->push_back(hwnd);

    return TRUE;
}

#pragma clang diagnostic pop

PBITMAPINFO bg::createBitmapInfo(HBITMAP hBitmap) {
    BITMAP bitmap;
    PBITMAPINFO bitmapInfo;
    WORD colorBits;

    if (!GetObject(hBitmap, sizeof(BITMAP), &bitmap)) {
        return nullptr;
    }

    colorBits = (WORD) (bitmap.bmPlanes + bitmap.bmBitsPixel);

    if (colorBits == 1) {
        colorBits = 1;
    } else if (colorBits <= 4) {
        colorBits = 4;
    } else if (colorBits <= 8) {
        colorBits = 8;
    } else if (colorBits <= 16) {
        colorBits = 16;
    } else if (colorBits <= 24) {
        colorBits = 24;
    } else {
        colorBits = 32;
    }

    if (colorBits < 24) {
        return nullptr;
    }

    bitmapInfo = static_cast<PBITMAPINFO>(LocalAlloc(LPTR, sizeof(BITMAPINFOHEADER)));

    bitmapInfo->bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    bitmapInfo->bmiHeader.biWidth = bitmap.bmWidth;
    bitmapInfo->bmiHeader.biHeight = bitmap.bmHeight;
    bitmapInfo->bmiHeader.biPlanes = bitmap.bmPlanes;
    bitmapInfo->bmiHeader.biBitCount = bitmap.bmBitsPixel;

    bitmapInfo->bmiHeader.biCompression = BI_RGB;

    bitmapInfo->bmiHeader.biSizeImage =
            ((bitmapInfo->bmiHeader.biWidth * colorBits + 31) & ~31) * bitmapInfo->bmiHeader.biHeight;

    bitmapInfo->bmiHeader.biClrImportant = 0;

    return bitmapInfo;
}

bool bg::saveBitmap(HDC hdc, HBITMAP hBitmap, const std::wstring &filePath) {
    PBITMAPINFO bitmapInfo = createBitmapInfo(hBitmap);
    auto bitmapInfoHeader = (PBITMAPINFOHEADER) bitmapInfo;
    auto lpBits = (LPBYTE) GlobalAlloc(GMEM_FIXED, bitmapInfoHeader->biSizeImage);

    if (!lpBits) {
        return false;
    }

    if (!GetDIBits(hdc, hBitmap, 0, (WORD) bitmapInfoHeader->biHeight, lpBits, bitmapInfo,
                   DIB_RGB_COLORS)) {
        return false;
    }

    HANDLE file = CreateFileW(filePath.c_str(),
                              GENERIC_READ | GENERIC_WRITE, (DWORD) 0, nullptr,
                              CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL,
                              (HANDLE) nullptr);
    if (file == INVALID_HANDLE_VALUE) {
        return false;
    }

    BITMAPFILEHEADER hdr;
    hdr.bfType = 0x4d42;
    hdr.bfSize = (DWORD) (sizeof(BITMAPFILEHEADER) +
                          bitmapInfoHeader->biSize + bitmapInfoHeader->biClrUsed
                                                     * sizeof(RGBQUAD) + bitmapInfoHeader->biSizeImage);
    hdr.bfReserved1 = 0;
    hdr.bfReserved2 = 0;

    hdr.bfOffBits = (DWORD) sizeof(BITMAPFILEHEADER) +
                    bitmapInfoHeader->biSize + bitmapInfoHeader->biClrUsed
                                               * sizeof(RGBQUAD);

    DWORD dwTmp;
    if (!WriteFile(file, (LPVOID) &hdr, sizeof(BITMAPFILEHEADER),
                   (LPDWORD) &dwTmp, nullptr)) {
        return false;
    }

    if (!WriteFile(file, (LPVOID) bitmapInfoHeader, sizeof(BITMAPINFOHEADER)
                                                    + bitmapInfoHeader->biClrUsed * sizeof(RGBQUAD),
                   (LPDWORD) &dwTmp, (nullptr))) {
        return false;
    }

    DWORD cb = bitmapInfoHeader->biSizeImage;
    BYTE *hp = lpBits;
    if (!WriteFile(file, (LPSTR) hp, (int) cb, (LPDWORD) &dwTmp, nullptr)) {
        return false;
    }

    CloseHandle(file);

    GlobalFree((HGLOBAL) lpBits);

    return true;
}

bool bg::saveToPng(HBITMAP hBitmap, const std::wstring &filePath) {
    Gdiplus::Bitmap bitmap(hBitmap, nullptr);
    CLSID imageId;
    if (FAILED(CLSIDFromString(L"{557CF406-1A04-11D3-9A73-0000F81EF32E}", &imageId))) {
        return false;
    }

    return bitmap.Save(filePath.c_str(), &imageId, nullptr) == Gdiplus::Status::Ok;
}

HBITMAP bg::captureWindow(HWND hwnd) {
    HDC hWindowDc = GetWindowDC(hwnd);

    HDC hCaptureDc = CreateCompatibleDC(hWindowDc);

    RECT rect;
    GetClientRect(hwnd, &rect);

    HBITMAP hBitmap = CreateCompatibleBitmap(hWindowDc, rect.right - rect.left, rect.bottom - rect.top);

    PrintWindow(hwnd, hCaptureDc, 0);
    HGDIOBJ hPrevObject = SelectObject(hCaptureDc, hBitmap);

//    BitBlt(hCaptureDc, rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top, hWindowDc,
//           0, 0, SRCCOPY);

    SelectObject(hCaptureDc, hPrevObject);

    DeleteDC(hCaptureDc);
    ReleaseDC(hwnd, hWindowDc);

    return hBitmap;
}

HBITMAP bg::captureScreen() {
    HDC hScreenDC = GetDC(nullptr);
    HDC hMemoryDC = CreateCompatibleDC(hScreenDC);

    int width = GetDeviceCaps(hScreenDC, HORZRES);
    int height = GetDeviceCaps(hScreenDC, VERTRES);

    std::cout << width << ' ' << height << std::endl;

    HBITMAP hBitmap = CreateCompatibleBitmap(hScreenDC, width, height);
    auto hOldBitmap = static_cast<HBITMAP>(SelectObject(hMemoryDC, hBitmap));

    BitBlt(hMemoryDC, 0, 0, width, height, hScreenDC, 0, 0, SRCCOPY);
    hBitmap = static_cast<HBITMAP>(SelectObject(hMemoryDC, hOldBitmap));
    DeleteDC(hMemoryDC);
    DeleteDC(hScreenDC);

    return hBitmap;
}