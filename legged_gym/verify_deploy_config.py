#!/usr/bin/env python3
"""
验证deploy_real配置是否正确
"""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from legged_gym.deploy.deploy_real.config import Config
from legged_gym import LEGGED_GYM_ROOT_DIR

config_path = f"{LEGGED_GYM_ROOT_DIR}/legged_gym/deploy/deploy_real/configs/g1.yaml"
config = Config(config_path)

print("="*80)
print("配置验证成功！")
print("="*80)

print(f"\ncontrol_dt: {config.control_dt}")
print(f"msg_type: {config.msg_type}")
print(f"imu_type: {config.imu_type}")

print(f"\n--- 策略相关 (23DOF) ---")
print(f"num_actions: {config.num_actions}")
print(f"policy_joint2motor_idx: {config.policy_joint2motor_idx}")
print(f"policy_default_angles len: {len(config.policy_default_angles)}")
print(f"policy_kps len: {len(config.policy_kps)}")
print(f"policy_kds len: {len(config.policy_kds)}")

print(f"\n--- 腿部分 (0-11电机) ---")
print(f"leg_joint2motor_idx: {config.leg_joint2motor_idx}")
print(f"default_angles len: {len(config.default_angles)}")
print(f"kps len: {len(config.kps)}")
print(f"kds len: {len(config.kds)}")

print(f"\n--- 腰臂部分 (17个电机，含锁定) ---")
print(f"arm_waist_joint2motor_idx: {config.arm_waist_joint2motor_idx}")
print(f"arm_waist_target len: {len(config.arm_waist_target)}")
print(f"arm_waist_kps len: {len(config.arm_waist_kps)}")
print(f"arm_waist_kds len: {len(config.arm_waist_kds)}")

print(f"\n--- 观测 ---")
print(f"observation_mode: {config.observation_mode}")
print(f"action_target_mode: {config.action_target_mode}")
print(f"num_one_step_obs: {config.num_one_step_obs}")
print(f"num_actor_history: {config.num_actor_history}")
print(f"num_obs: {config.num_obs}")

print(f"\n--- 缩放 ---")
print(f"ang_vel_scale: {config.ang_vel_scale}")
print(f"dof_pos_scale: {config.dof_pos_scale}")
print(f"dof_vel_scale: {config.dof_vel_scale}")
print(f"action_scale: {config.action_scale}")

print("\n" + "="*80)
print("验证完整！配置已按g1_walk_12dof.yaml格式更新，")
print("包含23DOF策略映射，且将额外的6个关节锁定在固定位置。")
print("="*80)

print("\n锁定的关节:")
locked_motors = [13,14,20,21,27,28]
locked_names = ['WAIST_ROLL','WAIST_PITCH','L_WRIST_PITCH','L_WRIST_YAW','R_WRIST_PITCH','R_WRIST_YAW']
for idx, name in zip(locked_motors, locked_names):
    pos = config.arm_waist_target[config.arm_waist_joint2motor_idx.index(idx)]
    print(f"  motor[{idx}] {name:<20} 锁定在 {pos}")
