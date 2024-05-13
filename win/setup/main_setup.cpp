#include "apps/SetupApp.h"

int WINAPI wWinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPWSTR lpCmdLine, int nCmdShow) {
  tp::SetupApp application(hInstance);
    application.run();

    return 0;
}