import time

import mujoco.viewer
import mujoco
import numpy as np
import os
import sys
import torch
import yaml

# 确保使用当前项目源码，而非已安装包
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from legged_gym import LEGGED_GYM_ROOT_DIR
# print("Actual LEGGED_GYM_ROOT_DIR:", LEGGED_GYM_ROOT_DIR)

# 训练策略输出索引（0~22）
# 左腿 (0-5): yaw(0), roll(1), pitch(2), knee(3), ankle_pitch(4), ankle_roll(5)
# 右腿 (6-11): yaw(6), roll(7), pitch(8), knee(9), ankle_pitch(10), ankle_roll(11)
# 腰部 (12): waist_yaw
# 左臂 (13-17): shoulder_pitch, shoulder_roll, shoulder_yaw, elbow, wrist_roll (相同)
# 右臂 (18-22): 相同

# MuJoCo 目标顺序（0~22）
# 左腿: pitch(0), roll(1), yaw(2), knee(3), ankle_pitch(4), ankle_roll(5)
# 右腿: pitch(6), roll(7), yaw(8), knee(9), ankle_pitch(10), ankle_roll(11)

# train_to_mujoco = np.array([
#     2, 1, 0, 3, 4, 5,      # 左腿：yaw→pitch, roll→roll, pitch→yaw, knee, ankle_pitch, ankle_roll
#     8, 7, 6, 9, 10, 11,     # 右腿：同上
#     12,                     # waist
#     13, 14, 15, 16, 17,     # 左臂相同
#     18, 19, 20, 21, 22      # 右臂相同
# ], dtype=int)

def get_projected_gravity(quaternion):
    """
    Compute projected gravity vector from quaternion (rotation from world to body frame).
    Gravity in world frame is (0, 0, -1), so projected gravity is
    world z-axis rotated to body frame.

    Isaac Gym uses quaternion order [x, y, z, w] forquat_rotate_inverse.
    MuJoCo returns quaternion in [w, x, y, z] order.
    We need to convert to Isaac Gym order for the computation.

    Isaac Gym's quat_rotate_inverse:
    v' = v * (2*q_w^2 - 1) + q_vec x v * (2*q_w) + q_vec x (q_vec x v) * (2)
    where q_w is quaternion.w, q_vec is quaternion.xyz
    """
    # Input quaternion is [w, x, y, z] from MuJoCo
    qw, qx, qy, qz = quaternion[0], quaternion[1], quaternion[2], quaternion[3]
    q_vec = np.array([qx, qy, qz])
    v = np.array([0.0, 0.0, -1.0])  # Gravity in world frame

    # v' = v * (2*q_w^2 - 1) + q_vec x v * (2*q_w) + q_vec x (q_vec x v) * (2)
    a = v * (2.0 * qw**2 - 1.0)
    b = np.cross(q_vec, v) * (2.0 * qw)
    c = q_vec * np.dot(q_vec, v) * 2.0
    projected_gravity = a - b + c

    return projected_gravity


def pd_control(target_q, q, kp, target_dq, dq, kd):
    """Calculates torques from position commands"""
    return (target_q - q) * kp + (target_dq - dq) * kd


