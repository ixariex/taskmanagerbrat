
cmake_minimum_required(VERSION 3.15)

project(TaskOptimizer LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Python COMPONENTS
    Interpreter
    Development.Module
    REQUIRED
)

execute_process(
    COMMAND "${Python_EXECUTABLE}" -m pybind11 --cmakedir
    OUTPUT_VARIABLE pybind11_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
    COMMAND_ERROR_IS_FATAL ANY
)

find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(
    task_optimizer
    bindings.cpp
    optimizer.cpp
)

# Copy the compiled Python module into the TaskForge package.
set(TASKFORGE_PACKAGE_DIR
    "${CMAKE_CURRENT_SOURCE_DIR}/../Taskforge"
)

add_custom_command(
    TARGET task_optimizer
    POST_BUILD
    COMMAND "${CMAKE_COMMAND}" -E make_directory
        "${TASKFORGE_PACKAGE_DIR}"
    COMMAND "${CMAKE_COMMAND}" -E copy_if_different
        "$<TARGET_FILE:task_optimizer>"
        "${TASKFORGE_PACKAGE_DIR}/$<TARGET_FILE_NAME:task_optimizer>"
    COMMENT "Copying task_optimizer into TaskForge package"
)
