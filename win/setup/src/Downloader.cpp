#include "logic/Downloader.h"

#include "logic/Logger.h"
#include "logic/WinWrapper.h"

#include <filesystem>

using namespace tp;
using namespace tp::logic;

bool Downloader::download() {
  std::wstring workingDirectory = L"C:\\Program Files\\ML\\";

  bool status = WinWrapper::executeProgram(L"cmd", L"/C mkdir \"C:\\Program Files\\ML\"", L"");
  if (!status) {
    return false;
  }

  status = WinWrapper::executeProgram(
      L"cmd", L"/C curl -o bin.zip https://storage.yandexcloud.net/...", workingDirectory);
  if (!status) {
    return false;
  }

  status = WinWrapper::executeProgram(L"cmd", L"/C tar -xf bin.zip", workingDirectory);
  if (!status) {
    return false;
  }

  status = WinWrapper::executeProgram(L"cmd", L"/C del /q bin.zip", workingDirectory);

  return status;
}

void Downloader::remove() {
  if (!WinWrapper::executeProgram(L"cmd", L"/C rmdir /s /q \"C:\\Program Files\\ML\"", L"")) {
    logI("Failed to remove binary folder");
  }

  std::wstring desktopPath = WinWrapper::getDesktopDirectory();
  if (!desktopPath.empty()) {
    desktopPath += L"\\ML.lnk\"";
    std::wstring command = L"/C del /f /q \"";
    command += desktopPath;

    if (!WinWrapper::executeProgram(L"cmd", command, L"")) {
      logI("Failed to remove icon");
    }
  }
}

bool Downloader::isDownloaded() {
  return WinWrapper::doesExist(L"C:\\Program Files\\ML", true);
}
