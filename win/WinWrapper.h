#pragma once

#include <string>

namespace ti::logic {
    class WinWrapper {
    public:
        ///@brief executes program in windows PowerShell
        ///@details does not require Visual C++ Runtime installed
        ///@param filePath program's file to execute or cmd command
        ///@param flags startup parameters to pass
        ///@param workingDirectory directory, in which program will be executed. In case empty string is passed, current working directory will be used
        ///@param waitForTermination true - function blocks until program termination, false - does not block.
        ///@return true - program is executed, false - error occurred
        static bool executeProgram(const std::wstring &filePath, const std::wstring &flags,
                                   const std::wstring &workingDirectory, bool waitForTermination = true);

        ///@brief creates desktop shortcut icon
        ///@param filePath - absolute path to the executable file
        ///@param shortcutName - name of the shortcut, which will be displayed on desktop
        ///@param workingDirectory - directory, in which file will be executed
        ///@param true - Icon is created, false - error occurred
        static bool createIcon(const std::wstring &filePath, const std::wstring &shortcutName, const std::wstring &workingDirectory);

        ///@brief checks whether a specific file or directory exist
        ///@param path - absolute or relative path to the file or directory
        ///@param isDirectory - specifies that the object is a directory or a file
        static bool doesExist(const std::wstring &path, bool isDirectory);
    };
}