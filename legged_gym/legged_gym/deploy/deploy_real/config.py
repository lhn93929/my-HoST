import os
import sys
import numpy as np
import yaml

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from legged_gym import LEGGED_GYM_ROOT_DIR
except ModuleNotFoundError:
    LEGGED_GYM_ROOT_DIR = PROJECT_ROOT


class Config:
    def __init__(self, file_path) -> None:
        with open(file_path, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

            self.control_dt = config["control_dt"]

            self.msg_type = config["msg_type"]
            self.imu_type = config["imu_type"]

            self.weak_motor = []
            if "weak_motor" in config:
                self.weak_motor = config["weak_motor"]

            self.lowcmd_topic = config.get("lowcmd_topic", "rt/lowcmd")
            self.lowstate_topic = config.get("lowstate_topic", "rt/lowstate")

            self.policy_path = config["policy_path"].replace("{LEGGED_GYM_ROOT_DIR}", LEGGED_GYM_ROOT_DIR)

            # 处理观测相关缩放
            self.ang_vel_scale = config["ang_vel_scale"]
            self.dof_pos_scale = config["dof_pos_scale"]
            self.dof_vel_scale = config["dof_vel_scale"]
            self.action_scale = config["action_scale"]
            self.action_rescale_noise = config.get("action_rescale_noise", 0.0)

            # cmd_scale 和 max_cmd 是可选的（仅在 legacy_command 模式需要）
            self.cmd_scale = np.array(config.get("cmd_scale", [2.0, 2.0, 0.25]), dtype=np.float32)
            self.max_cmd = np.array(config.get("max_cmd", [0.8, 0.5, 1.57]), dtype=np.float32)

            self.num_actions = config["num_actions"]
            self.num_one_step_obs = config.get("num_one_step_obs", None)
            self.num_actor_history = config.get("num_actor_history", 1)
            self.num_obs = config["num_obs"]
            self.observation_mode = config.get("observation_mode", "legacy_command")
            self.action_target_mode = config.get("action_target_mode", "default_offset")

            # 读取完整的 policy 相关配置
            if "policy_joint2motor_idx" in config:
                self.policy_joint2motor_idx = config["policy_joint2motor_idx"]
            else:
                raise ValueError("policy_joint2motor_idx is required in config")

            if "policy_default_angles" in config:
                self.policy_default_angles = np.array(config["policy_default_angles"], dtype=np.float32)
            elif "default_angles" in config:
                self.policy_default_angles = np.array(config["default_angles"], dtype=np.float32)
            else:
                raise ValueError("policy_default_angles or default_angles is required in config")

            if "policy_kps" in config:
                self.policy_kps = config["policy_kps"]
            elif "kps" in config:
                self.policy_kps = config["kps"]
            else:
                raise ValueError("policy_kps or kps is required in config")

            if "policy_kds" in config:
                self.policy_kds = config["policy_kds"]
            elif "kds" in config:
                self.policy_kds = config["kds"]
            else:
                raise ValueError("policy_kds or kds is required in config")

            # 向后兼容：如果没有分开的 leg/arm_waist 配置，从完整配置中提取
            # 假设顺序: left leg (6), right leg (6), waist (1), left arm (5), right arm (5)
            if "leg_joint2motor_idx" in config:
                self.leg_joint2motor_idx = config["leg_joint2motor_idx"]
            else:
                # 前12个是腿 (左6 + 右6)
                self.leg_joint2motor_idx = self.policy_joint2motor_idx[:12]

            if "arm_waist_joint2motor_idx" in config:
                self.arm_waist_joint2motor_idx = config["arm_waist_joint2motor_idx"]
            else:
                # 后11个是腰+手臂 (腰1 + 左臂5 + 右臂5)
                self.arm_waist_joint2motor_idx = self.policy_joint2motor_idx[12:]

            if "kps" in config:
                self.kps = config["kps"]
            else:
                self.kps = self.policy_kps

            if "kds" in config:
                self.kds = config["kds"]
            else:
                self.kds = self.policy_kds

            if "default_angles" in config:
                self.default_angles = np.array(config["default_angles"], dtype=np.float32)
            else:
                self.default_angles = self.policy_default_angles.copy()

            if "arm_waist_kps" in config:
                self.arm_waist_kps = config["arm_waist_kps"]
            else:
                # 从完整 kps 提取后11个
                self.arm_waist_kps = self.policy_kps[12:]

            if "arm_waist_kds" in config:
                self.arm_waist_kds = config["arm_waist_kds"]
            else:
                # 从完整 kds 提取后11个
                self.arm_waist_kds = self.policy_kds[12:]

            if "arm_waist_target" in config:
                self.arm_waist_target = np.array(config["arm_waist_target"], dtype=np.float32)
            else:
                # 从 policy_default_angles 提取后11个
                self.arm_waist_target = self.policy_default_angles[12:].copy()

            if self.observation_mode == "mujoco_history":
                one_step_obs = 3 + 3 + self.num_actions * 3 + 1
                expected_obs = one_step_obs * self.num_actor_history
                if self.num_one_step_obs != one_step_obs:
                    raise ValueError(f"num_one_step_obs must be {one_step_obs}, got {self.num_one_step_obs}")
                if self.num_obs != expected_obs:
                    raise ValueError(f"num_obs must be {expected_obs}, got {self.num_obs}")
                self._validate_policy_sequence("policy_joint2motor_idx", self.policy_joint2motor_idx)
                self._validate_policy_sequence("policy_default_angles", self.policy_default_angles)
                self._validate_policy_sequence("policy_kps", self.policy_kps)
                self._validate_policy_sequence("policy_kds", self.policy_kds)

    def _validate_policy_sequence(self, name, value):
        if len(value) != self.num_actions:
            raise ValueError(f"{name} must have {self.num_actions} entries, got {len(value)}")