#!/usr/bin/env python3
"""
分析23DOF策略到29DOF真实机器人的映射
"""

# =================== 29DOF 真实机器人电机顺序 ===================
motor_29dof = [
    (0,  'L_LEG_HIP_PITCH'),
    (1,  'L_LEG_HIP_ROLL'),
    (2,  'L_LEG_HIP_YAW'),
    (3,  'L_LEG_KNEE'),
    (4,  'L_LEG_ANKLE_PITCH'),
    (5,  'L_LEG_ANKLE_ROLL'),
    (6,  'R_LEG_HIP_PITCH'),
    (7,  'R_LEG_HIP_ROLL'),
    (8,  'R_LEG_HIP_YAW'),
    (9,  'R_LEG_KNEE'),
    (10, 'R_LEG_ANKLE_PITCH'),
    (11, 'R_LEG_ANKLE_ROLL'),
    (12, 'WAIST_YAW'),
    (13, 'WAIST_ROLL'),
    (14, 'WAIST_PITCH'),
    (15, 'L_SHOULDER_PITCH'),
    (16, 'L_SHOULDER_ROLL'),
    (17, 'L_SHOULDER_YAW'),
    (18, 'L_ELBOW'),
    (19, 'L_WRIST_ROLL'),
    (20, 'L_WRIST_PITCH'),  # 额外
    (21, 'L_WRIST_YAW'),    # 额外
    (22, 'R_SHOULDER_PITCH'),
    (23, 'R_SHOULDER_ROLL'),
    (24, 'R_SHOULDER_YAW'),
    (25, 'R_ELBOW'),
    (26, 'R_WRIST_ROLL'),
    (27, 'R_WRIST_PITCH'),  # 额外
    (28, 'R_WRIST_YAW'),    # 额外
]

# 构建名称到索引的映射
name_to_idx_29 = {name: idx for idx, name in motor_29dof}

# =================== 23DOF策略输出顺序 (训练顺序) ===================
# 训练顺序: left leg (6): yaw, roll, pitch, knee, ankle_pitch, ankle_roll
#          right leg (6): yaw, roll, pitch, knee, ankle_pitch, ankle_roll
#          waist (1): yaw
#          left arm (5): shoulder_pitch, shoulder_roll, shoulder_yaw, elbow, wrist_roll
#          right arm (5): shoulder_pitch, shoulder_roll, shoulder_yaw, elbow, wrist_roll

policy_23dof_names = [
    # 左腿 (0-5): yaw, roll, pitch, knee, ankle_pitch, ankle_roll
    'L_LEG_HIP_YAW',
    'L_LEG_HIP_ROLL',
    'L_LEG_HIP_PITCH',
    'L_LEG_KNEE',
    'L_LEG_ANKLE_PITCH',
    'L_LEG_ANKLE_ROLL',
    # 右腿 (6-11): yaw, roll, pitch, knee, ankle_pitch, ankle_roll
    'R_LEG_HIP_YAW',
    'R_LEG_HIP_ROLL',
    'R_LEG_HIP_PITCH',
    'R_LEG_KNEE',
    'R_LEG_ANKLE_PITCH',
    'R_LEG_ANKLE_ROLL',
    # 腰部 (12)
    'WAIST_YAW',
    # 左臂 (13-17)
    'L_SHOULDER_PITCH',
    'L_SHOULDER_ROLL',
    'L_SHOULDER_YAW',
    'L_ELBOW',
    'L_WRIST_ROLL',
    # 右臂 (18-22)
    'R_SHOULDER_PITCH',
    'R_SHOULDER_ROLL',
    'R_SHOULDER_YAW',
    'R_ELBOW',
    'R_WRIST_ROLL',
]

print("="*80)
print("23DOF策略到29DOF真实机器人的映射")
print("="*80)
print(f"{'策略索引':>8} {'策略关节名称':<25} {'真实电机索引':>15}")
print("-"*80)

policy_joint2motor_idx = []
for policy_idx, name in enumerate(policy_23dof_names):
    motor_idx = name_to_idx_29[name]
    policy_joint2motor_idx.append(motor_idx)
    print(f"{policy_idx:>8} {name:<25} {motor_idx:>15}")

print(f"\npolicy_joint2motor_idx = {policy_joint2motor_idx}")

# =================== 需要锁定的关节 ===================
print("\n" + "="*80)
print("需要锁定的额外关节 (不在策略中)")
print("="*80)

