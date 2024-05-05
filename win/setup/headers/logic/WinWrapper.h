#pragma once

#include "Windows.h"

#include <string>
#include <vector>

namespace tp::logic {
class WinWrapper {
public:
  ///@brief executes program in windows PowerShell
  ///@details does not require Visual C++ Runtime installed
  ///@param filePath program's file to execute or cmd command
  ///@param flags startup parameters to pass
  ///@param workingDirectory directory, in which program will be executed. In case empty string is passed, current
  /// working directory will be used
  ///@param waitForTermination true - function blocks until program termination, false - does not block.
  ///@return true - program is executed, false - error occurred
  static bool executeProgram(const std::wstring& filePath, const std::wstring& flags,
                             const std::wstring& workingDirectory, bool waitForTermination = true);

  ///@brief creates desktop shortcut icon
  ///@param filePath - absolute path to the executable file
  ///@param shortcutName - name of the shortcut, which will be displayed on desktop
  ///@param workingDirectory - directory, in which file will be executed
  ///@param true - Icon is created, false - error occurred
  static bool createIcon(const std::wstring& filePath, const std::wstring& shortcutName,
                         const std::wstring& workingDirectory);

  ///@brief checks whether a specific file or directory exist
  ///@param path - absolute or relative path to the file or directory
  ///@param isDirectory - specifies that the object is a directory or a file
  static bool doesExist(const std::wstring& path, bool isDirectory);

  ///@brief generates an absolute path of the desktop directory
  ///@brief the format of the string: C:\\Users\\user\\Desktop
  ///@return absolute path. In case an error occurs, empty string will be returned
  static std::wstring getDesktopDirectory();

  ///@brief adds exception to Firewall
  ///@details adds both inbound and outbound exceptions
  ///@param ruleName - short name of the Firewall rule
  ///@param pathToFile - absolute path to the executable, which will enjoy the privilege
  ///@return true - successfully added exception, false - error occurred
  static bool addFirewallRule(const std::wstring& ruleName, const std::wstring& pathToFile);

  ///@brief removes all Firewall rules with the specified name
  ///@param ruleName - short name of the Firewall rule
  ///@return true - successfully removed exception, false - error occurred
  static bool removeFirewallRule(const std::wstring& ruleName);

  ///@briefloads resource's data into the vector
  ///@param data - should be an empty vector. Will be filled with bytes of the resource
  ///@param resourceID - id of the resource
  ///@param type - win API specific string wit the resource type
  ///@return true - successfully loaded resource, false - otherwise
  static bool extractResource(std::vector<char>& data, int resourceId, const char* type);

  ///@brief extracts resource from the current process resource section and saves in the same directory
  ///@param resourceName - name of the file, where the resource will be saved (with the extension)
  ///@param type - type of the resource. For example, L"RCDATA", L"BITMAP"
  ///@param fileName - name of the file, where the data will be saved
  ///@return true - successfully loaded, false - error occurred
  static bool extractResource(const char* resourceName, const char* type, const wchar_t* fileName);
};
} // namespace tp::logic