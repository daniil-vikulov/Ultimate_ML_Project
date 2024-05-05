#include "gui/GuiManager.h"

#include "logic/Downloader.h"
#include "logic/Logger.h"

using namespace tp;
using namespace tg;

ContentManager *CONTENT_MANAGER{};
tp::GlobalFlags *GLOBAL_FLAGS;

/// install/uninstall button
const int ACTION_BUTTON = (WM_USER + 1);
const int UPDATE_BUTTON = (WM_USER + 2);
const int RUSSIAN_BUTTON_ID = (WM_USER + 3);
const int ENGLISH_BUTTON_ID = (WM_USER + 4);

#define LANGUAGE_ENGLISH 1
#define LANGUAGE_RUSSIAN 2

int LANGUAGE = LANGUAGE_ENGLISH;

GuiManager::GuiManager(HINSTANCE hInstance, tp::GlobalFlags *globalFlags) {
    _hInstance = hInstance;
    GLOBAL_FLAGS = globalFlags;
    _globalFlags = globalFlags;
    _contentManager = new ContentManager();
    CONTENT_MANAGER = _contentManager;
}

GuiManager::GuiManager() {
    delete _contentManager;
}

void GuiManager::run() {
    HWND windowDescriptor = createWindow(_hInstance);
    if (windowDescriptor == nullptr) {
        _globalFlags->terminationRequest = true;
        return;
    }

    CONTENT_MANAGER->init(windowDescriptor);

    drawPrimaryLayout();

    Message message;
    while (true) {
        auto status = GetMessage(&message, nullptr, 0, 0);
        if (status == 0 || status == -1) {
            break;
        }

        if (_globalFlags->terminationRequest) {
            break;
        }

        TranslateMessage(&message);
        DispatchMessage(&message);
    }

    CONTENT_MANAGER->clear();

    DestroyWindow(windowDescriptor);
    UnregisterClass(CLASS_NAME, _hInstance);
}

HWND GuiManager::createWindow(HINSTANCE hInstance) {
    WindowClass windowClass = {};
    windowClass.lpfnWndProc = windowProcess;
    windowClass.hInstance = hInstance;
    windowClass.lpszClassName = CLASS_NAME;
    windowClass.hbrBackground = (HBRUSH) GetStockObject(WHITE_BRUSH); // CreateSolidBrush(RGB(200, 255, 211));

    if (!RegisterClass(&windowClass)) {
        return nullptr;
    }

    HWND hwnd = CreateWindowEx(0, CLASS_NAME, CLASS_NAME, WS_OVERLAPPEDWINDOW | WS_CLIPCHILDREN, CW_USEDEFAULT,
                               CW_USEDEFAULT, 600, 400, nullptr, nullptr, hInstance, nullptr);

    if (hwnd == nullptr) {
        return hwnd;
    }

    ShowWindow(hwnd, SW_NORMAL);

    return hwnd;
}

LRESULT GuiManager::windowProcess(HWND windowDescriptor, UINT message, WPARAM wParam, LPARAM lParam) {
    static HBRUSH hBrush = nullptr;

    switch (message) {
        case WM_CREATE:
            hBrush = CreateSolidBrush(RGB(200, 255, 211));
            break;

        case WM_CLOSE:
            logI("Received window close request");
            GLOBAL_FLAGS->terminationRequest = true;
            PostQuitMessage(0);
            break;

        case WM_DESTROY:
            if (hBrush) {
                DeleteObject(hBrush);
            }
            logI("Window is being destroyed");
            break;

        case WM_DRAWITEM: {
            auto *pDraw = (DRAWITEMSTRUCT *) lParam;
            if (pDraw->CtlType == ODT_BUTTON) {
                HDC hdc = pDraw->hDC;

                RECT rect = pDraw->rcItem;

                SelectObject(hdc, hBrush);

                RoundRect(hdc, rect.left, rect.top, rect.right, rect.bottom, 10, 10);

                SetTextColor(pDraw->hDC, RGB(0, 0, 0)); // White text
                SetBkMode(pDraw->hDC, TRANSPARENT);

                WCHAR buttonText[256];
                GetWindowTextW(pDraw->hwndItem, buttonText, sizeof(buttonText) / sizeof(buttonText[0]));
                DrawTextW(pDraw->hDC, buttonText, -1, &pDraw->rcItem, DT_CENTER | DT_SINGLELINE | DT_VCENTER);

                return TRUE;
            }

            break;
        }

        case WM_COMMAND:
            if (wParam == ACTION_BUTTON) {
                if (tp::logic::Downloader::isDownloaded()) {
                    GLOBAL_FLAGS->uninstallRequestFlag = true;
                    setUndecorated();
                    drawUninstallingLayout();
                } else {
                    GLOBAL_FLAGS->installRequestFlag = true;
                    setUndecorated();
                    drawInstallingLayout();
                }
            }
            if (wParam == UPDATE_BUTTON) {
                GLOBAL_FLAGS->updatingRequestFlag = true;
                setUndecorated();
                drawUpdatingLayout();
            }
            if (wParam == RUSSIAN_BUTTON_ID) {
                LANGUAGE = LANGUAGE_RUSSIAN;
                drawPrimaryLayout();
            }
            if (wParam == ENGLISH_BUTTON_ID) {
                LANGUAGE = LANGUAGE_ENGLISH;
                drawPrimaryLayout();
            }
            break;

        default:
            return DefWindowProc(windowDescriptor, message, wParam, lParam);
    }

    return 0;
}

