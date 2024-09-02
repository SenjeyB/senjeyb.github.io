cmake_minimum_required(VERSION 3.10)
project(backend)

set(CMAKE_CXX_STANDARD 17)

add_executable(backend main.cpp database.cpp)
target_link_libraries(backend sqlite3)
find_package(CURL REQUIRED)
target_link_libraries(backend sqlite3 CURL::libcurl)
