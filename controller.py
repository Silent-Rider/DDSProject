import math


class FollowController:
    def __init__(self, k_lin=1, k_ang=4.0, stop_distance=50):
        self.k_lin = k_lin
        self.k_ang = k_ang
        self.stop_distance = stop_distance

    def compute_velocity(self, leader_pose, follower_pose):
        dx = leader_pose.x - follower_pose.x
        dy = leader_pose.y - follower_pose.y

        distance = math.sqrt(dx**2 + dy**2)
        target_angle = math.atan2(dy, dx)
        angle_error = target_angle - follower_pose.theta

        while angle_error > math.pi:
            angle_error -= 2 * math.pi
        while angle_error < -math.pi:
            angle_error += 2 * math.pi

        v = 0.0
        w = self.k_ang * angle_error

        if distance > self.stop_distance:
            v = self.k_lin * distance

        return v, w