void GuiManager::drawPrimaryLayout() {
    CONTENT_MANAGER->clear();

    if (tp::logic::Downloader::isDownloaded()) {
        const wchar_t *updateButtonText;
        const wchar_t *uninstallButtonText;

        if (LANGUAGE == LANGUAGE_RUSSIAN) {
            updateButtonText = L"Обновить";
            uninstallButtonText = L"Удалить";
        } else {
            updateButtonText = L"Update";
            uninstallButtonText = L"Uninstall";
        }

        CONTENT_MANAGER->addButton(UPDATE_BUTTON, updateButtonText, 175, 130, 250, 40);
        CONTENT_MANAGER->addButton(ACTION_BUTTON, uninstallButtonText, 175, 180, 250, 40);

    } else {
        const wchar_t *installButton;

        if (LANGUAGE == LANGUAGE_RUSSIAN) {
            installButton = L"Установить";
        } else {
            installButton = L"Install";
        }

        CONTENT_MANAGER->addButton(ACTION_BUTTON, installButton, 175, 150, 250, 40);
    }

    CONTENT_MANAGER->addButton(ENGLISH_BUTTON_ID, L"us", 540, 320, 30, 30);
    CONTENT_MANAGER->addButton(RUSSIAN_BUTTON_ID, L"ру", 500, 320, 30, 30);
}

void GuiManager::drawInstallingLayout() {
    CONTENT_MANAGER->clear();

    if (LANGUAGE == LANGUAGE_RUSSIAN) {
        CONTENT_MANAGER->addText2(L"Устанавливаем.", 0, 150, 600, 30);
        CONTENT_MANAGER->addText2(L"Пожалуйста, подождите...", 0, 180, 600, 30);
    } else if (LANGUAGE == LANGUAGE_ENGLISH) {
        CONTENT_MANAGER->addText2(L"Installing. Please, wait...", 0, 150, 600, 30);
    }
}

void GuiManager::drawUpdatingLayout() {
    CONTENT_MANAGER->clear();

    if (LANGUAGE == LANGUAGE_RUSSIAN) {
        CONTENT_MANAGER->addText2(L"Обновляем...", 0, 150, 600, 30);
        CONTENT_MANAGER->addText2(L"Пожалуйста, подождите...", 0, 180, 600, 30);
    } else if (LANGUAGE == LANGUAGE_ENGLISH) {
        CONTENT_MANAGER->addText2(L"Updating. Please, wait...", 0, 150, 600, 30);
    }
}

void GuiManager::drawUninstallingLayout() {
    CONTENT_MANAGER->clear();

    const wchar_t *text;

    if (LANGUAGE == LANGUAGE_RUSSIAN) {
        text = L"Удаляем...";
    } else if (LANGUAGE == LANGUAGE_ENGLISH) {
        text = L"Uninstalling...";
    }

    CONTENT_MANAGER->addText2(text, 0, 150, 600, 30);
}

void GuiManager::setUndecorated() {
    HWND windowDescriptor = CONTENT_MANAGER->getWindowDescriptor();

    LONG_PTR style = GetWindowLongA(windowDescriptor, GWL_STYLE);

    style &= ~(WS_CAPTION | WS_THICKFRAME);

    SetWindowLongPtr(windowDescriptor, GWL_STYLE, style);

    SetWindowPos(windowDescriptor, nullptr, 0, 0, 0, 0,
                 SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_NOOWNERZORDER);
}
