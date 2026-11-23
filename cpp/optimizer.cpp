#include "optimizer.h"

#include <algorithm>
#include <stdexcept>



static void validateTask(const Task& task) {

    if (task.importance < 1 || task.importance > 10) {
        throw std::invalid_argument(
            "Importance must be between 1 and 10"
        );
    }

    if (task.urgency < 1 || task.urgency > 10) {
        throw std::invalid_argument(
            "Urgency must be between 1 and 10"
        );
    }

    if (task.difficulty < 1 || task.difficulty > 10) {
        throw std::invalid_argument(
            "Difficulty must be between 1 and 10"
        );
    }
}




double calculatePriority(const Task& task) {

    validateTask(task);

    double priority =
        0.5 * task.importance +
        0.4 * task.urgency +
        0.1 * (11 - task.difficulty);

    return priority;
}




std::vector<Task> sortTasks(std::vector<Task> tasks) {

    
    for (const Task& task : tasks) {
        validateTask(task);
    }


    std::stable_sort(
        tasks.begin(),
        tasks.end(),
        [](const Task& a, const Task& b) {

            return calculatePriority(a) >
                   calculatePriority(b);

        }
    );

    return tasks;
}



Task findBestTask(const std::vector<Task>& tasks) {

    if (tasks.empty()) {
        throw std::invalid_argument(
            "Task list is empty"
        );
    }

    
    for (const Task& task : tasks) {
        validateTask(task);
    }

    auto bestTask = std::max_element(
        tasks.begin(),
        tasks.end(),
        [](const Task& a, const Task& b) {

            return calculatePriority(a) <
                   calculatePriority(b);

        }
    );

    return *bestTask;
}