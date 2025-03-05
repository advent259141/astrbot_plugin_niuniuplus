# 牛牛插件plus使用说明

## 一、插件简介
本插件改进自长安某得牛牛小游戏插件。在原插件基础上增添了几项功能。在部分群友的要求和经过原作者允许的情况下上传本插件。

安装后自动启用 群内发送 牛牛菜单 查看详情

## 二、功能与玩法
原插件功能

- **指令**：`注册牛牛`
- **玩法说明**：在群聊中发送“注册牛牛”指令，系统会为你的牛牛随机分配一个初始长度，长度范围在 1 - 10cm 之间（可在配置文件中调整）。

- **指令**：`打胶`
- **玩法说明**：打胶是改变牛牛长度的重要操作。不过打胶有冷却时间限制：
    - **10 分钟内**：不允许打胶，若尝试会收到类似“[用户昵称]，你的牛牛还在疲惫状态呢，至少再歇 10 分钟呀！”的提示。
    - **10 - 30 分钟**：越接近 10 分钟，打胶失败（牛牛长度缩短）的概率越高。打胶结果可能是增长、缩短或无变化。
    - **30 分钟后**：正常判定打胶结果，牛牛长度可能增加、减少或保持不变。
    - 
- **指令**：`我的牛牛`
- **玩法说明**：发送该指令可查看你当前牛牛的长度，并获得相应评价。

- **指令**：`比划比划 @目标用户` 或 `比划比划 目标用户名关键词`
- **玩法说明**：
    - 可以 @ 一名已注册牛牛的用户，或者输入用户名关键词进行牛牛长度的较量。
    - **邀请限制**：10 分钟内主动邀请超过 3 人比划，会收到提示让牛牛休息。对同一用户 10 分钟内只能发起一次比划。
    - **结果判定**：
        - **两败俱伤（5% 概率）**：双方牛牛长度都减半。例如“[用户昵称] 和 [目标用户昵称]，发生了意外！双方的牛牛都折断了，长度都减半啦！”
        - ~~**长度相近（差距 ≤ 10）**：有 30% 概率发起者凭借硬度取胜，长度增加；否则提示双方长度差距不大。~~ 目前废弃了这个设定 全部改为概率胜利由长度以及硬度（隐藏）决定
        - ~~**一方长度占优**：长度较长者获胜，获胜方长度可能增加（增加范围可在配置文件中调整）。~~ 挑战设定 胜率动态设定由长度以及硬度（隐藏）决定 短牛牛挑战成长牛牛时有额外奖励

- **指令**：`牛牛排行`
- **玩法说明**：发送该指令可查看当前群内牛牛长度的排行榜，展示排名、用户昵称和牛牛长度。

！！！新增功能
- **指令**：`锁牛牛 @目标用户`
- **玩法说明**：可以锁一名用户的牛牛，使其长度随机变长或变短，甚至有概率长度减半

- - **指令**：`打工【xx】小时`
- **玩法说明**：在群聊中发送打工，以及相应时长，可以进行打工操作赚取金币。每打工一小时可以获得30金币。打工时长只能是整小时，单次以及每日限制6小时，且打工期间无法进行其他操作。
- 
- - **指令**：`打工时间`
- **玩法说明**：在群聊中发送打工时间，可以查看本次打工剩余时间。

- - **指令**：`每日签到`
- **玩法说明**：在群聊中发送每日签到，可以根据牛牛长度获得对应数目的金币，以及一张记录本月签到次数的鹿关日历。

- - **指令**：`鹿关日历`
**玩法说明**：在群聊中发送鹿关日历，可以快捷查看专属于你的本月签到日历，包含本月你的签到日期以及签到次数

- - **指令**：`牛牛商城`
- **玩法说明**：可以打开牛牛商城界面，里面目前包含三种神秘道具：伟哥，男科手术，六味地黄丸。可以用金币购买道具，使用道具可以对牛牛造成对应效果。

## 三、使用须知
由于本插件是在长安某的原牛牛插件上仅仅作了功能增添，因此安装了原牛牛插件的用户仅需卸载原插件并安装本插件即可，对原来的数据不会做出改动。

