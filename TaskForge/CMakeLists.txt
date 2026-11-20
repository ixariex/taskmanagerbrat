cmake_minimum_required(VERSION 3.15)

project(TaskOptimizer LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Находим Python
find_package(Python COMPONENTS
    Interpreter
    Development.Module
    REQUIRED
)

# Находим pybind11
execute_process(
    COMMAND "${Python_EXECUTABLE}" -m pybind11 --cmakedir
    OUTPUT_VARIABLE pybind11_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

find_package(pybind11 CONFIG REQUIRED)

# Собираем Python-модуль
pybind11_add_module(
    task_optimizer
    bindings.cpp
    optimizer.cpp
)