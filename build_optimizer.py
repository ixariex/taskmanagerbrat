
"""
Build the TaskForge C++ Task Optimizer.

Run this script directly from PyCharm.
It configures CMake, builds the extension and copies
the resulting .pyd file into the Taskforge package.
"""

from pathlib import Path
import shutil
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parent

CPP_SOURCE = PROJECT_ROOT / "cpp"
BUILD_DIRECTORY = PROJECT_ROOT / "build" / "cpp-optimizer"
TASKFORGE_DIRECTORY = PROJECT_ROOT / "Taskforge"


def find_cmake() -> str:
    """Find the CMake executable."""

    cmake = shutil.which("cmake")

    if cmake:
        return cmake

    fallback = Path(r"C:\Program Files\CMake\bin\cmake.exe")

    if fallback.exists():
        return str(fallback)

    raise FileNotFoundError(
        "CMake was not found. Please check your CMake installation."
    )


def run_command(command: list[str]) -> None:
    """Execute a build command and stop if it fails."""

    print("\nRunning:")
    print(" ".join(f'"{part}"' for part in command))
    print("-" * 60)

    subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=True
    )


def main() -> None:
    print("=" * 60)
    print("TASKFORGE C++ OPTIMIZER BUILD")
    print("=" * 60)

    if not CPP_SOURCE.exists():
        raise FileNotFoundError("The cpp directory was not found.")

    if not (CPP_SOURCE / "CMakeLists.txt").exists():
        raise FileNotFoundError("CMakeLists.txt was not found.")

    if not TASKFORGE_DIRECTORY.exists():
        raise FileNotFoundError("The Taskforge package was not found.")

    cmake = find_cmake()

    print("\nPython interpreter:")
    print(sys.executable)

    print("\nCMake executable:")
    print(cmake)

    # Step 1: Configure the C++ project.
    configure_command = [
        cmake,
        "-S", str(CPP_SOURCE),
        "-B", str(BUILD_DIRECTORY),
        "-G", "Visual Studio 17 2022",
        "-A", "x64",
        f"-DPython_EXECUTABLE={sys.executable}",
    ]

    run_command(configure_command)

    # Step 2: Compile the C++ extension.
    build_command = [
        cmake,
        "--build", str(BUILD_DIRECTORY),
        "--config", "Release",
        "--parallel",
    ]

    run_command(build_command)

    # Step 3: Verify the compiled module.
    modules = list(
        TASKFORGE_DIRECTORY.glob("task_optimizer*.pyd")
    )

    if not modules:
        raise RuntimeError(
            "Build finished, but task_optimizer.pyd was not found "
            "inside the Taskforge directory."
        )

    print("\n" + "=" * 60)
    print("BUILD COMPLETED SUCCESSFULLY!")
    print("=" * 60)

    print("\nCompiled module:")

    for module in modules:
        print(module)


if __name__ == "__main__":
    main()
