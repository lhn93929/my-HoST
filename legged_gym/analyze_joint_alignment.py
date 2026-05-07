#!/usr/bin/env python3
"""
分析g1_config_ground.py与deploy_mujoco的关节对齐
"""

# MuJoCo XML actuator顺序 (从XML中读取):
mujoco_actuator_order = [
    'left_hip_pitch_joint', 'left_hip_roll_joint', 'left_hip_yaw_joint',
    'left_knee_joint', 'left_ankle_pitch_joint', 'left_ankle_roll_joint',
    'right_hip_pitch_joint', 'right_hip_roll_joint', 'right_hip_yaw_joint',
    'right_knee_joint', 'right_ankle_pitch_joint', 'right_ankle_roll_joint',
    'waist_yaw_joint',
    'left_shoulder_pitch_joint', 'left_shoulder_roll_joint', 'left_shoulder_yaw_joint',
    'left_elbow_joint', 'left_wrist_roll_joint',
    'right_shoulder_pitch_joint', 'right_shoulder_roll_joint', 'right_shoulder_yaw_joint',
    'right_elbow_joint', 'right_wrist_roll_joint'
]

# g1_config_ground.py中default_joint_angles的字典:
# 注意：字典的顺序在Python 3.7+中是插入顺序
training_joint_dict = {
    'left_hip_yaw_joint': 0.0,
    'left_hip_roll_joint': 0.0,
    'left_hip_pitch_joint': -0.1,
    'left_knee_joint': 0.3,
    'left_ankle_pitch_joint': -0.2,
    'left_ankle_roll_joint': 0.0,
    'left_wrist_roll_joint': 0.0,
    'right_hip_yaw_joint': 0.0,
    'right_hip_roll_joint': 0.0,
    'right_hip_pitch_joint': -0.1,
    'right_knee_joint': 0.3,
    'right_ankle_pitch_joint': -0.2,
    'right_ankle_roll_joint': 0.0,
    'right_wrist_roll_joint': 0.0,
    'waist_yaw_joint': 0.0,
    'waist_pitch_joint': 0.0,  # 29DOF才有，23DOF无
    'waist_roll_joint': 0.0,    # 29DOF才有，23DOF无
    'left_shoulder_pitch_joint': 0.0,
    'left_shoulder_roll_joint': 0.0,
    'left_shoulder_yaw_joint': 0.0,
    'left_elbow_joint': 0.8,
    'right_shoulder_pitch_joint': 0.0,
    'right_shoulder_roll_joint': 0.0,
    'right_shoulder_yaw_joint': 0.0,
    'right_elbow_joint': 0.8,
}

# g1_config_ground.py中asset配置的关节组:
training_left_leg_joints = ['left_hip_yaw_joint', 'left_hip_roll_joint', 'left_hip_pitch_joint',
                           'left_knee_joint', 'left_ankle_pitch_joint', 'left_ankle_roll_joint']
training_right_leg_joints = ['right_hip_yaw_joint', 'right_hip_roll_joint', 'right_hip_pitch_joint',
                            'right_knee_joint', 'right_ankle_pitch_joint', 'right_ankle_roll_joint']
training_left_arm_joints = ['left_shoulder_pitch_joint', 'left_shoulder_roll_joint', 'left_shoulder_yaw_joint',
                           'left_elbow_joint', 'left_wrist_roll_joint']
training_right_arm_joints = ['right_shoulder_pitch_joint', 'right_shoulder_roll_joint', 'right_shoulder_yaw_joint',
                            'right_elbow_joint', 'right_wrist_roll_joint']
training_waist_joints = ['waist_yaw_joint']

# 完整的训练关节顺序 (推测，按照asset的顺序组合):
training_joint_order = (
    training_left_leg_joints + training_right_leg_joints +
    training_waist_joints + training_left_arm_joints + training_right_arm_joints
)

print("=" * 80)
print("关节顺序对比分析")
print("=" * 80)

print(f"\n{'':30} {'MuJoCo顺序':30} {'训练顺序':30}")
print("-" * 90)

for i in range(23):
    mj_name = mujoco_actuator_order[i] if i < len(mujoco_actuator_order) else ''
    train_name = training_joint_order[i] if i < len(training_joint_order) else ''
    match = '✓' if mj_name == train_name else '✗'
    print(f"{i:2d}: {match} {mj_name:30} {train_name:30}")

print("\n" + "=" * 80)
print("结论: 需要创建映射表")
print("=" * 80)

# 找出每个训练关节在MuJoCo中的索引:
train_to_mujoco_map = []
for train_joint in training_joint_order:
    if train_joint in mujoco_actuator_order:
        idx = mujoco_actuator_order.index(train_joint)
        train_to_mujoco_map.append(idx)
        print(f"{train_joint}: mujoco index {idx}")
    else:
        print(f"WARNING: {train_joint} not found in MuJoCo")

print(f"\n映射表 (训练索引 -> MuJoCo索引): {train_to_mujoco_map}")

# 反之, MuJoCo索引 -> 训练索引:
mujoco_to_train_map = []
for mj_joint in mujoco_actuator_order:
    if mj_joint in training_joint_order:
        idx = training_joint_order.index(mj_joint)
        mujoco_to_train_map.append(idx)
    else:
        mujoco_to_train_map.append(-1)

print(f"映射表 (MuJoCo索引 -> 训练索引): {mujoco_to_train_map}")

print("\n" + "=" * 80)
print("获取正确的default_angles (MuJoCo顺序)")
print("=" * 80)

# 创建MuJoCo顺序的default_angles:
mujoco_default_angles = []
for joint_name in mujoco_actuator_order:
    if joint_name in training_joint_dict:
        mujoco_default_angles.append(training_joint_dict[joint_name])
    else:
        mujoco_default_angles.append(0.0)
        print(f"WARNING: {joint_name} not found in training dict")

print(f"\nMuJoCo顺序的default_angles:")
for name, val in zip(mujoco_actuator_order, mujoco_default_angles):
    print(f"  {name:30}: {val}")

# 创建target_joint_angles (MuJoCo顺序):
training_target_dict = {
    'left_hip_yaw_joint': 0.0, 'left_hip_roll_joint': 0.0, 'left_hip_pitch_joint': -0.1,
    'left_knee_joint': 0.3, 'left_ankle_pitch_joint': -0.2, 'left_ankle_roll_joint': 0.0,
    'left_wrist_roll_joint': 0.0,
    'right_hip_yaw_joint': 0.0, 'right_hip_roll_joint': 0.0, 'right_hip_pitch_joint': -0.1,
    'right_knee_joint': 0.3, 'right_ankle_pitch_joint': -0.2, 'right_ankle_roll_joint': 0.0,
    'right_wrist_roll_joint': 0.0,
    'waist_yaw_joint': 0.0,
    'left_shoulder_pitch_joint': 0.0, 'left_shoulder_roll_joint': 0.3,
    'left_shoulder_yaw_joint': 0.0, 'left_elbow_joint': 0.0,
    'right_shoulder_pitch_joint': 0.0, 'right_shoulder_roll_joint': -0.3,
    'right_shoulder_yaw_joint': 0.0, 'right_elbow_joint': 0.0,
}

mujoco_target_angles = []
for joint_name in mujoco_actuator_order:
    if joint_name in training_target_dict:
        mujoco_target_angles.append(training_target_dict[joint_name])
    else:
        mujoco_target_angles.append(0.0)

print(f"\nMuJoCo顺序的target_joint_angles (for action=0):")
for name, val in zip(mujoco_actuator_order, mujoco_target_angles):
    print(f"  {name:30}: {val}")
