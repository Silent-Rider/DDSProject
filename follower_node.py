import math
import sys
import time

from cyclonedds.domain import DomainParticipant
from cyclonedds.topic import Topic
from cyclonedds.pub import DataWriter
from cyclonedds.sub import DataReader

from dds_types import TrianglePose, TriangleMove
from controller import FollowController


DOMAIN_ID = 0
UPDATE_PERIOD = 0.1


class FollowerNode:
    def __init__(self, leader_name: str, follower_name: str):
        self.leader_name = leader_name
        self.follower_name = follower_name

        self.leader_pose = None
        self.follower_pose = None

        self.move = FollowController()

        self.participant = DomainParticipant(DOMAIN_ID)

        self.leader_pose_topic = Topic(
            self.participant,
            f"{self.leader_name}_TrianglePose",
            TrianglePose
        )

        self.follower_pose_topic = Topic(
            self.participant,
            f"{self.follower_name}_TrianglePose",
            TrianglePose
        )

        self.follower_move_topic = Topic(
            self.participant,
            f"{self.follower_name}_TriangleMove",
            TriangleMove
        )

        self.leader_pose_reader = DataReader(
            self.participant,
            self.leader_pose_topic
        )

        self.follower_pose_reader = DataReader(
            self.participant,
            self.follower_pose_topic
        )

        self.move_writer = DataWriter(
            self.participant,
            self.follower_move_topic
        )

    def read_latest_pose(self, reader):
        messages = reader.take(N=20)

        if len(messages) == 0:
            return None

        return messages[-1]

    def read_poses(self):
        new_leader_pose = self.read_latest_pose(self.leader_pose_reader)
        new_follower_pose = self.read_latest_pose(self.follower_pose_reader)

        if new_leader_pose is not None:
            self.leader_pose = new_leader_pose

        if new_follower_pose is not None:
            self.follower_pose = new_follower_pose

    def publish_move(self, delta_lin: float, delta_theta: float):
        move_msg = TriangleMove(
            name=self.follower_name,
            delta_lin=delta_lin,
            delta_theta=delta_theta,
            timestamp_ns=time.time_ns()
        )

        self.move_writer.write(move_msg)

    def update(self):
        self.read_poses()

        if self.leader_pose is None or self.follower_pose is None:
            return

        v, w = self.move.compute_velocity(
            self.leader_pose,
            self.follower_pose
        )

        delta_lin = v * UPDATE_PERIOD
        delta_theta = w * UPDATE_PERIOD

        self.publish_move(delta_lin, delta_theta)

    def run(self):
        while True:
            self.update()
            time.sleep(UPDATE_PERIOD)


def main():
    if len(sys.argv) != 3:
        sys.exit(1)

    leader_name = sys.argv[1]
    follower_name = sys.argv[2]

    node = FollowerNode(
        leader_name=leader_name,
        follower_name=follower_name
    )

    node.run()


if __name__ == "__main__":
    main()
