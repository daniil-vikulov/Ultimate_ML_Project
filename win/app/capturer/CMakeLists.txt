cmake_minimum_required(VERSION 3.22)
project(Capturer)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ../bin/)

set(CMAKE_CXX_STANDARD 17)

add_executable(Capturer main.cpp src/Tools.cpp)
