import numpy as np
from scipy.spatial.transform import Rotation as R


def get_gravity_orientation(quaternion):
    qw = quaternion[0]
    qx = quaternion[1]
    qy = quaternion[2]
    qz = quaternion[3]

    gravity_orientation = np.zeros(3)

    gravity_orientation[0] = 2 * (-qz * qx + qw * qy)
    gravity_orientation[1] = -2 * (qz * qy + qw * qx)
    gravity_orientation[2] = 1 - 2 * (qw * qw + qz * qz)

    return gravity_orientation


def get_projected_gravity(quaternion):
    """
    Compute projected gravity vector from quaternion (rotation from world to body frame).
    Gravity in world frame is (0, 0, -1), so projected gravity is
    world z-axis rotated to body frame.

    Quaternion input order: [w, x, y, z] (MuJoCo/real robot convention)

    Implementation matches Isaac Gym's quat_rotate_inverse:
    v' = v * (2*q_w^2 - 1) + q_vec x v * (2*q_w) + q_vec x (q_vec x v) * (2)
    """
    # Input quaternion is [w, x, y, z]
    qw, qx, qy, qz = quaternion[0], quaternion[1], quaternion[2], quaternion[3]
    q_vec = np.array([qx, qy, qz])
    v = np.array([0.0, 0.0, -1.0])  # Gravity in world frame

    # v' = v * (2*q_w^2 - 1) + q_vec x v * (2*q_w) + q_vec * (q_vec · v) * 2
    a = v * (2.0 * qw**2 - 1.0)
    b = np.cross(q_vec, v) * (2.0 * qw)
    c = q_vec * np.dot(q_vec, v) * 2.0
    projected_gravity = a - b + c

    return projected_gravity


def transform_imu_data(waist_yaw, waist_yaw_omega, imu_quat, imu_omega):
    RzWaist = R.from_euler("z", waist_yaw).as_matrix()
    R_torso = R.from_quat([imu_quat[1], imu_quat[2], imu_quat[3], imu_quat[0]]).as_matrix()
    R_pelvis = np.dot(R_torso, RzWaist.T)
    w = np.dot(RzWaist, imu_omega[0]) - np.array([0, 0, waist_yaw_omega])
    return R.from_matrix(R_pelvis).as_quat()[[3, 0, 1, 2]], w
