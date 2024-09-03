cmake_minimum_required(VERSION 3.10)
project(backend)

set(CMAKE_CXX_STANDARD 17)

add_executable(backend main.cpp database.cpp)
find_package(CURL REQUIRED)
find_package(JsonCpp REQUIRED)
target_include_directories(backend PRIVATE ${JsonCpp_INCLUDE_DIRS})
target_link_libraries(backend PRIVATE ${JsonCpp_LIBRARIES})
target_link_libraries(backend PRIVATE sqlite3 CURL::libcurl)
