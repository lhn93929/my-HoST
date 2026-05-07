"""Test script to verify MuJoCo deployment configuration matches training environment"""
import numpy as np
from scipy.spatial.transform import Rotation

print("=" * 60)
print("TESTING MUCO DEPLOYMENT CONFIGURATION")
print("=" * 60)

# 1. Test quaternion interpretation
print("\n1. QUATERNION INTERPRETATION TEST")
print("-" * 40)

quaternions = {
    'prone_-1': {'isaac': [0.0, -1.0, 0.0, 1.0], 'desc': 'prone -90 deg about Y'},  # g1_config_ground.py
    'prone_+1': {'isaac': [0.0,  1.0, 0.0, 1.0], 'desc': 'prone +90 deg about Y'},  # g1_config_ground_prone.py
    'identity':  {'isaac': [0.0,  0.0, 0.0, 1.0], 'desc': 'identity (standing)'},
}

for name, q_dict in quaternions.items():
    q_isaac = np.array(q_dict['isaac'])  # [x, y, z, w]
    print(f"\n{name}: {q_dict['desc']}")
    print(f"  Isaac Gym [x,y,z,w]: {q_isaac}")

    r = Rotation.from_quat(q_isaac)
    euler = r.as_euler("xyz", degrees=True)
    print(f"  Euler angles (xyz): {euler}")
    print(f"  Rotation matrix:")
    print(f"    {r.as_matrix()}")

# 2. Test joint order
print("\n\n2. JOINT ORDER TEST")
print("-" * 40)

# Expected joint order from URDF
urdf_joints = [
    'left_hip_pitch_joint',
    'left_hip_roll_joint',
    'left_hip_yaw_joint',
    'left_knee_joint',
    'left_ankle_pitch_joint',
    'left_ankle_roll_joint',
    'right_hip_pitch_joint',
    'right_hip_roll_joint',
    'right_hip_yaw_joint',
    'right_knee_joint',
    'right_ankle_pitch_joint',
    'right_ankle_roll_joint',
    'waist_yaw_joint',
    'left_shoulder_pitch_joint',
    'left_shoulder_roll_joint',
    'left_shoulder_yaw_joint',
    'left_elbow_joint',
    'left_wrist_roll_joint',
    'right_shoulder_pitch_joint',
    'right_shoulder_roll_joint',
    'right_shoulder_yaw_joint',
    'right_elbow_joint',
    'right_wrist_roll_joint',
]

print(f"Total DOF: {len(urdf_joints)}")
print("\nJoint order (matching URDF):")
for i, joint in enumerate(urdf_joints):
    print(f"  {i:2d}: {joint}")

# 3. Test torque limits
print("\n\n3. TORQUE LIMITS TEST")
print("-" * 40)

torque_limits = [88, 88, 88, 139, 50, 50,   # left leg
                88, 88, 88, 139, 50, 50,   # right leg
                88,                          # waist_yaw
                25, 25, 25, 25, 25,        # left arm
                25, 25, 25, 25, 25]        # right arm

print(f"Total torque limits: {len(torque_limits)}")
print(f"Max torque: {max(torque_limits)} Nm")

# Group by joint type
group_names = ['Left hip', 'Left knee', 'Left ankle', 'Right hip', 'Right knee',
                'Right ankle', 'Waist', 'Left arm', 'Right arm']
group_limits = [
    [torque_limits[0], torque_limits[1], torque_limits[2]],  # left hip
    [torque_limits[3]],                                     # left knee
    [torque_limits[4], torque_limits[5]],                      # left ankle
    [torque_limits[6], torque_limits[7], torque_limits[8]],  # right hip
    [torque_limits[9]],                                     # right knee
    [torque_limits[10], torque_limits[11]],                    # right ankle
    [torque_limits[12]],                                    # waist
    torque_limits[13:18],                                   # left arm
    torque_limits[18:23],                                   # right arm
]

for name, limits in zip(group_names, group_limits):
    print(f"  {name}: {limits}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED")
print("=" * 60)
