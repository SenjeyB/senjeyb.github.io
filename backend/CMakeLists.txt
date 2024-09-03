cmake_minimum_required(VERSION 3.10)
project(backend)

set(CMAKE_CXX_STANDARD 17)

find_package(nlohmann_json 3.2.0 REQUIRED)
add_executable(backend main.cpp database.cpp)
target_link_libraries(backend sqlite3 CURL::libcurl nlohmann_json::nlohmann_json)