locked_joints = []
for idx, name in motor_29dof:
    if name not in policy_23dof_names:
        locked_joints.append((idx, name))

print(f"{'电机索引':>8} {'关节名称':<25}")
print("-"*80)
for idx, name in locked_joints:
    print(f"{idx:>8} {name:<25}")

print(f"\n总共有 {len(locked_joints)} 个关节需要锁定")

# =================== arm_waist_joint2motor_idx ===================
# 包含所有腰+臂的电机，包括策略使用的和需要锁定的
# 腰: 12,13,14
# 左臂:15-21
# 右臂:22-28
arm_waist_joint2motor_idx = [12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28]
print("\n" + "="*80)
print("arm_waist_joint2motor_idx (全部腰+臂电机)")
print("="*80)
print(arm_waist_joint2motor_idx)

# =================== default_angles ===================
print("\n" + "="*80)
print("策略需要的关节 default_angles (训练顺序的数值，但按策略映射后给电机)")
print("="*80)
print("注意: 这里的数值是关节角度，按policy_23dof_names的顺序，实际部署时会通过policy_joint2motor_idx映射到对应电机")
print("数值来自deploy_mujoco/configs/g1.yaml")

# 从g1_config_ground.py来的default_angles (训练顺序对应数值)
# 但注意: policy输出时，我们需要知道每个关节对应的默认角度值
# 我们需要构建policy_default_angles: 按policy_23dof_names的顺序，每个关节的默认角度

# 训练配置中的default_joint_angles数值映射
train_defaults = {
    'L_LEG_HIP_YAW': 0.0,
    'L_LEG_HIP_ROLL': 0.0,
    'L_LEG_HIP_PITCH': -0.1,
    'L_LEG_KNEE': 0.3,
    'L_LEG_ANKLE_PITCH': -0.2,
    'L_LEG_ANKLE_ROLL': 0.0,
    'R_LEG_HIP_YAW': 0.0,
    'R_LEG_HIP_ROLL': 0.0,
    'R_LEG_HIP_PITCH': -0.1,
    'R_LEG_KNEE': 0.3,
    'R_LEG_ANKLE_PITCH': -0.2,
    'R_LEG_ANKLE_ROLL': 0.0,
    'WAIST_YAW': 0.0,
    'L_SHOULDER_PITCH': 0.0,
    'L_SHOULDER_ROLL': 0.0,
    'L_SHOULDER_YAW': 0.0,
    'L_ELBOW': 0.8,
    'L_WRIST_ROLL': 0.0,
    'R_SHOULDER_PITCH': 0.0,
    'R_SHOULDER_ROLL': 0.0,
    'R_SHOULDER_YAW': 0.0,
    'R_ELBOW': 0.8,
    'R_WRIST_ROLL': 0.0,
}

# 额外关节的锁定位置
locked_defaults = {
    'WAIST_ROLL': 0.0,
    'WAIST_PITCH': 0.0,
    'L_WRIST_PITCH': 0.0,
    'L_WRIST_YAW': 0.0,
    'R_WRIST_PITCH': 0.0,
    'R_WRIST_YAW': 0.0,
}

print("\npolicy_default_angles (按policy顺序):")
policy_default_angles = [train_defaults[name] for name in policy_23dof_names]
for name, val in zip(policy_23dof_names, policy_default_angles):
    print(f"  {name:<25} {val}")
print(f"\npolicy_default_angles = {policy_default_angles}")

# =================== kps/kds ===================
print("\n" + "="*80)
print("PD Gains (kps/kds)")
print("="*80)

# 从deploy_mujoco/g1.yaml获取增益，按motor顺序分配
kps_template = {
    'hip': 250,
    'roll': 200,
    'yaw': 200,
    'knee': 200,
    'ankle_pitch': 40,
    'ankle_roll': 40,
    'waist': 200,
    'shoulder_pitch': 300,
    'shoulder_roll': 300,
    'shoulder_yaw': 200,
    'elbow': 200,
    'wrist': 200,
}
kds_template = {
    'hip': 6,
    'roll': 4,
    'yaw': 4,
    'knee': 6,
    'ankle_pitch': 4,
    'ankle_roll': 4,
    'waist': 8,
    'shoulder_pitch': 8,
    'shoulder_roll': 8,
    'shoulder_yaw': 6,
    'elbow': 6,
    'wrist': 6,
}

