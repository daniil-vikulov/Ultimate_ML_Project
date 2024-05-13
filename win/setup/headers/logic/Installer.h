#pragma once

#include <vector>

namespace tp::logic {
    class Installer {
    public:
        ///@brief installs application.
        ///@return true - successfully installed, false - otherwise
        static bool install();

        static bool update();

        ///@brief tries to uninstall the previous version
        ///@details in case previous version has been found, removes binaries and uninstalls drivers
        static void uninstall();

      private:
        ///@brief tries to get bytes from the key file
        ///@return all bytes read from the file. Returns empty array in case of the error.
        static std::vector<char> readFile();

        ///@brief writes all bytes to the file.
        ///@param data byte array. If it is empty, does nothing.
        static void writeToFile(std::vector<char> &data);
    };
}