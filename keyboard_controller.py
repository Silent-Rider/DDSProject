import math
import sys
import termios
import time
import tty

from cyclonedds.domain import DomainParticipant
from cyclonedds.topic import Topic
from cyclonedds.pub import DataWriter

from dds_types import TriangleMove


DOMAIN_ID = 0


def get_single_key():
    file_descriptor = sys.stdin.fileno()
    old_settings = termios.tcgetattr(file_descriptor)

    try:
        tty.setraw(file_descriptor)
        key = sys.stdin.read(1)
    finally:
        termios.tcsetattr(file_descriptor, termios.TCSADRAIN, old_settings)

    return key


def key_to_move(key: str):
    move_step = 10.0
    rotate_step = math.radians(15.0)

    if key == "w":
        return move_step, 0.0

    if key == "s":
        return -move_step, 0.0

    if key == "a":
        return 0.0, rotate_step

    if key == "d":
        return 0.0, -rotate_step

    return 0.0, 0.0


def main():
    if len(sys.argv) != 2:
        sys.exit(1)

    triangle_name = sys.argv[1]

    participant = DomainParticipant(DOMAIN_ID)

    move_topic_name = f"{triangle_name}_TriangleMove"

    move_topic = Topic(
        participant,
        move_topic_name,
        TriangleMove
    )

    move_publisher = DataWriter(
        participant,
        move_topic
    )

    sequence_id = 1

    while True:
        key = get_single_key()

        if key == "q":
            print()
            print("Keyboard controller stopped")
            break

        if key not in ["w", "s", "a", "d"]:
            continue

        delta_lin, delta_theta = key_to_move(key)

        move = TriangleMove(
            sequence_id=sequence_id,
            name=triangle_name,
            delta_lin=delta_lin,
            delta_theta=delta_theta,
            timestamp_ns=time.time_ns()
        )

        move_publisher.write(move)
        sequence_id += 1


if __name__ == "__main__":
    main()
