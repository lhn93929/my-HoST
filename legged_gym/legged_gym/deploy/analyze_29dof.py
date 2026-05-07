#!/usr/bin/env python3
"""
分析29DOF真实机器人的关节结构和23DOF策略对应关系
"""

# 原始deploy_real配置的结构
# leg_joint2motor_idx: [0-11] (12DOF)
# arm_waist_joint2motor_idx: [12-28] (17DOF)
# 17 = 3 (腰) + 7 (左臂) + 7 (右臂)

print("="*80)
print("29DOF 真实机器人关节结构分析")
print("="*80)

print("\n原始配置的电机索引分组:")
print("-"*80)
print("腿部 (0-11):", list(range(12)))
print("腰臂 (12-28):", list(range(12,29)))

print("\n29DOF 详细关节推断 (Unitree G1):")
print("-"*80)

# 更准确的29DOF分配
joint_29_dof = [
    # 左腿 0-5
    ("0-11", "腿", 0, "left_hip_pitch"),
    ("0-11", "腿", 1, "left_hip_roll"),
    ("0-11", "腿", 2, "left_hip_yaw"),
    ("0-11", "腿", 3, "left_knee"),
    ("0-11", "腿", 4, "left_ankle_pitch"),
    ("0-11", "腿", 5, "left_ankle_roll"),
    # 右腿 6-11
    ("0-11", "腿", 6, "right_hip_pitch"),
    ("0-11", "腿", 7, "right_hip_roll"),
    ("0-11", "腿", 8, "right_hip_yaw"),
    ("0-11", "腿", 9, "right_knee"),
    ("0-11", "腿",10, "right_ankle_pitch"),
    ("0-11", "腿",11, "right_ankle_roll"),
    # 腰部 12-14 (3DOF)
    ("12-28", "腰",12, "waist_yaw"),
    ("12-28", "腰",13, "waist_roll"),
    ("12-28", "腰",14, "waist_pitch"),
    # 左臂 15-21 (7DOF)
    ("12-28", "左臂",15, "left_shoulder_pitch"),
    ("12-28", "左臂",16, "left_shoulder_roll"),
    ("12-28", "左臂",17, "left_shoulder_yaw"),
    ("12-28", "左臂",18, "left_elbow"),
    ("12-28", "左臂",19, "left_wrist_pitch"),
    ("12-28", "左臂",20, "left_wrist_roll"),
    ("12-28", "左臂",21, "left_wrist_yaw"),
    # 右臂 22-28 (7DOF)
    ("12-28", "右臂",22, "right_shoulder_pitch"),
    ("12-28", "右臂",23, "right_shoulder_roll"),
    ("12-28", "右臂",24, "right_shoulder_yaw"),
    ("12-28", "右臂",25, "right_elbow"),
    ("12-28", "右臂",26, "right_wrist_pitch"),
    ("12-28", "右臂",27, "right_wrist_roll"),
    ("12-28", "右臂",28, "right_wrist_yaw"),
]

print(f"{'分组':<10} {'部位':<6} {'索引':>6} {'关节名称':<25}")
print("-"*80)
for group, part, idx, name in joint_29_dof:
    print(f"{group:<10} {part:<6} {idx:>6} {name:<25}")

print("\n" + "="*80)
print("23DOF (MuJoCo/训练) 与 29DOF (真实) 对应关系")
print("="*80)

# MuJoCo/训练的23DOF关节列表
mujoco_23_joints = [
    "left_hip_pitch", "left_hip_roll", "left_hip_yaw",
    "left_knee", "left_ankle_pitch", "left_ankle_roll",
    "right_hip_pitch", "right_hip_roll", "right_hip_yaw",
    "right_knee", "right_ankle_pitch", "right_ankle_roll",
    "waist_yaw",
    "left_shoulder_pitch", "left_shoulder_roll", "left_shoulder_yaw",
    "left_elbow", "left_wrist_roll",
    "right_shoulder_pitch", "right_shoulder_roll", "right_shoulder_yaw",
    "right_elbow", "right_wrist_roll",
]

# 29DOF索引到名称的映射
idx_to_name_29 = {idx: name for _, _, idx, name in joint_29_dof}
name_to_idx_29 = {name: idx for _, _, idx, name in joint_29_dof}

print(f"\n{'23DOF索引':>10} {'关节名称':<25} {'29DOF索引':>10} {'状态':<10}")
print("-"*80)

# 构建映射
policy_joint2motor_idx = []
for i_23, name_23 in enumerate(mujoco_23_joints):
    if name_23 in name_to_idx_29:
        idx_29 = name_to_idx_29[name_23]
        status = "✓"
        policy_joint2motor_idx.append(idx_29)
    else:
        status = "✗ 未找到"
        idx_29 = -1
    print(f"{i_23:>10} {name_23:<25} {idx_29:>10} {status:<10}")

print(f"\n需要固定的关节 (在29DOF中但不在23DOF策略中):")
print("-"*80)
joints_to_fix = []
for _, _, idx_29, name_29 in joint_29_dof:
    if name_29 not in mujoco_23_joints:
        joints_to_fix.append((idx_29, name_29))
        print(f"{idx_29:>6} {name_29}")

print("\n" + "="*80)
print("推荐的 deploy_real/configs/g1.yaml 配置")
print("="*80)

print(f"\npolicy_joint2motor_idx: {policy_joint2motor_idx}")

print(f"\n# 对应关系:")
for i_23, (idx_29, name) in enumerate(zip(policy_joint2motor_idx, mujoco_23_joints)):
    print(f"#   23DOF[{i_23}] = {name} = 29DOF[{idx_29}]")

print(f"\n# 需要固定的关节 (arm_waist_target要包含这些):")
arm_waist_idx = list(range(12,29))
print(f"# arm_waist_joint2motor_idx: {arm_waist_idx}")

print("\n说明:")
print("- 23DOF策略不控制: waist_roll, waist_pitch, left_wrist_pitch, left_wrist_yaw")
print("                        right_wrist_pitch, right_wrist_yaw")
print("- 这些关节需要在 arm_waist_target 中设置固定位置")
