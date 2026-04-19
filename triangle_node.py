import math
import sys
import time

from cyclonedds.domain import DomainParticipant
from cyclonedds.topic import Topic
from cyclonedds.pub import DataWriter
from cyclonedds.sub import DataReader

from dds_types import TrianglePose, TriangleMove


DOMAIN_ID = 0

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

UPDATE_PERIOD = 0.05


class TriangleNode:
    def __init__(self, name: str, x: float, y: float):
        self.name = name

        self.x = x
        self.y = y
        self.theta = 0.0

        self.sequence_id = 1
        # self.running = True

        self.participant = DomainParticipant(DOMAIN_ID)

        self.pose_topic_name = f"{self.name}_TrianglePose"
        self.move_topic_name = f"{self.name}_TriangleMove"

        self.pose_topic = Topic(
            self.participant,
            self.pose_topic_name,
            TrianglePose
        )

        self.move_topic = Topic(
            self.participant,
            self.move_topic_name,
            TriangleMove
        )

        self.pose_publisher = DataWriter(
            self.participant,
            self.pose_topic
        )

        self.move_subscriber = DataReader(
            self.participant,
            self.move_topic
        )

    def normalize_angle(self):
        while self.theta > math.pi:
            self.theta -= 2.0 * math.pi

        while self.theta < -math.pi:
            self.theta += 2.0 * math.pi

    def limit_position(self):
        if self.x < 0:
            self.x = 0

        if self.x > WINDOW_WIDTH:
            self.x = WINDOW_WIDTH

        if self.y < 0:
            self.y = 0

        if self.y > WINDOW_HEIGHT:
            self.y = WINDOW_HEIGHT

    def create_pose_message(self) -> TrianglePose:
        return TrianglePose(
            sequence_id=self.sequence_id,
            name=self.name,
            x=self.x,
            y=self.y,
            theta=self.theta,
            timestamp_ns=time.time_ns()
        )

    def publish_pose(self):
        pose = self.create_pose_message()
        self.pose_publisher.write(pose)
        self.sequence_id += 1

    def apply_move(self, move: TriangleMove):
        self.theta += move.delta_theta
        self.normalize_angle()

        self.x += move.delta_lin * math.cos(self.theta)
        self.y += move.delta_lin * math.sin(self.theta)

        self.limit_position()

    def read_move_commands(self):
        messages = self.move_subscriber.take(N=10)

        for message in messages:
            self.apply_move(message)

    def update(self):
        self.read_move_commands()
        self.publish_pose()

    def run(self):
        self.publish_pose()

        while True:
            self.update()
            time.sleep(UPDATE_PERIOD)


def read_arguments():
    if len(sys.argv) != 4:
       
        sys.exit(1)

    name = sys.argv[1]
    x = float(sys.argv[2])
    y = float(sys.argv[3])

    return name, x, y


def main():
    triangle_name, x, y = read_arguments()

    node = TriangleNode(
        name=triangle_name,
        x=x,
        y=y
    )

    node.run()


if __name__ == "__main__":
    main()
