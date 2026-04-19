import math
import tkinter as tk

from cyclonedds.domain import DomainParticipant
from cyclonedds.topic import Topic
from cyclonedds.sub import DataReader

from dds_types import TrianglePose


DOMAIN_ID = 0

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

TRIANGLE_COUNT = 10
UPDATE_PERIOD_MS = 50
COLORS = ['blue', 'red', 'yellow', 'green', 'orange', 'brown', 'cyan', 'magenta', 'gray', 'black']


class TriangleGui:
    def __init__(self):
        self.participant = DomainParticipant(DOMAIN_ID)

        self.readers = {}
        self.latest_poses = {}

        self.triangle_items = {}
        self.text_items = {}

        self.root = tk.Tk()
        self.root.title("DDS Triangle GUI")

        self.canvas = tk.Canvas(
            self.root,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg="white"
        )
        self.canvas.pack()
        self.create_dds_readers()

    def create_dds_readers(self):
        for i in range(1, TRIANGLE_COUNT + 1):
            name = f"triangle{i}"
            topic_name = f"{name}_TrianglePose"

            topic = Topic(
                self.participant,
                topic_name,
                TrianglePose
            )

            reader = DataReader(
                self.participant,
                topic
            )

            self.readers[name] = reader

    def read_poses(self):
        for name, reader in self.readers.items():
            messages = reader.take(N=20)

            if len(messages) > 0:
                self.latest_poses[name] = messages[-1]

    def get_triangle_points(self, pose):
        size = 20

        local_points = [
            (size, 0),
            (-size, size / 2),
            (-size, -size / 2)
        ]

        points = []

        for local_x, local_y in local_points:
            rotated_x = (
                local_x * math.cos(pose.theta)
                - local_y * math.sin(pose.theta)
            )

            rotated_y = (
                local_x * math.sin(pose.theta)
                + local_y * math.cos(pose.theta)
            )

            screen_x = pose.x + rotated_x
            screen_y = WINDOW_HEIGHT - pose.y - rotated_y

            points.extend([screen_x, screen_y])

        return points

    def draw_triangle(self, pose):
        points = self.get_triangle_points(pose)
        name = pose.name
        
        i = int(name[len("triangle"):])
        color = COLORS[i % len(COLORS)]

        if name not in self.triangle_items:
            item_id = self.canvas.create_polygon(
                points,
                fill=color,
                outline="black"
            )

            self.triangle_items[name] = item_id
        else:
            item_id = self.triangle_items[name]
            self.canvas.coords(item_id, *points)

    def draw(self):
        self.canvas.delete("grid")

        for pose in self.latest_poses.values():
            self.draw_triangle(pose)

    def update(self):
        self.read_poses()
        self.draw()

        self.root.after(UPDATE_PERIOD_MS, self.update)

    def run(self):
        self.root.after(UPDATE_PERIOD_MS, self.update)
        self.root.mainloop()


def main():
    gui = TriangleGui()
    gui.run()


if __name__ == "__main__":
    main()
