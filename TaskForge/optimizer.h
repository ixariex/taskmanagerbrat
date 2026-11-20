#ifndef OPTIMIZER_H
#define OPTIMIZER_H

#include <string>
#include <vector>

struct Task {
    int id;
    std::string title;

    int importance;  // Важность: 1–10
    int urgency;     // Срочность: 1–10
    int difficulty;  // Сложность: 1–10

    int estimatedTime; // Ожидаемое время выполнения в минутах
};

double calculatePriority(const Task& task);

std::vector<Task> sortTasks(std::vector<Task> tasks);

Task findBestTask(const std::vector<Task>& tasks);

#endif