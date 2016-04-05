cmake_minimum_required(VERSION 2.8)
project(pantheon)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/lib)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/bin)

set(BIN_DIRECTORY ${PROJECT_SOURCE_DIR}/bin/)
configure_file (
  "${PROJECT_SOURCE_DIR}/CMakeConfig.h.in"
  "${PROJECT_SOURCE_DIR}/CMakeConfig.h"
)
include_directories("${PROJECT_SOURCE_DIR}")

add_subdirectory(src/default-tcp bin)

add_executable(client src/client.cc)
add_executable(server src/server.cc) 
