#pragma once

#include <string>

namespace tp::logic {
class Downloader {
public:
  ///@brief downloads latest version of available binaries
  ///@return true - successfully downloaded, false - error occurred.
  static bool download();

  ///@brief tries to delete binaries of a previous version and the desktop icon
  static void remove();

  ///@brief checks whether binaries are already downloaded
  static bool isDownloaded();
};
} // namespace tp::logic