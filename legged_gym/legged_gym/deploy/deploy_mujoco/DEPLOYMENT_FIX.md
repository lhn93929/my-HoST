# MuJoCo 部署修复说明

## 问题描述
MuJoCo 部署中出现了**初始姿态错误**和**疯狂抽搐旋转**的问题，这是由于训练环境（Isaac Gym）与部署环境（MuJoCo）在多个方面存在不一致导致的。

## 已修复的问题

### 1. 关节顺序对齐 ✅
**问题**：配置文件中关节顺序与 URDF 定义不一致

**修复**：
- 更新配置文件关节顺序为 URDF 中的真实顺序
- URDF 顺序：hip_pitch → hip_roll → hip_yaw → knee → ankle_pitch → ankle_roll

### 2. 动作解释修复 ✅
**问题**：部署代码错误地将动作解释为绝对目标位置而非相对增量

**修复**：
```python
# 错误（原始代码）
target_dof_pos = action * action_scale + default_angles

# 正确（修复后）
target_dof_pos = d.qpos[7:] + action * action_scale
```

### 3. 初始姿态配置 ✅
**问题**：机器人初始为直立状态，而非训练时的俯卧姿态

**修复**：
- 在配置文件中添加 `init_base_quat` 和 `init_base_pos`
- `g1.yaml`（prone姿态）：`init_base_quat: [1.0, 0.0, -1.0, 0.0]`
- `g1_ground_prone.yaml`（prone姿态）：`init_base_quat: [1.0, 0.0, 1.0, 0.0]`

### 4. 力矩限幅 ✅
**问题**：部署时未对力矩进行限幅，可能导致过大扭矩

**修复**：
- 在配置文件中添加 `torque_limits`（从 URDF effort 限制提取）
- PD 控制后添加裁剪：`tau = np.clip(tau, -torque_limits, torque_limits)`

### 5. 观测历史缓冲初始化 ✅
**问题**：观测历史初始为全零，可能导致策略初期输出异常

**修复**：
- 在仿真开始前运行 `num_actor_history` 步来填充观测缓冲区
- 每步计算观测并更新历史缓冲

### 6. 重力投影计算 ✅
**问题**：`get_projected_gravity` 函数实现与 Isaac Gym 不一致

**修复**：
- 更新为与 Isaac Gym `quat_rotate_inverse` 完全一致的实现
- 正确处理四元数顺序：Isaac Gym 为 [x, y, z, w]，MuJoCo 为 [w, x, y, z]

## 配置文件说明

### g1.yaml
- 用于俯卧（prone）姿态起立训练的策略部署
- 初始四元数：`[1.0, 0.0, -1.0, 0.0]`（-90度绕Y轴）
- 默认关节角匹配 `g1_config_ground.py`

### g1_ground_prone.yaml
- 用于俯卧（prone）姿态起立的备选配置
- 初始四元数：`[1.0, 0.0, 1.0, 0.0]`（+90度绕Y轴）
- 默认关节角匹配 `g1_config_ground_prone.py`

## 观测空间
- 单步观测：76维
  - base_ang_vel (3)
  - projected_gravity (3)
  - dof_pos (23)
  - dof_vel (23)
  - actions (23)
  - action_rescale (1)
- 历史观测：456维（76 × 6步）

## 使用方法

```bash
# 进入项目目录
cd /home/lhn/HoST/legged_gym

# 激活正确的 conda 环境（如需要）
conda activate host
export PYTHONPATH=/home/lhn/HoST/legged_gym:$PYTHONPATH
# 运行部署
python legged_gym/deploy/deploy_mujoco/deploy_mujoco.py g1.yaml

# 或使用 prone 配置
python legged_gym/deploy/deploy_mujoco/deploy_mujoco.py g1_ground_prone.yaml
```

## 测试验证

运行测试脚本验证配置：
```bash
python legged_gym/deploy/deploy_mujoco/test_config.py
```

## 文件修改清单

1. `legged_gym/deploy/deploy_mujoco/configs/g1.yaml`
2. `legged_gym/deploy/deploy_mujoco/configs/g1_ground_prone.yaml`
3. `legged_gym/deploy/deploy_mujoco/deploy_mujoco.py`
4. `legged_gym/deploy/deploy_mujoco/test_config.py` (新建)
