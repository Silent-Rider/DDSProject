import math
import time

from cyclonedds.domain import DomainParticipant
from cyclonedds.topic import Topic
from cyclonedds.sub import DataReader

from dds_types import TrianglePose


DOMAIN_ID = 0
TRIANGLE_COUNT = 10


def main():
    participant = DomainParticipant(DOMAIN_ID)

    readers = {}

    for i in range(1, TRIANGLE_COUNT + 1):
        name = f"triangle{i}"
        topic_name = f"{name}_TrianglePose"

        topic = Topic(
            participant,
            topic_name,
            TrianglePose
        )

        reader = DataReader(
            participant,
            topic
        )

        readers[name] = reader

    print("DDS pose listener for 10 triangles started")
    print()

    latest_poses = {}

    while True:
        for name, reader in readers.items():
            messages = reader.take(N=20)

            if len(messages) > 0:
                latest_poses[name] = messages[-1]

        print("-" * 70)

        for i in range(1, TRIANGLE_COUNT + 1):
            name = f"triangle{i}"
            pose = latest_poses.get(name)

            if pose is None:
                print(f"{name}: no data")
            else:
                print(
                    f"{name}: "
                    f"x={pose.x:7.2f}, "
                    f"y={pose.y:7.2f}, "
                    f"theta={math.degrees(pose.theta):7.2f} deg"
                )

        time.sleep(1.0)


if __name__ == "__main__":
    main()
