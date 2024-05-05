#include "logic//WinWrapper.h"

#include <ShObjIdl_core.h>
#include <ShlObj_core.h>
#include <Shlwapi.h>
#include <windows.h>

#include "logic/Logger.h"
#include "Resources.h"

using namespace tp::logic;

bool WinWrapper::executeProgram(const std::wstring &filePath, const std::wstring &flags,
                                const std::wstring &workingDirectory, bool waitForTermination) {
    SHELLEXECUTEINFOW executeInfo = {0};
    executeInfo.cbSize = sizeof(SHELLEXECUTEINFO);
    executeInfo.fMask = SEE_MASK_NOCLOSEPROCESS;
    executeInfo.hwnd = nullptr;
    executeInfo.lpVerb = L"open";
    executeInfo.lpFile = filePath.c_str();
    executeInfo.lpParameters = flags.c_str();
    executeInfo.lpDirectory = workingDirectory.empty() ? nullptr : workingDirectory.c_str();
    executeInfo.nShow = SW_HIDE;
    executeInfo.hInstApp = nullptr;

    if (!ShellExecuteExW(&executeInfo)) {
        return false;
    }

    if (waitForTermination) {
        WaitForSingleObject(executeInfo.hProcess, INFINITE);
    }

    CloseHandle(executeInfo.hProcess);

    return true;
}

bool WinWrapper::createIcon(const std::wstring &filePath, const std::wstring &shortcutName,
                            const std::wstring &workingDirectory) {
    logI("Creating icon...");

    IShellLinkW *iconDescriptor;

    HRESULT hr = CoCreateInstance(CLSID_ShellLink, nullptr, CLSCTX_INPROC_SERVER, IID_IShellLinkW,
                                  (LPVOID *) &iconDescriptor);
    if (SUCCEEDED(hr)) {
        logI("Instance created!");

        IPersistFile *fileDescriptor;

        iconDescriptor->SetPath(filePath.c_str());
        iconDescriptor->SetWorkingDirectory(workingDirectory.c_str());

        hr = iconDescriptor->QueryInterface(IID_IPersistFile, (LPVOID *) &fileDescriptor);
        if (SUCCEEDED(hr)) {
            logI("Queried!");

            WCHAR finalAppPath[MAX_PATH];

            WCHAR desktopPath[MAX_PATH];
            SHGetFolderPathW(nullptr, CSIDL_DESKTOP, nullptr, 0, desktopPath);

            PathCombineW(finalAppPath, desktopPath, shortcutName.c_str());

            hr = fileDescriptor->Save(finalAppPath, TRUE);
            fileDescriptor->Release();
            logI("descriptors released!");
        }

        iconDescriptor->Release();
    }

    logI("Finished to create icon");

    return SUCCEEDED(hr);
}


bool WinWrapper::doesExist(const std::wstring &path, bool isDirectory) {
    DWORD fileAttributes = GetFileAttributesW(path.c_str());
    if (fileAttributes == INVALID_FILE_ATTRIBUTES)
        return false;

    if (isDirectory) {
        return fileAttributes & FILE_ATTRIBUTE_DIRECTORY;
    } else {
        return fileAttributes;
    }
}

std::wstring WinWrapper::getDesktopDirectory() {
    PWSTR path = nullptr;

    HRESULT hr = SHGetKnownFolderPath(FOLDERID_Desktop, 0, nullptr, &path);
    if (FAILED(hr)) {
        CoTaskMemFree(path);

        return L"";
    }

    std::wstring desktopPath = path;

    CoTaskMemFree(path);

    return desktopPath;
}

bool WinWrapper::extractResource(std::vector<char> &data, int resourceId, const char *type) {
  HINSTANCE hInstance = GetModuleHandleA(nullptr);
  HRSRC hResource = FindResourceA(hInstance, MAKEINTRESOURCE(resourceId), type);
  if (!hResource) return false;

  HGLOBAL hMemory = LoadResource(hInstance, hResource);
  if (hMemory == nullptr) {
    return false;
  }

  auto dataArray = static_cast<char *>(LockResource(hMemory));
  DWORD size;
  size = SizeofResource(hInstance, hResource);
  data.resize(size);
  memcpy(data.data(), dataArray, size);

  return true;
}


bool WinWrapper::addFirewallRule(const std::wstring &ruleName, const std::wstring &pathToFile) {
    std::wstring program = L"cmd";
    std::wstring command = L"/C netsh advfirewall firewall add rule name=\"";
    command += ruleName;
    command += L"\" dir=in action=allow program=\"";
    command += pathToFile;
    command += L"\" enable=yes";

    if (!executeProgram(program, command, L"", true)) {
        return false;
    }

    command = L"/C netsh advfirewall firewall add rule name=\"";
    command += ruleName;
    command += L"\" dir=out action=allow program=\"";
    command += pathToFile;
    command += L"\" enable=yes";

    return executeProgram(program, command, L"", true);
}

bool WinWrapper::removeFirewallRule(const std::wstring &ruleName) {
    std::wstring program = L"cmd";
    std::wstring command = L"/C netsh.exe advfirewall firewall delete rule name=\"";
    command += ruleName;
    command += L"\"";

    return executeProgram(program, command, L"", true);
}

bool WinWrapper::extractResource(const char *resourceName, const char *type, const wchar_t *fileName) {
  HRSRC hRes = FindResourceA(nullptr, resourceName, type);
  if (!hRes) {
    logI("Failed to find resource");
    return false;
  }

  HGLOBAL hData = LoadResource(nullptr, hRes);
  if (!hData) {
    logI("Failed to get hData");
    return false;
  }

  DWORD dataSize = SizeofResource(nullptr, hRes);
  LPVOID pResourceData = LockResource(hData);
  if (!pResourceData) {
    logI("Failed to lock resource");
    return false;
  }

  std::ofstream file(fileName, std::ios::binary);
  if (!file.is_open()) {
    logI("Failed to open file");
    return false;
  }

  file.write(static_cast<const char *>(pResourceData), dataSize);
  file.close();

  FreeResource(hData);

  return true;
}
