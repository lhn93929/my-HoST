#!/usr/bin/env python3
"""
测试 config.py 是否能正常加载 g1.yaml
"""

import sys
import os

# 添加项目路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import Config

print("="*60)
print("测试 Config 加载")
print("="*60)

try:
    config_path = f"{PROJECT_ROOT}/legged_gym/deploy/deploy_real/configs/g1.yaml"
    # 如果路径不对，尝试直接从当前目录找
    if not os.path.exists(config_path):
        config_path = "configs/g1.yaml"
    print(f"加载配置文件: {config_path}")
    config = Config(config_path)
    print("✓ 配置加载成功!\n")

    print("配置摘要:")
    print(f"  control_dt: {config.control_dt}")
    print(f"  msg_type: {config.msg_type}")
    print(f"  imu_type: {config.imu_type}")
    print(f"  num_actions: {config.num_actions}")
    print(f"  num_obs: {config.num_obs}")
    print(f"  observation_mode: {config.observation_mode}")
    print(f"  action_target_mode: {config.action_target_mode}")
    print(f"  action_scale: {config.action_scale}")
    print()

    print("关节映射:")
    print(f"  policy_joint2motor_idx (len={len(config.policy_joint2motor_idx)}): {config.policy_joint2motor_idx}")
    print(f"  leg_joint2motor_idx (len={len(config.leg_joint2motor_idx)}): {config.leg_joint2motor_idx}")
    print(f"  arm_waist_joint2motor_idx (len={len(config.arm_waist_joint2motor_idx)}): {config.arm_waist_joint2motor_idx}")
    print()

    print("PD 增益:")
    print(f"  kps (len={len(config.kps)}): {config.kps[:6]}...")
    print(f"  kds (len={len(config.kds)}): {config.kds[:6]}...")
    print(f"  policy_kps (len={len(config.policy_kps)}): {config.policy_kps[:6]}...")
    print(f"  policy_kds (len={len(config.policy_kds)}): {config.policy_kds[:6]}...")
    print(f"  arm_waist_kps (len={len(config.arm_waist_kps)}): {config.arm_waist_kps}")
    print(f"  arm_waist_kds (len={len(config.arm_waist_kds)}): {config.arm_waist_kds}")
    print()

    print("默认角度:")
    print(f"  default_angles (len={len(config.default_angles)}): {config.default_angles[:6]}...")
    print(f"  policy_default_angles (len={len(config.policy_default_angles)}): {config.policy_default_angles[:6]}...")
    print(f"  arm_waist_target (len={len(config.arm_waist_target)}): {config.arm_waist_target}")
    print()

    print("观测缩放:")
    print(f"  ang_vel_scale: {config.ang_vel_scale}")
    print(f"  dof_pos_scale: {config.dof_pos_scale}")
    print(f"  dof_vel_scale: {config.dof_vel_scale}")
    print(f"  action_rescale_noise: {config.action_rescale_noise}")
    print()

    print("="*60)
    print("✓ 所有测试通过!")
    print("="*60)

except Exception as e:
    print(f"\n✗ 错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
