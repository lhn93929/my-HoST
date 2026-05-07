#!/usr/bin/env python3
"""
验证训练配置和MuJoCo配置的关节顺序差异
"""

# ==========================================
# 1. 训练时的关节顺序 (从g1_config_ground.py)
# ==========================================
train_left_leg = [
    'left_hip_yaw_joint',
    'left_hip_roll_joint',
    'left_hip_pitch_joint',
    'left_knee_joint',
    'left_ankle_pitch_joint',
    'left_ankle_roll_joint'
]
train_right_leg = [
    'right_hip_yaw_joint',
    'right_hip_roll_joint',
    'right_hip_pitch_joint',
    'right_knee_joint',
    'right_ankle_pitch_joint',
    'right_ankle_roll_joint'
]
train_waist = ['waist_yaw_joint']
train_left_arm = [
    'left_shoulder_pitch_joint',
    'left_shoulder_roll_joint',
    'left_shoulder_yaw_joint',
    'left_elbow_joint',
    'left_wrist_roll_joint'
]
train_right_arm = [
    'right_shoulder_pitch_joint',
    'right_shoulder_roll_joint',
    'right_shoulder_yaw_joint',
    'right_elbow_joint',
    'right_wrist_roll_joint'
]

train_order = train_left_leg + train_right_leg + train_waist + train_left_arm + train_right_arm

# ==========================================
# 2. MuJoCo的关节顺序 (从XML actuator顺序)
# ==========================================
mujoco_order = [
    'left_hip_pitch_joint',   # 0
    'left_hip_roll_joint',    # 1
    'left_hip_yaw_joint',     # 2
    'left_knee_joint',        # 3
    'left_ankle_pitch_joint', # 4
    'left_ankle_roll_joint',  # 5
    'right_hip_pitch_joint',  # 6
    'right_hip_roll_joint',   # 7
    'right_hip_yaw_joint',    # 8
    'right_knee_joint',       # 9
    'right_ankle_pitch_joint',# 10
    'right_ankle_roll_joint', # 11
    'waist_yaw_joint',        # 12
    'left_shoulder_pitch_joint',  # 13
    'left_shoulder_roll_joint',   # 14
    'left_shoulder_yaw_joint',    # 15
    'left_elbow_joint',           # 16
    'left_wrist_roll_joint',      # 17
    'right_shoulder_pitch_joint', # 18
    'right_shoulder_roll_joint',  # 19
    'right_shoulder_yaw_joint',   # 20
    'right_elbow_joint',          # 21
    'right_wrist_roll_joint',     # 22
]

# ==========================================
# 3. 对比和映射
# ==========================================
print("="*80)
print("关节顺序对比")
print("="*80)
print(f"{'索引':<6} {'训练顺序':<30} {'MuJoCo顺序':<30} {'匹配':<6}")
print("-"*80)

mismatch = []
for i in range(23):
    train_name = train_order[i]
    mujoco_name = mujoco_order[i]
    match = "✓" if train_name == mujoco_name else "✗"
    if match == "✗":
        mismatch.append((i, train_name, mujoco_name))
    print(f"{i:<6} {train_name:<30} {mujoco_name:<30} {match:<6}")

print(f"\n不匹配数量: {len(mismatch)}")

# ==========================================
# 4. 创建映射表
# ==========================================
print("\n" + "="*80)
print("映射表: 训练索引 -> MuJoCo索引")
print("="*80)

train_to_mujoco = []
for train_name in train_order:
    mj_idx = mujoco_order.index(train_name)
    train_to_mujoco.append(mj_idx)
    print(f"train[{len(train_to_mujoco)-1}] = {train_name:<30} -> mujoco[{mj_idx}]")

print(f"\ntrain_to_mujoco_map = {train_to_mujoco}")

print("\n" + "="*80)
print("映射表: MuJoCo索引 -> 训练索引")
print("="*80)

mujoco_to_train = []
for mujoco_name in mujoco_order:
    train_idx = train_order.index(mujoco_name)
    mujoco_to_train.append(train_idx)
    print(f"mujoco[{len(mujoco_to_train)-1}] = {mujoco_name:<30} -> train[{train_idx}]")

