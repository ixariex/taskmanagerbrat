#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "optimizer.h"

namespace py = pybind11;

PYBIND11_MODULE(task_optimizer, m) {

    m.doc() = "TaskForge C++ Task Optimizer";

    py::class_<Task>(m, "Task")

        .def(py::init<>())

        .def_readwrite("id", &Task::id)
        .def_readwrite("title", &Task::title)
        .def_readwrite("importance", &Task::importance)
        .def_readwrite("urgency", &Task::urgency)
        .def_readwrite("difficulty", &Task::difficulty)
        .def_readwrite("estimated_time", &Task::estimatedTime);

    m.def(
        "calculate_priority",
        &calculatePriority
    );

    m.def(
        "sort_tasks",
        &sortTasks
    );

    m.def(
        "find_best_task",
        &findBestTask
    );
}