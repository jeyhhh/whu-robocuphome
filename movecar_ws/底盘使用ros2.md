
# 底盘使用教程

文档内容以.md格式为准

## 硬件连接

参考说明书进行连接，遥控器 `SWB` 拨到最上方

## 下载安装包

`tracer_ros2-humble`

`ugv_sdk-main`

创建`movecar_ws/src`，将两个安装包放入里面，在`movecar_ws`文件夹下运行

```
colcon build
```

运行编译命令时，如果遇到asio.hpp错误，运行下述命令

```
sudo apt install libasio-dev
```

安装成功后再次进行编译


## 测试CANABLE硬件与CAN 通讯

### 设置CAN-TO-USB适配器

使能 gs_usb 内核模块

```
sudo modprobe gs_usb
```

设置500k波特率和使能can-to-usb适配器
```
sudo ip link set can0 up type can bitrate 500000
```

如果在前⾯的步骤中没有发⽣错误，您应该可以使⽤命令⽴即查看can设备

```
ifconfig -a
```

你应该在第一个设备看到一个“can0”

安装并使⽤can-utils来测试硬件

```
sudo apt install can-utils
```

若此次can-to-usb已经和TRACER机器⼈相连，且⼩⻋已经开启的情况下，使⽤下列指令

```
candump can0
```
可以监听来⾃ TRACER底盘的数据了

## 使用ros2软件包

首次使用 creatr-ros2 软件包

```
cd ~/movecar_ws/src/ugv_sdk-main/scripts/
bash setup_can2usb.bash
```

如果不是第一次使用 tracer-ros2 包(每次关闭电源时都运行此命令)

```
cd ~/movecar_ws/src/ugv_sdk-main/scripts/
bash bringup_can2usb_500k.bash
```

## 使用ros2控制

进入`movecar_ws`文件夹，打开终端输入

```
source install/setup.bash
ros2 launch tracer_base tracer_base.launch.py
```

成功后，在同一个文件夹下打开一个新终端

```
source install/setup.bash

ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

根据实验结果，linear内的x，y可以操控机器人运动，angular的z可以操控机器人转向，其他变量暂时没有用途