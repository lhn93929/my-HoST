#!/usr/bin/env python3
"""
验证关节顺序映射是否正确
"""

# 训练顺序的关节名称 (train order)
train_joint_names = [
    'left_hip_yaw_joint', 'left_hip_roll_joint', 'left_hip_pitch_joint',
    'left_knee_joint', 'left_ankle_pitch_joint', 'left_ankle_roll_joint',
    'right_hip_yaw_joint', 'right_hip_roll_joint', 'right_hip_pitch_joint',
    'right_knee_joint', 'right_ankle_pitch_joint', 'right_ankle_roll_joint',
    'waist_yaw_joint',
    'left_shoulder_pitch_joint', 'left_shoulder_roll_joint', 'left_shoulder_yaw_joint',
    'left_elbow_joint', 'left_wrist_roll_joint',
    'right_shoulder_pitch_joint', 'right_shoulder_roll_joint', 'right_shoulder_yaw_joint',
    'right_elbow_joint', 'right_wrist_roll_joint',
]

# MuJoCo顺序的关节名称 (mujoco order)
mujoco_joint_names = [
    'left_hip_pitch_joint', 'left_hip_roll_joint', 'left_hip_yaw_joint',
    'left_knee_joint', 'left_ankle_pitch_joint', 'left_ankle_roll_joint',
    'right_hip_pitch_joint', 'right_hip_roll_joint', 'right_hip_yaw_joint',
    'right_knee_joint', 'right_ankle_pitch_joint', 'right_ankle_roll_joint',
    'waist_yaw_joint',
    'left_shoulder_pitch_joint', 'left_shoulder_roll_joint', 'left_shoulder_yaw_joint',
    'left_elbow_joint', 'left_wrist_roll_joint',
    'right_shoulder_pitch_joint', 'right_shoulder_roll_joint', 'right_shoulder_yaw_joint',
    'right_elbow_joint', 'right_wrist_roll_joint',
]

# 映射表
train_to_mujoco_map = [2, 1, 0, 3, 4, 5, 8, 7, 6, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
mujoco_to_train_map = [2, 1, 0, 3, 4, 5, 8, 7, 6, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]

print("="*80)
print("验证1: 训练 -> MuJoCo 映射")
print("="*80)
print(f"{'索引':<8} {'训练关节名称':<35} {'MuJoCo索引':<12} {'MuJoCo关节名称':<35} {'匹配':<6}")
print("-"*80)

all_correct = True
for train_idx in range(23):
    mujoco_idx = train_to_mujoco_map[train_idx]
    train_name = train_joint_names[train_idx]
    mujoco_name = mujoco_joint_names[mujoco_idx]
    match = "✓" if train_name == mujoco_name else "✗"
    if match == "✗":
        all_correct = False
    print(f"{train_idx:<8} {train_name:<35} {mujoco_idx:<12} {mujoco_name:<35} {match:<6}")

print(f"\n训练->MuJoCo映射: {'✓ 全部正确' if all_correct else '✗ 有错误'}")

print("\n" + "="*80)
print("验证2: MuJoCo -> 训练 映射")
print("="*80)
print(f"{'索引':<8} {'MuJoCo关节名称':<35} {'训练索引':<12} {'训练关节名称':<35} {'匹配':<6}")
print("-"*80)

all_correct2 = True
for mujoco_idx in range(23):
    train_idx = mujoco_to_train_map[mujoco_idx]
    mujoco_name = mujoco_joint_names[mujoco_idx]
    train_name = train_joint_names[train_idx]
    match = "✓" if mujoco_name == train_name else "✗"
    if match == "✗":
        all_correct2 = False
    print(f"{mujoco_idx:<8} {mujoco_name:<35} {train_idx:<12} {train_name:<35} {match:<6}")

print(f"\nMuJoCo->训练映射: {'✓ 全部正确' if all_correct2 else '✗ 有错误'}")

print("\n" + "="*80)
print("总结")
print("="*80)
if all_correct and all_correct2:
    print("✓ 所有映射都正确!")
else:
    print("✗ 映射有错误!")
