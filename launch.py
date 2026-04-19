import os
import signal
import subprocess
import sys
import time
import random


def start_process(command):
    return subprocess.Popen(command)


def main():
    triangle_count = 0
    if len(sys.argv) != 2:
        sys.exit(1)
    count_arg = sys.argv[1]
    try:
        triangle_count = int(count_arg)
    except:
        sys.exit(1)        
        
    current_dir = os.path.dirname(os.path.abspath(__file__))
    python_executable = sys.executable

    processes = []

    for i in range(1, triangle_count + 1):
        name = f"triangle{i}"
        x = random.randint(100, 700)
        y = random.randint(100, 500)

        command = [
            python_executable,
            os.path.join(current_dir, "triangle_node.py"),
            name,
            str(x),
            str(y)
        ]

        process = start_process(command)
        processes.append(process)

        time.sleep(0.2)

    for i in range(1, triangle_count):
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

        time.sleep(0.2)

    keyboard_process = subprocess.Popen([
        python_executable,
        os.path.join(current_dir, "keyboard_controller.py"),
        "triangle1"
    ])

    try:
        keyboard_process.wait()
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
                
        time.sleep(1.0)

        for process in processes:
            if process.poll() is None:
                process.kill()


if __name__ == "__main__":
    main()
