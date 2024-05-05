#include "apps/SetupApp.h"

#include "logic/Installer.h"
#include "logic/Logger.h"

#include <thread>

using namespace tp;
using namespace tg;
using namespace logic;

SetupApp::SetupApp(HINSTANCE hInstance) {
  logI("Initializing app...");
  initWinAPI();

  _globalFlags = new GlobalFlags;
  _globalFlags->terminationRequest = false;
  _globalFlags->uninstallRequestFlag = false;
  _globalFlags->installRequestFlag = false;
  _globalFlags->updatingRequestFlag = false;
  _guiManager = GuiManager(hInstance, _globalFlags);
  logI("Initialized app!");
}

SetupApp::~SetupApp() {
  cleanWinAPI();

  delete _globalFlags;
}

void SetupApp::run() {
  logI("Running app...");
  std::thread coreThread(coreHandler, _globalFlags);

  _guiManager.run();

  coreThread.join();
  logI("App finished!");
}

void SetupApp::initWinAPI() {
  CoInitializeEx(nullptr, COINIT_MULTITHREADED);
}

void SetupApp::cleanWinAPI() {
  CoUninitialize();
}

void SetupApp::coreHandler(GlobalFlags* globalFlags) {
  logI("Starting core thread...");

  while (!globalFlags->terminationRequest &&
         !(globalFlags->installRequestFlag || globalFlags->uninstallRequestFlag || globalFlags->updatingRequestFlag)) {
    Sleep(100);
  }

  if (globalFlags->installRequestFlag) {
    logI("Installing...");
    Installer::install();
  } else if (globalFlags->uninstallRequestFlag) {
    logI("Uninstalling...");
    Installer::uninstall();
  } else if (globalFlags->updatingRequestFlag) {
    logI("Updating...");
    Installer::update();
  }

  globalFlags->terminationRequest = true;

  logI("Core thread finished!");
}
