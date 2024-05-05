cmake_minimum_required(VERSION 3.24)
project(Setup)

add_compile_options("$<$<C_COMPILER_ID:MSVC>:/utf-8>")
add_compile_options("$<$<CXX_COMPILER_ID:MSVC>:/utf-8>")

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ../../bin)

include_directories(headers)
include_directories(resources)
include_directories(../headers)
link_directories(../external/lib)

file(GLOB_RECURSE SRC src/*.cpp ../src/*.cpp)

add_executable(${PROJECT_NAME} WIN32 main_setup.cpp ${SRC})

set(LIBS Ole32.lib Shell32.lib winhttp.lib Rpcrt4.lib Crypt32.lib Shlwapi.lib comctl32.lib)

target_link_libraries(${PROJECT_NAME} ${LIBS})

SET_TARGET_PROPERTIES(${PROJECT_NAME} PROPERTIES LINK_FLAGS "/MANIFESTUAC:\"level='requireAdministrator' uiAccess='false'\" /SUBSYSTEM:WINDOWS")

add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
        COMMAND ${INSTALLER_SIGN_COMMAND}
        COMMENT "Signing ${INSTALLER_APP_NAME}"
)