def get_gain(name, template):
    if 'HIP_PITCH' in name:
        return template['hip']
    elif 'HIP_ROLL' in name:
        return template['roll']
    elif 'HIP_YAW' in name:
        return template['yaw']
    elif 'KNEE' in name:
        return template['knee']
    elif 'ANKLE_PITCH' in name:
        return template['ankle_pitch']
    elif 'ANKLE_ROLL' in name:
        return template['ankle_roll']
    elif 'WAIST_YAW' in name or 'WAIST_ROLL' in name or 'WAIST_PITCH' in name:
        return template['waist']
    elif 'SHOULDER_PITCH' in name:
        return template['shoulder_pitch']
    elif 'SHOULDER_ROLL' in name:
        return template['shoulder_roll']
    elif 'SHOULDER_YAW' in name:
        return template['shoulder_yaw']
    elif 'ELBOW' in name:
        return template['elbow']
    elif 'WRIST' in name:
        return template['wrist']
    else:
        return 100

print("\npolicy_kps/policy_kds (按policy顺序):")
policy_kps = [get_gain(name, kps_template) for name in policy_23dof_names]
policy_kds = [get_gain(name, kds_template) for name in policy_23dof_names]
for name, kp, kd in zip(policy_23dof_names, policy_kps, policy_kds):
    print(f"  {name:<25} kp={kp:>3}, kd={kd:>2}")
print(f"\npolicy_kps = {policy_kps}")
print(f"policy_kds = {policy_kds}")

# =================== leg/arm_waist 分开 ===================
print("\n" + "="*80)
print("按g1_walk_12dof.yaml格式分开: leg, arm_waist")
print("="*80)

# leg 是前12个电机 (0-11)
leg_joint2motor_idx = [0,1,2,3,4,5,6,7,8,9,10,11]
print(f"\nleg_joint2motor_idx = {leg_joint2motor_idx}")

# leg的default_angles (0-11电机顺序的数值)
# 电机0: L_LEG_HIP_PITCH -> -0.1
# 电机1: L_LEG_HIP_ROLL -> 0.0
# 电机2: L_LEG_HIP_YAW -> 0.0
# 电机3: L_LEG_KNEE -> 0.3
# 电机4: L_LEG_ANKLE_PITCH -> -0.2
# 电机5: L_LEG_ANKLE_ROLL -> 0.0
# 电机6: R_LEG_HIP_PITCH -> -0.1
# 电机7: R_LEG_HIP_ROLL -> 0.0
# 电机8: R_LEG_HIP_YAW -> 0.0
# 电机9: R_LEG_KNEE -> 0.3
# 电机10: R_LEG_ANKLE_PITCH -> -0.2
# 电机11: R_LEG_ANKLE_ROLL -> 0.0
leg_default_angles = [-0.1, 0.0, 0.0, 0.3, -0.2, 0.0, -0.1, 0.0, 0.0, 0.3, -0.2, 0.0]
leg_kps = [250, 200, 200, 200, 40, 40, 250, 200, 200, 200, 40, 40]
leg_kds = [6, 4, 4, 6, 4, 4, 6, 4, 4, 6, 4, 4]
print(f"\ndefault_angles (leg, 0-11电机顺序):")
for idx, name in motor_29dof[:12]:
    print(f"  motor[{idx}]={name:<25} {leg_default_angles[idx]}")
print(f"\nleg default_angles = {leg_default_angles}")
print(f"leg kps = {leg_kps}")
print(f"leg kds = {leg_kds}")

# arm_waist 是 12-28 (17个电机)
print(f"\narm_waist_joint2motor_idx = {arm_waist_joint2motor_idx}")
print("\narm_waist_target (包含策略使用的和需要锁定的):")
arm_waist_target = []
for idx in arm_waist_joint2motor_idx:
    name = motor_29dof[idx][1]
    if name in train_defaults:
        val = train_defaults[name]
    else:
        val = locked_defaults[name]
    arm_waist_target.append(val)
    print(f"  motor[{idx}]={name:<25} {val}")
print(f"\narm_waist_target = {arm_waist_target}")

# arm_waist_kps, arm_waist_kds
arm_waist_kps = [get_gain(motor_29dof[idx][1], kps_template) for idx in arm_waist_joint2motor_idx]
arm_waist_kds = [get_gain(motor_29dof[idx][1], kds_template) for idx in arm_waist_joint2motor_idx]
print(f"\narm_waist_kps = {arm_waist_kps}")
print(f"arm_waist_kds = {arm_waist_kds}")
