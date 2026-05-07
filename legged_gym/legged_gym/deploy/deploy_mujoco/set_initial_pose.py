#!/usr/bin/env python3
"""
将机器人在 MuJoCo 中摆放到初始姿态
"""

import time
import mujoco.viewer
import mujoco
import numpy as np
import os
import sys
import yaml

# 添加项目路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from legged_gym import LEGGED_GYM_ROOT_DIR


def get_projected_gravity(quaternion):
    """计算重力投影 (与部署代码保持一致)"""
    qw, qx, qy, qz = quaternion[0], quaternion[1], quaternion[2], quaternion[3]
    q_vec = np.array([qx, qy, qz])
    v = np.array([0.0, 0.0, -1.0])

    a = v * (2.0 * qw**2 - 1.0)
    b = np.cross(q_vec, v) * (2.0 * qw)
    c = q_vec * np.dot(q_vec, v) * 2.0
    projected_gravity = a - b + c

    return projected_gravity


def main():
    import argparse

    parser = argparse.ArgumentParser(description="设置机器人初始姿态")
    parser.add_argument("config", type=str, nargs="?", default="g1.yaml",
                        help="配置文件名 (默认: g1.yaml)")
    parser.add_argument("--duration", type=float, default=5.0,
                        help="保持姿态的时间 (秒, 默认: 5.0)")
    parser.add_argument("--freeze", action="store_true",
                        help="冻结机器人 (锁定姿态)")

    args = parser.parse_args()

    # 加载配置
    config_path = f"configs/{args.config}"
    if not os.path.exists(config_path):
        config_path = f"{LEGGED_GYM_ROOT_DIR}/legged_gym/deploy/deploy_mujoco/configs/{args.config}"

    print(f"加载配置: {config_path}")
    with open(config_path, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        xml_path = config["xml_path"].replace("{LEGGED_GYM_ROOT_DIR}", LEGGED_GYM_ROOT_DIR)
        default_angles = np.array(config["default_angles"], dtype=np.float32)
        init_base_quat = np.array(config.get("init_base_quat", [1.0, 0.0, 0.0, 0.0]), dtype=np.float64)
        init_base_pos = np.array(config.get("init_base_pos", [0.0, 0.0, 0.5]), dtype=np.float64)

    print("="*60)
    print("MuJoCo 机器人初始姿态设置")
    print("="*60)

    # 加载模型
    print(f"加载模型: {xml_path}")
    m = mujoco.MjModel.from_xml_path(xml_path)
    d = mujoco.MjData(m)

    # 设置初始姿态
    print("\n设置初始姿态:")
    print(f"  基座位置: {init_base_pos}")
    print(f"  基座四元数 [w, x, y, z]: {init_base_quat}")
    print(f"  关节角度数量: {len(default_angles)}")

    d.qpos[0:3] = init_base_pos
    d.qpos[3:7] = init_base_quat
    d.qpos[7:7+len(default_angles)] = default_angles

    # 清零速度
    d.qvel[:] = 0.0
    d.qacc[:] = 0.0

    # 前向运动学
    mujoco.mj_forward(m, d)

    # 计算重力投影用于验证
    projected_gravity = get_projected_gravity(d.qpos[3:7])
    print(f"\n验证状态:")
    print(f"  重力投影向量: [{projected_gravity[0]:.4f}, {projected_gravity[1]:.4f}, {projected_gravity[2]:.4f}]")
    print(f"  水平分量大小: {np.linalg.norm(projected_gravity[:2]):.4f}")

    # 显示关节信息
    print(f"\n关节信息 (共 {m.nu} 个):")
    for i in range(min(m.nu, 23)):
        joint_name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i+1) if i+1 < m.njnt else f"joint_{i}"
        print(f"  [{i:2d}] {joint_name or f'joint_{i}':30s}: {d.qpos[7+i]:8.4f} rad")

    if args.freeze:
        # 冻结模式: 锁定所有关节
        print("\n冻结模式: 已将所有关节锁定在当前位置")

    print(f"\n启动 viewer, 将保持 {args.duration} 秒...")

    # 启动 viewer
    with mujoco.viewer.launch_passive(m, d) as viewer:
        start = time.time()
        while viewer.is_running() and time.time() - start < args.duration:
            step_start = time.time()

            if args.freeze:
                # 冻结模式: 不断重置姿态
                d.qpos[0:3] = init_base_pos
                d.qpos[3:7] = init_base_quat
                d.qpos[7:7+len(default_angles)] = default_angles
                d.qvel[:] = 0.0
                mujoco.mj_forward(m, d)
            else:
                # PD 控制保持姿态
                kps = np.array(config.get("kps", [200]*len(default_angles)), dtype=np.float32)
                kds = np.array(config.get("kds", [10]*len(default_angles)), dtype=np.float32)

                tau = (default_angles - d.qpos[7:]) * kps - d.qvel[6:] * kds

                # 应用力矩限制
                torque_limits = np.array(config.get("torque_limits", [np.inf]*len(default_angles)), dtype=np.float32)
                tau = np.clip(tau, -torque_limits, torque_limits)

                d.ctrl[:] = tau
                mujoco.mj_step(m, d)

            viewer.sync()

            # 保持实时率
            time_until_next_step = m.opt.timestep - (time.time() - step_start)
            if time_until_next_step > 0:
                time.sleep(time_until_next_step)

        print("\n时间到，退出 viewer")


if __name__ == "__main__":
    main()
