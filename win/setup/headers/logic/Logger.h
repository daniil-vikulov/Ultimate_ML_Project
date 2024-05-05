#pragma once

#include <fstream>
#include <iostream>
#include <vector>

#ifdef TESTING_BUILD

namespace tp::logic {
class Logger {
private:
  ///@brief Holds info about redirected out streams. Should be used for saving data
  struct RedirectionInfo {
    std::ostream* originalStream;
    std::streambuf* originalBuffer;
    std::ofstream* fileStream;
  };

public:
  template <typename... Args>
  static void info(const char* filePath, Args... args) {
    auto redirectionInfo = redirectStreams();

    std::cout << parseFileName("[INFO]", filePath);
    ((std::cout << args << ' '), ...) << '\n';

    refresh(redirectionInfo);
  }

  template <typename... Args>
  static void fatal(const char* filePath, Args... args) {
    auto redirectionInfo = redirectStreams();

    std::cout << parseFileName("[FATAL]", filePath);
    ((std::cout << args << ' '), ...) << std::endl;

    refresh(redirectionInfo);

    abort();
  }

  template <typename... Args>
  static void error(const char* filePath, Args... args) {
    auto redirectionInfo = redirectStreams();

    std::cout << parseFileName("[ERROR]", filePath);
    ((std::cout << args << ' '), ...) << '\n';

    refresh(redirectionInfo);
  }

  template <typename... Args>
  static void warning(const char* filePath, Args... args) {
    auto redirectionInfo = redirectStreams();

    std::cout << parseFileName("[WARNING]", filePath);
    ((std::cout << args << ' '), ...) << '\n';

    refresh(redirectionInfo);
  }

private:
  ///@brief extracts fileName and format it for logging
  static std::string parseFileName(const char* logType, const char* filePath);

  ///@brief redirects stdout to logger files
  static RedirectionInfo redirectStreams();

  ///@brief saves content to file and clean all the buffered data
  static void refresh(RedirectionInfo redirectionInfo);
};
} // namespace tp::logic

#define logI(...) tp::logic::Logger::info(__FILE__, __VA_ARGS__)
#define logF(...) tp::logic::Logger::fatal(__FILE__, __VA_ARGS__)
#define logE(...) tp::logic::Logger::error(__FILE__, __VA_ARGS__)
#define logW(...) tp::logic::Logger::warning(__FILE__, __VA_ARGS__)

#else

namespace tp::logic {}

#define logI(...)
#define logF(...) abort()
#define logS(...)
#define logE(...)
#define logW(...)

#endif