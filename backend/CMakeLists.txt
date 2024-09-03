cmake_minimum_required(VERSION 3.10)
project(backend)

set(CMAKE_CXX_STANDARD 17)

add_executable(backend main.cpp database.cpp)

find_package(CURL REQUIRED)

find_path(JSONCPP_INCLUDE_DIR json/json.h)
find_library(JSONCPP_LIBRARY jsoncpp)

if (JSONCPP_INCLUDE_DIR AND JSONCPP_LIBRARY)
    message(STATUS "Found JsonCpp library at ${JSONCPP_LIBRARY}")
    include_directories(${JSONCPP_INCLUDE_DIR})
    target_link_libraries(backend ${JSONCPP_LIBRARY})
else()
    message(FATAL_ERROR "Could not find JsonCpp library")
endif()

target_link_libraries(backend sqlite3 CURL::libcurl)
