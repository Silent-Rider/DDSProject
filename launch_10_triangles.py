import os
import signal
import subprocess
import sys
import time


TRIANGLE_COUNT = 10


def start_process(command):
    return subprocess.Popen(command)


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    python_executable = sys.executable

    processes = []

    print("Starting 10 TriangleNode processes...")
    print()

    start_x = 100
    start_y = 300
    distance = 50

    for i in range(1, TRIANGLE_COUNT + 1):
        name = f"triangle{i}"
        x = start_x - (i - 1) * distance
        y = start_y

        command = [
            python_executable,
            os.path.join(current_dir, "triangle_node.py"),
            name,
            str(x),
            str(y)
        ]

        process = start_process(command)
        processes.append(process)

        print(f"started {name}: x={x}, y={y}")

        time.sleep(0.2)

    print()
    print("Starting follower nodes...")
    print()

    for i in range(1, TRIANGLE_COUNT):
        leader_name = f"triangle{i}"
        follower_name = f"triangle{i + 1}"

        command = [
            python_executable,
            os.path.join(current_dir, "follower_node.py"),
            leader_name,
            follower_name
        ]

        process = start_process(command)
        processes.append(process)

        print(f"started follower: {follower_name} follows {leader_name}")

        time.sleep(0.2)

    print()
    print("Starting keyboard controller for triangle1...")
    print("Use:")
    print("  w - move forward")
    print("  s - move backward")
    print("  a - turn left")
    print("  d - turn right")
    print("  q - quit and stop all processes")
    print()

    keyboard_process = subprocess.Popen([
        python_executable,
        os.path.join(current_dir, "keyboard_controller.py"),
        "triangle1"
    ])

    try:
        keyboard_process.wait()
    finally:
        print()
        print("Stopping all DDS processes...")

        for process in processes:
            if process.poll() is None:
                process.terminate()

        time.sleep(1.0)

        for process in processes:
            if process.poll() is None:
                process.kill()

        print("All processes stopped")


if __name__ == "__main__":
    main()