print(f"\nmujoco_to_train_map = {mujoco_to_train}")

# ==========================================
# 5. 验证default_angles
# ==========================================
print("\n" + "="*80)
print("default_angles验证")
print("="*80)

# 训练配置中的default_joint_angles字典
train_default_dict = {
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
    'left_shoulder_pitch_joint': 0.0,
    'left_shoulder_roll_joint': 0.0,
    'left_shoulder_yaw_joint': 0.0,
    'left_elbow_joint': 0.8,
    'right_shoulder_pitch_joint': 0.0,
    'right_shoulder_roll_joint': 0.0,
    'right_shoulder_yaw_joint': 0.0,
    'right_elbow_joint': 0.8,
}

# 当前g1.yaml中的default_angles (MuJoCo顺序)
current_mujoco_default = [
    -0.1, 0.0, 0.0, 0.3, -0.2, 0.0,  # left leg (pitch, roll, yaw, ...)
    -0.1, 0.0, 0.0, 0.3, -0.2, 0.0,  # right leg
    0.0,  # waist
    0.0, 0.0, 0.0, 0.8, 0.0,  # left arm
    0.0, 0.0, 0.0, 0.8, 0.0   # right arm
]

# 正确的MuJoCo顺序default_angles
correct_mujoco_default = []
for joint_name in mujoco_order:
    correct_mujoco_default.append(train_default_dict[joint_name])

print(f"\n当前g1.yaml中的default_angles (可能有问题):")
for i, (name, val) in enumerate(zip(mujoco_order, current_mujoco_default)):
    print(f"  {i}: {name:<30} = {val}")

print(f"\n正确的MuJoCo顺序default_angles:")
for i, (name, val) in enumerate(zip(mujoco_order, correct_mujoco_default)):
    print(f"  {i}: {name:<30} = {val}")

print(f"\n正确的default_angles列表 (复制到g1.yaml):")
print(f"  {correct_mujoco_default}")

# ==========================================
# 6. 检查kps和kds
# ==========================================
print("\n" + "="*80)
print("PD gains验证")
print("="*80)

# 训练配置中的stiffness和damping
# 需要根据关节名称分配
stiffness_dict = {
    'hip': 150, 'knee': 200, 'ankle': 40,
    'shoulder': 100, 'elbow': 100, 'waist': 100, 'wrist': 100
}
damping_dict = {
    'hip': 4, 'knee': 6, 'ankle': 2,
    'shoulder': 4, 'elbow': 4, 'waist': 4, 'wrist': 4
}

def get_gain(joint_name, gain_dict):
    if 'hip' in joint_name:
        return gain_dict['hip']
    elif 'knee' in joint_name:
        return gain_dict['knee']
    elif 'ankle' in joint_name:
        return gain_dict['ankle']
    elif 'shoulder' in joint_name:
        return gain_dict['shoulder']
    elif 'elbow' in joint_name:
        return gain_dict['elbow']
    elif 'waist' in joint_name:
        return gain_dict['waist']
    elif 'wrist' in joint_name:
        return gain_dict['wrist']
    else:
        return 100.0

# 生成MuJoCo顺序的kps和kds
mujoco_kps = [get_gain(name, stiffness_dict) for name in mujoco_order]
mujoco_kds = [get_gain(name, damping_dict) for name in mujoco_order]

print(f"\n正确的kps (MuJoCo顺序):")
print(f"  {mujoco_kps}")
print(f"\n正确的kds (MuJoCo顺序):")
print(f"  {mujoco_kds}")

# ==========================================
# 7. 总结需要修改的内容
# ==========================================
print("\n" + "="*80)
print("总结: 需要修改的内容")
print("="*80)
print("""
1. g1.yaml中的default_angles需要重新排列为MuJoCo顺序
2. deploy_mujoco.py中需要添加关节映射逻辑:
   - 从MuJoCo读取dof_pos后，需要转换为训练顺序用于观测
   - 从策略输出action后，需要转换为MuJoCo顺序用于控制
""")
