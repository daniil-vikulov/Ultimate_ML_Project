#include "logic/Logger.h"

#ifdef TESTING_BUILD

#include <sstream>
#include <iomanip>

using namespace tp::logic;

std::string Logger::parseFileName(const char *logType, const char *filePath) {
    std::string src = filePath;
    std::string ans;

    int i = (int) src.size() - 1;
    while (src[i] != '\\' && src[i] != '/') {
        ans.push_back(src[i]);
        --i;
    }

    ans += "[";

    std::reverse(ans.begin(), ans.end());

    ans += "]";

    std::ostringstream oss;
    oss << std::left << std::setw(15) << std::setfill(' ') << logType;

    oss << std::left << std::setw(30) << std::setfill(' ') << ans;

    return oss.str();
}

Logger::RedirectionInfo Logger::redirectStreams() {
    RedirectionInfo info{};

    auto *fileStream = new std::ofstream;
    info.fileStream = fileStream;
    info.originalStream = &std::cout;
    info.originalBuffer = std::cout.rdbuf();

    std::string filename = "Logs.txt";

    info.fileStream->open(filename, std::ios::out | std::ios::app);
    info.originalStream->rdbuf(fileStream->rdbuf());

    return info;
}

void Logger::refresh(Logger::RedirectionInfo redirectionInfo) {
    redirectionInfo.originalStream->rdbuf(redirectionInfo.originalBuffer);
    if (redirectionInfo.fileStream->is_open()) {
        redirectionInfo.fileStream->close();
    }

    delete redirectionInfo.fileStream;
}
#endif