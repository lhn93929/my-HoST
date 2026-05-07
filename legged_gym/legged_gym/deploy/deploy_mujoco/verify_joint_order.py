#!/usr/bin/env python3
"""
验证关节顺序并生成映射关系
"""

import mujoco
import numpy as np
import yaml
import os

from legged_gym import LEGGED_GYM_ROOT_DIR


def get_mujoco_joint_names(model):
    """获取MuJoCo中的关节名称顺序"""
    joint_names = []
    for i in range(model.nu):
        name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_ACTUATOR, i)
        if name is None:
            name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, i)
        joint_names.append(name)
    return joint_names


def main():
    # 加载MuJoCo模型
    xml_path = f"{LEGGED_GYM_ROOT_DIR}/resources/robots/g1/g1_23dof.xml"
    model = mujoco.MjModel.from_xml_path(xml_path)

    # 获取MuJoCo中的关节顺序
    mujoco_joint_names = get_mujoco_joint_names(model)

    print("=" * 80)
    print("MuJoCo关节顺序 (actuator顺序)")
    print("=" * 80)
    for i, name in enumerate(mujoco_joint_names):
        print(f"{i:2d}: {name}")
    print(f"\nTotal: {len(mujoco_joint_names)} joints")

    # 加载deploy_mujoco的配置
    deploy_mujoco_config_path = f"{LEGGED_GYM_ROOT_DIR}/legged_gym/deploy/deploy_mujoco/configs/g1.yaml"
    with open(deploy_mujoco_config_path, 'r') as f:
        deploy_mujoco_config = yaml.load(f, Loader=yaml.FullLoader)

    print("\n" + "=" * 80)
    print("deploy_mujoco g1.yaml配置检查")
    print("=" * 80)

    # deploy_mujoco config中的默认角度顺序
    print(f"\ndefault_angles数量: {len(deploy_mujoco_config['default_angles'])}")
    print(f"kps数量: {len(deploy_mujoco_config['kps'])}")
    print(f"num_actions: {deploy_mujoco_config['num_actions']}")

    # 加载deploy_real的配置
    deploy_real_config_path = f"{LEGGED_GYM_ROOT_DIR}/legged_gym/deploy/deploy_real/configs/g1.yaml"
    with open(deploy_real_config_path, 'r') as f:
        deploy_real_config = yaml.load(f, Loader=yaml.FullLoader)

    print("\n" + "=" * 80)
    print("deploy_real g1.yaml配置检查")
    print("=" * 80)

    print(f"\npolicy_joint2motor_idx: {deploy_real_config['policy_joint2motor_idx']}")
    print(f"数量: {len(deploy_real_config['policy_joint2motor_idx'])}")
    print(f"\npolicy_default_angles数量: {len(deploy_real_config['policy_default_angles'])}")

    # 生成映射表
    print("\n" + "=" * 80)
    print("完整的23DOF关节顺序映射表")
    print("=" * 80)
    print()

    joint_order_description = [
        ("左腿", 0, 6, [
            "left_hip_pitch_joint", "left_hip_roll_joint", "left_hip_yaw_joint",
            "left_knee_joint", "left_ankle_pitch_joint", "left_ankle_roll_joint"
        ]),
        ("右腿", 6, 12, [
            "right_hip_pitch_joint", "right_hip_roll_joint", "right_hip_yaw_joint",
            "right_knee_joint", "right_ankle_pitch_joint", "right_ankle_roll_joint"
        ]),
        ("腰部", 12, 13, [
            "waist_yaw_joint"
        ]),
        ("左臂", 13, 18, [
            "left_shoulder_pitch_joint", "left_shoulder_roll_joint", "left_shoulder_yaw_joint",
            "left_elbow_joint", "left_wrist_roll_joint"
        ]),
        ("右臂", 18, 23, [
            "right_shoulder_pitch_joint", "right_shoulder_roll_joint", "right_shoulder_yaw_joint",
            "right_elbow_joint", "right_wrist_roll_joint"
        ]),
    ]

    print("索引    部位    关节名称")
    print("-" * 80)

    all_joints = []
    for part_name, start, end, joints in joint_order_description:
        for i, joint in enumerate(joints):
            idx = start + i
            all_joints.append(joint)
            print(f"{idx:2d}     {part_name:8s}  {joint}")

    # 验证MuJoCo顺序是否匹配
    print("\n" + "=" * 80)
    print("MuJoCo顺序验证")
    print("=" * 80)

    matches = []
    for i in range(len(mujoco_joint_names)):
        match = mujoco_joint_names[i] == all_joints[i]
        matches.append(match)
        status = "✓" if match else "✗"
        print(f"{i:2d}: {status}  MuJoCo: {mujoco_joint_names[i]:30s}  期望: {all_joints[i]}")

    print(f"\n匹配结果: {sum(matches)}/{len(matches)}")
    if all(matches):
        print("✓ MuJoCo关节顺序与期望顺序一致！")
    else:
        print("✗ MuJoCo关节顺序不匹配！")

    # 验证配置文件中的顺序
    print("\n" + "=" * 80)
    print("deploy_mujoco配置验证")
    print("=" * 80)

    default_angles = deploy_mujoco_config['default_angles']
    if len(default_angles) == len(all_joints):
        print("✓ default_angles数量与期望一致")
    else:
        print("✗ default_angles数量不匹配")

    print("\n验证deploy_real配置...")
    policy_joint_idx = deploy_real_config['policy_joint2motor_idx']
    if len(policy_joint_idx) == 23 and policy_joint_idx == list(range(23)):
        print("✓ policy_joint2motor_idx顺序正确（0-22依次排列）")
    else:
        print("✗ policy_joint2motor_idx可能需要调整")

    # 输出可以直接复制到配置中的格式
    print("\n" + "=" * 80)
    print("配置参考")
    print("=" * 80)
    print("\npolicy_joint2motor_idx: " + str(list(range(23))))

    print("\n如果需要按真实机器人的电机索引调整，请提供实际的motor索引映射。")


if __name__ == "__main__":
    main()
