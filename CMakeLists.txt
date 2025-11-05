cmake_minimum_required(VERSION 3.10)
project(DroneVision LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)

# Include paths
include_directories(${PROJECT_SOURCE_DIR}/include)

# Source files
set(SOURCES
    src/main.cpp
    src/camera_module.cpp
)

add_executable(drone_vision ${SOURCES})

# Link libraries if needed later (e.g., OpenCV, TensorRT, MAVSDK)
# find_package(OpenCV REQUIRED)
# target_link_libraries(drone_vision ${OpenCV_LIBS})
