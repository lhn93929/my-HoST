#!/usr/bin/env python3
"""
分析23DOF(MuJoCo/训练)与29DOF(真实机器人)的关节对应关系
"""

# MuJoCo/训练的23DOF顺序
mujoco_23_joints = [
    # 左腿 0-5
    "left_hip_pitch",
    "left_hip_roll",
    "left_hip_yaw",
    "left_knee",
    "left_ankle_pitch",
    "left_ankle_roll",
    # 右腿 6-11
    "right_hip_pitch",
    "right_hip_roll",
    "right_hip_yaw",
    "right_knee",
    "right_ankle_pitch",
    "right_ankle_roll",
    # 腰部 12
    "waist_yaw",
    # 左臂 13-17
    "left_shoulder_pitch",
    "left_shoulder_roll",
    "left_shoulder_yaw",
    "left_elbow",
    "left_wrist_roll",
    # 右臂 18-22
    "right_shoulder_pitch",
    "right_shoulder_roll",
    "right_shoulder_yaw",
    "right_elbow",
    "right_wrist_roll",
]

# 根据原始配置推断的29DOF真实机器人关节顺序
# leg_joint2motor_idx: [0,1,2,3,4,5,6,7,8,9,10,11] - 12个腿关节
# arm_waist_joint2motor_idx: [12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28] - 17个腰臂关节

# 根据Unitree G1机器人的常见关节配置，29DOF的分布可能是：
# 腿:12, 腰:3, 臂:7*2=14 → 总共12+3+14=29

real_29_joints_inferred = [
    # 左腿 0-5
    "left_hip_pitch",
    "left_hip_roll",
    "left_hip_yaw",
    "left_knee",
    "left_ankle_pitch",
    "left_ankle_roll",
    # 右腿 6-11
    "right_hip_pitch",
    "right_hip_roll",
    "right_hip_yaw",
    "right_knee",
    "right_ankle_pitch",
    "right_ankle_roll",
    # 腰部 12-14 (3DOF)
    "waist_yaw",
    "waist_roll",
    "waist_pitch",
    # 左臂 15-21 (7DOF)
    "left_shoulder_pitch",
    "left_shoulder_roll",
    "left_shoulder_yaw",
    "left_elbow",
    "left_wrist_pitch",  # 额外的
    "left_wrist_roll",
    "left_wrist_yaw",    # 额外的
    # 右臂 22-28 (7DOF)
    "right_shoulder_pitch",
    "right_shoulder_roll",
    "right_shoulder_yaw",
    "right_elbow",
    "right_wrist_pitch",  # 额外的
    "right_wrist_roll",
    "right_wrist_yaw",    # 额外的
]

# 23DOF到29DOF的映射
# 对于训练中的23DOF，我们需要忽略真实机器人中的额外关节
# 23DOF中没有：waist_roll, waist_pitch, *_wrist_pitch, *_wrist_yaw

joint_map_23_to_29 = {
    0: 0,   # left_hip_pitch
    1: 1,   # left_hip_roll
    2: 2,   # left_hip_yaw
    3: 3,   # left_knee
    4: 4,   # left_ankle_pitch
    5: 5,   # left_ankle_roll
    6: 6,   # right_hip_pitch
    7: 7,   # right_hip_roll
    8: 8,   # right_hip_yaw
    9: 9,   # right_knee
    10:10,  # right_ankle_pitch
    11:11,  # right_ankle_roll
    12:12,  # waist_yaw
    13:15,  # left_shoulder_pitch (跳过13,14的额外腰关节)
    14:16,  # left_shoulder_roll
    15:17,  # left_shoulder_yaw
    16:18,  # left_elbow
    17:20,  # left_wrist_roll (跳过19的wrist_pitch)
    18:22,  # right_shoulder_pitch (跳过21的右wrist_pitch?)
    19:23,  # right_shoulder_roll
    20:24,  # right_shoulder_yaw
    21:25,  # right_elbow
    22:27,  # right_wrist_roll (跳过26的wrist_pitch)
}

# 另一种可能：腰部只有1DOF(yaw)，手臂是5DOF，没有额外关节
# 这样的话，23DOF直接对应前23个电机索引！

joint_map_23_to_29_simple = {
    i: i for i in range(23)
}

def main():
    print("="*80)
    print("23DOF (MuJoCo/训练) 与 29DOF (真实机器人) 关节对应分析")
    print("="*80)

    print("\n方案一：前23个电机直接对应 (推荐用于部署验证)")
    print("-"*80)
    print(f"{'23DOF索引':>10} {'关节名称':<30} {'29DOF电机索引':>15}")
    print("-"*80)
    for i in range(23):
        print(f"{i:>10} {mujoco_23_joints[i]:<30} {i:>15}")

    print("\n方案二：考虑真实机器人可能有额外腰/腕关节的情况")
    print("-"*80)
    print("如果真实机器人有：")
    print("  - 腰部3DOF (yaw, roll, pitch)")
    print("  - 手臂7DOF (增加 wrist_pitch, wrist_yaw)")
    print("则需要使用映射表：")

    print(f"\n{'23DOF索引':>10} {'关节名称':<30} {'29DOF电机索引':>15}")
    print("-"*80)
    for i in range(23):
        print(f"{i:>10} {mujoco_23_joints[i]:<30} {joint_map_23_to_29[i]:>15}")

    print("\n" + "="*80)
    print("deploy_real/configs/g1.yaml 配置建议")
    print("="*80)

    print("\n方案一配置（简单）：")
    print("policy_joint2motor_idx: " + str(list(range(23))))
    print("\n这种情况下：")
    print("- 假设真实机器人的前23个电机顺序与MuJoCo一致")
    print("- 对于29DOF机器人，索引23-28的关节不被策略控制，可以设置为固定位置")
    print("- arm_waist_target需要覆盖索引12-28的默认位置")

    print("\n方案二配置（如果真实机器人确实有29DOF且顺序不同）：")
    print("policy_joint2motor_idx: " + str([joint_map_23_to_29[i] for i in range(23)]))

    print("\n" + "="*80)
    print("如何确定正确的映射？")
    print("="*80)
    print("\n1. 检查真实机器人的URDF或文档，确认各关节对应的电机ID")
    print("2. 运行 deploy_real/check_gravity.py 查看imu数据和关节数据")
    print("3. 尝试方案一，观察机器人运动是否符合预期")
    print("4. 如果某个关节运动不对，调整对应索引")

    print("\n当前 deploy_real/configs/g1.yaml 使用的是方案一（0-22顺序）")

    print("\n29DOF完整关节推断表：")
    print("-"*80)
    print(f"{'29DOF索引':>10} {'推断关节名称':<30} {'策略使用':>10}")
    print("-"*80)
    for i in range(29):
        used = "✓" if i in [joint_map_23_to_29_simple[j] for j in range(23)] else "-"
        name = real_29_joints_inferred[i] if i < len(real_29_joints_inferred) else f"joint_{i}"
        print(f"{i:>10} {name:<30} {used:>10}")


if __name__ == "__main__":
    main()
