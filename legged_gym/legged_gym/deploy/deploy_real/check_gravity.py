#!/usr/bin/env python3
"""
重力投影检测脚本
用于检测机器人是否处于竖直状态
"""

import sys
import os
import time
import numpy as np

# 添加项目路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowState_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_ as LowStateHG

from common.rotation_helper import get_projected_gravity, get_gravity_orientation


class GravityChecker:
    def __init__(self, interface="enp0s31f6", msg_type="hg"):
        self.low_state = None
        self.state_received = False

        # 初始化 DDS
        ChannelFactoryInitialize(0, interface)

        # 创建 low state 订阅者
        if msg_type == "hg":
            self.lowstate_subscriber = ChannelSubscriber("rt/lowstate", LowStateHG)
        else:
            from unitree_sdk2py.idl.default import unitree_go_msg_dds__LowState_
            from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowState_ as LowStateGo
            self.lowstate_subscriber = ChannelSubscriber("rt/lowstate", LowStateGo)

        self.lowstate_subscriber.Init(self.lowstate_callback, 10)

        print("等待机器人数据...")
        self.wait_for_state()

    def lowstate_callback(self, msg):
        self.low_state = msg
        self.state_received = True

    def wait_for_state(self):
        while not self.state_received:
            time.sleep(0.01)
        print("已连接到机器人!")

    def check_vertical(self, tolerance=0.15):
        """
        检测机器人是否竖直

        参数:
            tolerance: 容忍度 (0.0 ~ 1.0)，越小越严格

        返回:
            is_vertical: 是否竖直
            projected_gravity: 重力投影向量
            deviation: 与理想竖直状态的偏差
        """
        # 获取 IMU 四元数 [w, x, y, z]
        quat = np.array([
            self.low_state.imu_state.quaternion[0],
            self.low_state.imu_state.quaternion[1],
            self.low_state.imu_state.quaternion[2],
            self.low_state.imu_state.quaternion[3]
        ])

        # 计算重力投影
        projected_gravity = get_projected_gravity(quat)

        # 理想竖直状态: 重力应该沿 -z 方向 [0, 0, -1]
        ideal_gravity = np.array([0.0, 0.0, -1.0])

        # 计算偏差 (点积)
        dot_product = np.dot(projected_gravity, ideal_gravity)

        # 计算角度偏差 (弧度)
        angle_deviation = np.arccos(np.clip(dot_product, -1.0, 1.0))

        # 计算水平分量的大小
        horizontal_magnitude = np.linalg.norm(projected_gravity[:2])

        # 判断是否竖直
        is_vertical = horizontal_magnitude < tolerance

        return is_vertical, projected_gravity, horizontal_magnitude, angle_deviation

    def print_status(self):
        """打印当前状态"""
        is_vertical, proj_grav, horizontal_mag, angle_dev = self.check_vertical()

        print("\n" + "="*60)
        print("机器人姿态检测")
        print("="*60)
        print(f"IMU 四元数 [w, x, y, z]: [{self.low_state.imu_state.quaternion[0]:.4f}, "
              f"{self.low_state.imu_state.quaternion[1]:.4f}, "
              f"{self.low_state.imu_state.quaternion[2]:.4f}, "
              f"{self.low_state.imu_state.quaternion[3]:.4f}]")
        print(f"重力投影向量: [{proj_grav[0]:.4f}, {proj_grav[1]:.4f}, {proj_grav[2]:.4f}]")
        print(f"水平分量大小: {horizontal_mag:.4f}")
        print(f"与竖直方向偏差: {np.degrees(angle_dev):.2f} 度")
        print(f"是否竖直: {'✓ 是' if is_vertical else '✗ 否'}")

        if not is_vertical:
            # 提示倾倒方向
            if abs(proj_grav[0]) > abs(proj_grav[1]):
                direction = "前" if proj_grav[0] > 0 else "后"
            else:
                direction = "左" if proj_grav[1] > 0 else "右"
            print(f"倾倒方向: {direction}")
        print("="*60 + "\n")

        return is_vertical


def main():
    import argparse

    parser = argparse.ArgumentParser(description="重力投影检测脚本")
    parser.add_argument("interface", type=str, nargs="?", default="enp0s31f6",
                        help="网络接口名称 (默认: enp0s31f6)")
    parser.add_argument("--msg-type", type=str, default="hg", choices=["hg", "go"],
                        help="消息类型 (默认: hg)")
    parser.add_argument("--tolerance", type=float, default=0.15,
                        help="竖直检测容忍度 (默认: 0.15)")
    parser.add_argument("--monitor", action="store_true",
                        help="持续监控模式")
    parser.add_argument("--interval", type=float, default=0.5,
                        help="监控间隔 (秒, 默认: 0.5)")

    args = parser.parse_args()

    print("="*60)
    print("Unitree G1 重力投影检测工具")
    print("="*60)

    try:
        checker = GravityChecker(interface=args.interface, msg_type=args.msg_type)

        if args.monitor:
            print(f"持续监控模式 (间隔: {args.interval}s)... 按 Ctrl+C 退出")
            try:
                while True:
                    checker.print_status()
                    time.sleep(args.interval)
            except KeyboardInterrupt:
                print("\n检测结束")
        else:
            checker.print_status()

    except Exception as e:
        print(f"错误: {e}")
        print("\n请检查:")
        print("1. 网络接口名称是否正确 (使用 'ip addr' 查看)")
        print("2. 机器人是否已连接并启动")
        print("3. 是否有防火墙阻止 DDS 通信")
        sys.exit(1)


if __name__ == "__main__":
    main()
