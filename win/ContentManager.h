#pragma once

#include <stack>
#include <windows.h>

namespace ti::gui {
    using WindowDescriptor = HWND;
    using Message = MSG;
    using WindowClass = WNDCLASS;

    class ContentManager {
    private:
        WindowDescriptor _windowDescriptor{};
        std::stack<WindowDescriptor> _widgetList;

    public:
        /**
         * @brief Construct a new Content Manager object
         * @param windowDescriptor WinAPI HWND descriptor of the current window
         */
        void init(WindowDescriptor windowDescriptor);

        /**
         * @brief Add a button to the current window
         * @param id unique id of the button
         * @param x left coordinate of the button
         * @param y upper coordinate of the button
         */
        void addButton(int id, const wchar_t *text, int x, int y, int width, int height);


        /**
         * @brief Add a textbox with fixed text to the current window
         * @param id unique id of the textbox
         * @param x left coordinate of the textbox
         * @param y upper coordinate of the textbox
         */
        [[maybe_unused]] void addTextBox(int id, const wchar_t *text, int x, int y, int width, int height);

        /**
        * @brief Add a text to the current window
        * @param id unique id of the text
        * @param x left coordinate of the text
        * @param y upper coordinate of the text
        */
        [[maybe_unused]] void addText(int id, const wchar_t *text, int x, int y, int width, int height);

        ///@brief updates window, forcing window repainting
        void update();

        ///@brief removes all the internal widgets from the window
        void clear();
    };
}