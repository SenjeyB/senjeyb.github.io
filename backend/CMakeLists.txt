cmake_minimum_required(VERSION 3.10)
project(backend)

set(CMAKE_CXX_STANDARD 17)

find_package(JsonCpp REQUIRED)
find_package(CURL REQUIRED)

add_executable(backend main.cpp database.cpp)
include_directories(${JSONCPP_INCLUDE_DIRS})
target_link_libraries(backend sqlite3 CURL::libcurl ${JSONCPP_LIBRARIES})
