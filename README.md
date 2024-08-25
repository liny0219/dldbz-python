# dldbz-python

#### 介绍
{**以下是 Gitee 平台说明，您可以替换此简介**
Gitee 是 OSCHINA 推出的基于 Git 的代码托管平台（同时支持 SVN）。专为开发者提供稳定、高效、安全的云端软件开发协作平台
无论是个人、团队、或是企业，都能够用 Gitee 实现代码托管、项目管理、协作开发。企业项目请看 [https://gitee.com/enterprises](https://gitee.com/enterprises)}

#### 软件架构
软件架构说明


#### 安装教程

1.  pip install -r requirements.txt 安装依赖
2.  python -m uiautomator2 init     初始化uiautomator2

#### 使用说明

1.  修改模拟器的分辨率为960x540
2.  在config.json里修改adb port，雷电模拟器默认为127.0.0.1:5555，mumu模拟器默认为:127.0.0.1:16384
3.  启动脚本：python dldbz.py

#### 战斗DSL说明
##### 战斗开始
BattleStart

##### 战斗结束
BattleEnd

##### 前排角色1使用技能2，能量级别为3进行攻击
Role,1,2,3

##### 设置所有角色为最大能量
Boost

##### 切换前排和后排角色（不攻击）
SwitchAll

##### 切换角色1 TODO
Switch,1

##### 等待500毫秒
Wait,500

##### 跳过500毫秒（占位符逻辑）
Skip,500

##### 执行攻击
Attack

##### 角色1使用必杀技能
SP,1

##### 重置所有角色的技能和能量为0 TODO
Reset



#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request


