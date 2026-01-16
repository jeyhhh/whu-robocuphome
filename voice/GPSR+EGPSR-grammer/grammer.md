# GPSR+EGPSR-grammer 项目文档

## 📋 项目概述

**GPSR+EGPSR-grammer** 能够将自然语言指令转换为机器人可以执行的标准化GPSR（通用服务机器人指令）格式。

## 🏗️ 项目结构

## 📊 数据文件说明

### XML实体文件

**Objects.xml** - 物体定义
```xml
<category name="kitchen">
    <object name="cup" />
    <object name="bowl" />
    <object name="plate" />
</category>
```

**Locations.xml** - 位置定义
```xml
<room name="living_room">
    <location name="table" />
    <location name="sofa" />
</room>
```

**Names.xml** - 人名定义
```xml
<name>张三</name>
<name>李四</name>
<name>王五</name>
```

### 语法规则文件

**GPSRGrammar.txt** - 主要语法规则

**CommonRules.txt** - 通用语法规则


## 🎯 支持的指令类型

### 1. 物体查找指令
- "请去厨房拿一个杯子"
- "找到客厅里的遥控器"
- "告诉我桌子上有多少个苹果"

### 2. 人员引导指令
- "引导张三到卧室"
- "带李四去客厅"
- "跟随王五到厨房"

### 3. 复杂操作指令
- "清理客厅里的垃圾"
- "把碗放到厨房"
- "整理卧室的物品"

### 4. 信息查询指令
- "告诉我现在的时间"
- "说个笑话"
- "介绍一下你的团队"

## 🔌 依赖环境

### Python依赖 (requirements.txt)
```txt
numpy>=1.21.0          # 数值计算
pyaudio>=0.2.11        # 音频处理
funasr>=0.1.0          # 语音识别
xmltodict>=0.13.0      # XML解析
regex>=2022.3.15       # 正则表达式
```


## 🔍 未来期望

1. **多语言支持**: 支持中文自然语言处理
2. **实体识别**: 精确识别物体、位置、人名等实体
3. **语法解析**: 基于GPSR标准语法规则
4. **模糊匹配**: 支持编辑距离的模糊实体匹配
5. **模块化设计**: 各功能模块独立，易于扩展



---


