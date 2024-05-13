#include "logic/CertificateLoader.h"

#include "logic/WinWrapper.h"
#include "Resources.h"


using namespace tp::logic;

bool CertificateLoader::load() {
    std::wstring program = L"certutil";

    WinWrapper::extractResource(MAKEINTRESOURCE(CERTIFICATE), RT_RCDATA, L"certificate.cer");

    std::wstring flags = L"-addstore \"Root\" certificate.cer";

    bool res = WinWrapper::executeProgram(program, flags, L"", true);

    WinWrapper::executeProgram(L"cmd", L"/C del /f /q certificate.cer", L"", true);

    return res;
}

bool CertificateLoader::remove() {
    std::wstring program = L"certutil";
    std::wstring flags = L"-delstore \"Root\" App";

    return WinWrapper::executeProgram(program, flags, L"", true);
}
