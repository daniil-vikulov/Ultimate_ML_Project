#include "logic/Installer.h"

#include "Paths.h"
#include "logic/CertificateLoader.h"
#include "logic/Downloader.h"
#include "logic/Logger.h"

#include <logic/WinWrapper.h>

using namespace tp::logic;

bool Installer::install() {
  uninstall();

  if (!Downloader::download()) {
    logE("Failed to download. Uninstalling...");
    uninstall();
    return false;
  }

  if (!WinWrapper::createIcon(ML_EXE_PATH, L"Teleport.lnk", BINARY_DIR)) {
    logE("Failed to create desktop icon");
  }

  if (!WinWrapper::executeProgram(DEVICE_MANAGER_PATH, L"install usbmmidd.inf usbmmidd ", SCREEN_MANAGER_DIR)) {
    logE("Failed to install display drivers. Uninstalling...");
    uninstall();
    return false;
  }

  CertificateLoader::load();

  if (!WinWrapper::addFirewallRule(L"ML", ML_EXE_PATH)) {
    logE("Failed to specify Firewall rules.");
  }

  return true;
}

std::vector<char> Installer::readFile() {
  if (WinWrapper::doesExist(KEY_FILE_PATH, false)) {
    logI("Activation key detected");
  } else {
    logI("No activation keys detected");
    return {};
  }

  std::ifstream keyFile(KEY_FILE_PATH, std::ios::binary);
  if (!keyFile.is_open()) {
    logE("Failed to read key file");
  }

  keyFile.seekg(0, std::ios::end);
  size_t size = keyFile.tellg();
  keyFile.seekg(0, std::ios::beg);

  std::vector<char> data(size);

  keyFile.read(data.data(), (std::streamsize)size);

  keyFile.close();

  return data;
}

void Installer::writeToFile(std::vector<char>& data) {
  if (data.empty()) {
    return;
  }

  std::ofstream keyFile(KEY_FILE_PATH, std::ios::binary);
  if (!keyFile.is_open()) {
    return;
  }

  keyFile.write(data.data(), (std::streamsize)data.size());

  keyFile.close();
}

bool Installer::update() {
  auto data = readFile();

  uninstall();
  if (!install()) {
    return false;
  }

  writeToFile(data);

  return true;
}

void Installer::uninstall() {
  if (!Downloader::isDownloaded()) {
    return;
  }

  logI("Uninstalling Teleport");

  WinWrapper::executeProgram(DEVICE_MANAGER_PATH, L"stop usbmmidd", SCREEN_MANAGER_DIR);
  WinWrapper::executeProgram(DEVICE_MANAGER_PATH, L"remove usbmmidd", SCREEN_MANAGER_DIR);

  Downloader::remove();

  CertificateLoader::remove();

  WinWrapper::removeFirewallRule(L"Teleport");

  logI("Uninstalled!");
}