if __name__ == "__main__":
    # get config file name from command line
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", type=str, help="config file name in config folder")
    args = parser.parse_args()
    config_file = args.config_file

    # Use current working directory for config file
    config_path = f"deploy/deploy_mujoco/configs/{config_file}"
    if not os.path.exists(config_path):
        # Fallback to LEGGED_GYM_ROOT_DIR
        config_path = f"{LEGGED_GYM_ROOT_DIR}/legged_gym/deploy/deploy_mujoco/configs/{config_file}"

    with open(config_path, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        policy_path = config["policy_path"].replace("{LEGGED_GYM_ROOT_DIR}", LEGGED_GYM_ROOT_DIR)
        xml_path = config["xml_path"].replace("{LEGGED_GYM_ROOT_DIR}", LEGGED_GYM_ROOT_DIR)

        simulation_duration = config["simulation_duration"]
        simulation_dt = config["simulation_dt"]
        control_decimation = config["control_decimation"]

        kps = np.array(config["kps"], dtype=np.float32)
        kds = np.array(config["kds"], dtype=np.float32)

        default_angles = np.array(config["default_angles"], dtype=np.float32)

        ang_vel_scale = config["ang_vel_scale"]
        dof_pos_scale = config["dof_pos_scale"]
        dof_vel_scale = config["dof_vel_scale"]
        action_scale = config["action_scale"]

        num_actions = config["num_actions"]
        num_one_step_obs = config["num_one_step_obs"]
        num_actor_history = config["num_actor_history"]
        num_obs = config["num_obs"]

        # Initial base pose from config (optional, defaults to identity)
        init_base_quat = config.get("init_base_quat", [0.70710678, 0.0, -0.70710678, 0.0])  # w,x,y,z
        init_base_pos = config.get("init_base_pos", [0.0, 0.0, 0.5])

        # Torque limits from config (optional, no clipping if not provided)
        torque_limits = np.array(config.get("torque_limits", [float('inf')] * num_actions), dtype=np.float32)

    # define context variables
    action = np.zeros(num_actions, dtype=np.float32)
    target_dof_pos = default_angles.copy()
    obs = np.zeros(num_obs, dtype=np.float32)
    action_rescale = action_scale

    counter = 0

    # Load robot model
    m = mujoco.MjModel.from_xml_path(xml_path)
    d = mujoco.MjData(m)
    m.opt.timestep = simulation_dt
    # # ========== 新增：将期望初始姿态设为模型默认 reset 状态 ==========
    # # 构建初始 qpos 向量 (nq = 7 基座 + 23 关节 = 30)
    # desired_qpos = np.zeros(m.nq)
    # # 基座位置 (x,y,z)
    # desired_qpos[0:3] = init_base_pos
    # # 基座姿态四元数 (w,x,y,z)
    # desired_qpos[3:7] = init_base_quat
    # # 关节角度
    # desired_qpos[7:] = default_angles

    # # 写入模型的 qpos0（MuJoCo reset 时的目标状态）
    # m.qpos0[:] = desired_qpos

    # # 同时将当前状态也设置为该初始状态
    # d.qpos[:] = desired_qpos
    # mujoco.mj_forward(m, d)
    # # =============================================================
    # Set initial base pose
    d.qpos[0:3] = init_base_pos
    d.qpos[3:7] = init_base_quat
    # Set initial joint angles
    d.qpos[7:] = default_angles

    # load policy
    policy = torch.jit.load(policy_path)

    # Initialize observation history by running some steps without control
    print("Initializing observation history buffer...")
    for _ in range(num_actor_history):
        mujoco.mj_forward(m, d)
        qj = d.qpos[7:]
        dqj = d.qvel[6:]
        quat = d.qpos[3:7]
        omega = d.qvel[3:6]

        # Scale observations
        dof_pos_scaled = qj * dof_pos_scale
        dof_vel_scaled = dqj * dof_vel_scale
        projected_gravity = get_projected_gravity(quat)
        omega_scaled = omega * ang_vel_scale

        # Build single step observation
        current_obs = np.concatenate([
            omega_scaled,
            projected_gravity,
            dof_pos_scaled,
            dof_vel_scaled,
            action,
            [action_rescale + (np.random.rand() - 0.5) * 0.05]
        ])

        # Update history buffer
        obs = np.roll(obs, -num_one_step_obs)
        obs[-num_one_step_obs:] = current_obs
    print("Stabilizing initial contact...")
    for _ in range(800):
        d.ctrl[:] = 0.0
        mujoco.mj_step(m, d)
    with mujoco.viewer.launch_passive(m, d) as viewer:
        # Close the viewer automatically after simulation_duration wall-seconds.
        start = time.time()
        while viewer.is_running() and time.time() - start < simulation_duration:
            step_start = time.time()

            # qvel_arm = d.qvel[6:]   # 所有关节速度
            # max_vel = np.max(np.abs(qvel_arm))
            # if max_vel > 0.5:   # 阈值可调
            #     print(f"Step {counter}: max joint vel = {max_vel:.3f} rad/s")
            #     # 打印前几个关节速度
            #     print("First 6 joint vels:", qvel_arm[:6])
            # Compute PD control
            tau = pd_control(target_dof_pos, d.qpos[7:], kps, np.zeros_like(kds), d.qvel[6:], kds)
            # # 计算阻尼力矩分量
            # damping_torque = -kds * d.qvel[6:]
            # max_damping = np.max(np.abs(damping_torque))
            # if max_damping > 10.0:   # 假设阻尼力矩超过10 N·m视为异常
            #     print(f"Step {counter}: max damping torque = {max_damping:.2f} N·m")
            # Apply torque limits
            tau = np.clip(tau, -torque_limits, torque_limits)

            d.ctrl[:] = tau

            # mj_step can be replaced with code that also evaluates
            # a policy and applies a control signal before stepping the physics.
            mujoco.mj_step(m, d)

            counter += 1
            if counter % control_decimation == 0:
                # Apply control signal here.

                # create observation matching host_ground.py compute_observations
                qj = d.qpos[7:]
                dqj = d.qvel[6:]
                quat = d.qpos[3:7]
                omega = d.qvel[3:6]

                # Scale observations to match training environment
                dof_pos_scaled = qj * dof_pos_scale
                dof_vel_scaled = dqj * dof_vel_scale
                projected_gravity = get_projected_gravity(quat)
                omega_scaled = omega * ang_vel_scale

                # Build single step observation: 76 dims
                # [base_ang_vel (3), projected_gravity (3), dof_pos (23), dof_vel (23), actions (23), action_rescale (1)]
                current_obs = np.concatenate([
                    omega_scaled,
                    projected_gravity,
                    dof_pos_scaled,
                    dof_vel_scaled,
                    action,
                    [action_rescale + (np.random.rand() - 0.5) * 0.05]  # action_rescale with noise
                ])

                # Update history buffer (shift left and append new)
                obs = np.roll(obs, -num_one_step_obs)
                obs[-num_one_step_obs:] = current_obs
            # ----- 延迟期内仅保持默认姿态，不启用策略 -----
                if counter < 4000:
                    action = np.zeros(num_actions, dtype=np.float32)
                    target_dof_pos = default_angles.copy()
                else:
                    obs_tensor = torch.from_numpy(obs).unsqueeze(0)
                    action = policy(obs_tensor).detach().numpy().squeeze()
                    target_dof_pos = d.qpos[7:] + action * action_scale
                # obs_tensor = torch.from_numpy(obs).unsqueeze(0)
                # # policy inference
                # action = policy(obs_tensor).detach().numpy().squeeze()
                # # action = action[train_to_mujoco]   # 重排为 MuJoCo 顺序

                # # CRITICAL FIX: Action is relative to current joint position, not default_angles
                # # Training: joint_pos_target = dof_pos + action * action_scale
                # target_dof_pos = d.qpos[7:] + action * action_scale
                # # target_dof_pos = default_angles.copy()

            # Pick up changes to the physics state, apply perturbations, update options from GUI.
            viewer.sync()

            # Rudimentary time keeping, will drift relative to wall clock.
            time_until_next_step = m.opt.timestep - (time.time() - step_start)
            if time_until_next_step > 0:
                time.sleep(time_until_next_step)
