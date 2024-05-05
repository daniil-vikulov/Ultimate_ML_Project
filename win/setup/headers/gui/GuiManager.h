#pragma once

#include "ContentManager.h"
#include "apps/GlobalFlags.h"

#include <windows.h>

namespace tp::tg {
class GuiManager {
private:
  HINSTANCE _hInstance{};
  GlobalFlags* _globalFlags{};
  ContentManager *_contentManager{};

  static constexpr const char* CLASS_NAME = "Setup";

public:
  GuiManager(HINSTANCE hInstance, GlobalFlags* globalFlags);

  GuiManager();

  ///@brief starts Gui as a separate thread. Is not blocking
  ///@details Gui should be controlled via GlobalFlag
  void run();

private:
  static HWND createWindow(HINSTANCE hInstance);

  static LRESULT CALLBACK windowProcess(HWND windowDescriptor, UINT message, WPARAM wParam, LPARAM lParam);

  static void drawPrimaryLayout();

  static void drawInstallingLayout();

  static void drawUpdatingLayout();

  static void drawUninstallingLayout();

  static void setUndecorated();
};
} // namespace tp::tg