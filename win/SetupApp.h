#pragma once

#include "gui/GuiManager.h"

namespace ti {
    class SetupApp {
    private:
        GlobalFlags *_globalFlags;
        gui::GuiManager _guiManager{};

    public:
        explicit SetupApp(HINSTANCE hInstance);

        ~SetupApp();

        ///@brief starts application with being blocking until app's termination
        void run();

    private:
        ///@brief initializes necessary win API libraries for proper execution
        static void initWinAPI();

        ///@brief release all initialized resource of WinAPI libraries
        static void cleanWinAPI();
    };
}