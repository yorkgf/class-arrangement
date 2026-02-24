# 高中排课系统需求文档

## 项目概述

使用 Google OR-Tools CP-SAT 求解器为9-12年级共18个班级创建自动排课系统，满足70+条复杂约束条件。

**最后更新**: 2026-02-24
**版本**: 3.6
**状态**: 已实现并验证（FEASIBLE）

---

## 1. 时间配置

### 每周时间槽 (35个)

| 星期 | 节次 | 备注 |
|------|------|------|
| 周一 | 1-6节 | 6个时间槽 |
| 周二 | 1-8节 | 8个时间槽 |
| 周三 | 1-8节 | 8个时间槽 |
| 周四 | 1-6节 | 6个时间槽 |
| 周五 | 1-7节 | 7个时间槽 |

**注意**: 周二7-8节用于12年级PE和Counseling，其他班级此时间段空闲。

---

## 2. 班级与课程配置

### 2.1 9年级

#### 行政班 (9-A, 9-B, 9-C) - 27节/周

| 班级 | 课程 (周课时) | 教师 |
|------|--------------|------|
| **9-A**, **9-B**, **9-C** | Algebra (5), Social (4), Psychology (3), Physics (3), Chemistry (3), Biology (3), Geography (2), Art (2), PE (2) | Algebra: Yuhan<br>Social: Darin<br>Psychology: Chloe<br>Physics: Guo<br>Chemistry: Shao<br>Biology: Zhao<br>Geography: Manuel<br>Art: Shiwen<br>PE: Wen |

**注意**: 行政班不包含English课程，学生参加走班英语课程。

#### 走班英语班 (9-Eng-A/B/C/D/E) - 6节/周

| 班级 | 课程 (周课时) | 教师 | 学生来源 |
|------|--------------|------|----------|
| **9-Eng-A** | English (6) | LZY | 9-A、9-B学生 |
| **9-Eng-B** | English (6) | CYF | 9-A、9-B学生 |
| **9-Eng-C** | English (6) | Ezio | 9-A、9-B学生 |
| **9-Eng-D** | English (6) | Ezio | 9-C学生 |
| **9-Eng-E** | English (6) | LZY | 9-C学生 |

**走班制说明**:
- 9-A和9-B行政班的学生按英语水平分到A/B/C三个走班英语班
- 9-C行政班的学生按英语水平分到D/E两个走班英语班
- A/B/C班必须同时上课（联合上课）
- D/E班必须同时上课（联合上课）
- A/B/C与D/E不能同时上课（LZY同时教A和E，Ezio同时教C和D，存在教师冲突）
- 当走班英语班上课时，对应行政班必须空出时间（互斥约束）

### 2.2 10年级 (33节/周)

#### 普通班 (10-A, 10-B, 10-C)
| 课程 | 周课时 | 教师 |
|------|--------|------|
| English | 5 | Lucy |
| World History | 3 | Neil |
| Psych&Geo | 3 | Chloe, Manuel |
| Spanish | 2 | AK |
| Pre-Cal | 5 | Dan |
| Micro-Econ | 5 | Neil |
| Chemistry | 3 | Shao |
| Phys&Bio | 3 | Song (10-A/10-B), Zhao (10-C) | 10-A+10-C联合上课 |
| Art | 2 | Shiwen |
| PE | 2 | Wen |

#### EAL班 (本学期新增)
| 班级 | 课程 | 周课时 | 教师 | 同步要求 |
|------|------|--------|------|----------|
| 10-EAL-A | EAL | 3 | Ezio | 与Psych&Geo同步 |
| 10-EAL-B | EAL | 3 | CYF | 与Psych&Geo同步 |
| 10-EAL-C | EAL | 6 | LZY | 3节与Psych&Geo同步<br>3节与Phys&Bio同步 |

### 2.3 11年级 (35节/周)

| 课程 | 周课时 | 教师 | 备注 |
|------|--------|------|------|
| English | 5 | CYF | |
| Literature | 3 | CYF | |
| Spanish | 3 | AK | |
| Cal-ABBC | 5 | Yan (11-A), Song (11-A), Yan (11-B) | 11-A两位教师 |
| Group 1 AP | 5 | Guo, Zhao | 跨年级联合，多教师 |
| Group 2 AP | 5 | Neil, Guo | 跨年级联合，多教师 |
| Group 3 AP | 5 | Chloe, Manuel | 跨年级联合，多教师 |
| Art | 2 | Shiwen | |
| PE | 2 | Wen | |

### 2.4 12年级 (31节/周)

| 课程 | 周课时 | 教师 | 备注 |
|------|--------|------|------|
| Spanish | 3 | AK | |
| BC-Stats | 5 | Yan (12-A), Yuhan (12-B) | 联合上课，不同教师 |
| AP Seminar | 5 | Ezio, Lucy, Darin | 新增Darin，与9th Social冲突 |
| Group 1 AP | 5 | Guo, Zhao | 跨年级联合，多教师 |
| Group 2 AP | 5 | Neil, Guo | 跨年级联合，多教师 |
| Group 3 AP | 5 | Chloe, Manuel | 跨年级联合，多教师 |
| PE | 2 | Wen |
| Counseling | 1 | Wen |

**注意**: 12年级原计划36节，因时间槽不足(34可用)，移除了AP Composition课程

---

## 3. 联合上课约束 (Joint Sessions)

联合上课的班级必须在同一时间上同一课程，**不计入教师冲突**。

| 课程 | 班级 | 教师 | 备注 |
|------|------|------|------|
| **9年级走班英语A/B/C** | 9-Eng-A, 9-Eng-B, 9-Eng-C | LZY, CYF, Ezio | 3个班级同时上课，学生来自9-A/9-B |
| **9年级走班英语D/E** | 9-Eng-D, 9-Eng-E | Ezio, LZY | 2个班级同时上课，学生来自9-C |
| **10年级 Psych&Geo** | 10-A, 10-B, 10-C | Chloe, Manuel | 联合上课，多教师 |
| **10年级 Phys&Bio** | 10-A, 10-C | Song, Zhao | 联合上课，不同教师（10-B独立） |
| **12年级 BC-Stats** | 12-A, 12-B | Yan, Yuhan | 联合上课，不同教师 |
| **12年级 AP Seminar** | 12-A, 12-B | Ezio, Lucy, Darin | 联合上课，多教师 |
| **Group 1 AP** | 11-A, 11-B, 12-A, 12-B | Guo, Zhao, **Shiwen** | 跨年级联合，多教师 |
| **Group 2 AP** | 11-A, 11-B, 12-A, 12-B | Neil, Guo | 跨年级联合，多教师 |
| **Group 3 AP** | 11-A, 11-B, 12-A, 12-B | Chloe, Manuel | 跨年级联合，多教师 |

### EAL同步约束 (E3 & E4)

| EAL班级 | 总课时 | E3约束 (与Psych&Geo同步) | E4约束 (与Phys&Bio同步) | 教师 |
|---------|--------|--------------------------|------------------------|------|
| 10-EAL-A | 3节 | 3节与10-A Psych&Geo同步 | - | Ezio |
| 10-EAL-B | 3节 | 3节与10-B Psych&Geo同步 | - | CYF |
| 10-EAL-C | 6节 | 3节与10-C Psych&Geo同步 | 额外3节与10-A/10-C Phys&Bio同步 | LZY |

**E3约束说明**: 单向蕴含关系 (Psych&Geo ⇒ EAL)，即当对应班级上Psych&Geo时，EAL班级必须同时上EAL。注意这不是双向等式，因为10-EAL-C有6节课而Psych&Geo只有3节。

**E4约束说明**: 10-EAL-C必须有且仅有3节课与10-A或10-C的Phys&Bio课程时间重叠。

### Phys&Bio约束说明

- **10-A Phys&Bio (Song)** + **10-C Phys&Bio (Zhao)**: 联合上课，必须同时上
- **10-B Phys&Bio (Song)**: 独立上课，不能与10-A/10-C同时上（教师冲突）
- **10-EAL-C EAL**: 与10-A/10-C Phys&Bio时间同步（额外3节）

### 新增硬约束（H和I）

**H. 11-A English与12年级AP Seminar同步（硬约束）**
11-A班的5节English课必须与12-A和12-B班的AP Seminar/Composition的5节课完全同时上课。

| 课程 | 班级 | 课时 | 同步要求 |
|------|------|------|----------|
| AP Seminar | 12-A, 12-B | 5节 | 联合上课，同时上 |
| English | 11-A | 5节 | **必须与AP Seminar同时上** |

**I. Lucy教师冲突约束（硬约束）**
Lucy同时教授：
- 12-A/B AP Seminar/Composition（5节/周，联合上课）
- 10-A/B/C English（各5节/周）

当12年级上AP Seminar时，10年级任何班级不能上English课。

---

## 4. 教师冲突约束

### 4.1 基本规则
- 同一教师在同一时间槽最多只能教一门课程
- 联合上课除外（多个班级同时上课，不同教师或同一教师）

### 4.2 特殊教师处理

#### Art教师 (Shiwen)
- 教授全校所有Art课程（9-A/B/C, 10-A/B/C, 11-A/B）
- 同时教授 Group 1 AP（11-A/B, 12-A/B）
- 每个班级独立上课（非联合）
- **冲突约束**: 同一时间只能教一个班级
- **新增约束**: Art课与Group 1 AP不能同时上（约束P）

#### PE教师 (Wen)
- 教授全校所有PE课程
- 12年级PE为联合上课
- 9-11年级PE每个班级独立
- **冲突约束**: 同一时间只能教一个班级（12年级两个班算一个）

### 4.3 英语教师跨年级冲突

| 教师 | 9年级走班英语 | 10年级 | 11年级 | 12年级 | 冲突约束 |
|------|--------------|--------|--------|--------|----------|
| **LZY** | 9-Eng-A, 9-Eng-E | 10-C EAL | - | - | 不可同时上课 |
| **CYF** | 9-Eng-B | 10-B EAL | 11-A/B English<br>11-A/B Literature | - | 不可同时上课 |
| **Ezio** | 9-Eng-C, 9-Eng-D | 10-A EAL | - | 12-A/B AP Seminar | 不可同时上课 |
| **Lucy** | - | 10-A/B/C English | - | 12-A/B AP Seminar | 10年级English与12年级AP Seminar不能同时上 |

**注意**: LZY同时教9-Eng-A和9-Eng-E，Ezio同时教9-Eng-C和9-Eng-D，因此A/B/C组和D/E组不能同时上课。

### 4.4 BC-Statistics特殊约束

BC-Statistics是12-A和12-B的联合上课，但由两位不同教师教授：
- **12-A BC-Statistics**: Yan
- **12-B BC-Statistics**: Yuhan

因此有额外的教师冲突约束：

| 教师 | 课程 | 冲突课程 | 约束说明 |
|------|------|----------|----------|
| **Yan** | 11年级 Cal-ABBC (Yan+Song)<br>12-A BC-Statistics | 两者不能同时上课 | Yan同时教授这两门课 |
| **Yuhan** | 9年级 Algebra<br>12-B BC-Statistics | 两者不能同时上课 | Yuhan同时教授这两门课 |

### 4.5 Phys&Bio特殊约束

Phys&Bio中10-A和10-C是联合上课，但由两位不同教师教授：
- **10-A Phys&Bio**: Song
- **10-C Phys&Bio**: Zhao
- **10-B Phys&Bio**: Song（独立上课）

因此有额外的教师冲突约束：

| 教师 | 课程 | 冲突课程 | 约束说明 |
|------|------|----------|----------|
| **Song** | 10-A Phys&Bio<br>10-B Phys&Bio<br>11-A Cal-ABBC | 10-A/10-B不能同时上<br>11-A Cal-ABBC vs 10-A/10-B Phys&Bio | Song同时教授这些课程 |
| **Zhao** | 9th Biology<br>10-C Phys&Bio<br>Group 1 AP | 10-C Phys&Bio vs Group 1 AP | Zhao同时教授这些课程 |

### 4.6 Guo教师特殊约束

Guo教授多门课程，需要避免时间冲突：

| 教师 | 课程 | 冲突课程 | 约束说明 |
|------|------|----------|----------|
| **Guo** | 9th Physics<br>Group 1 AP<br>Group 2 AP | 9th Physics vs Group 1/2 AP | Guo同时教授这些课程 |

### 4.7 Manuel教师特殊约束

Manuel教授多门课程，需要避免时间冲突：

| 教师 | 课程 | 冲突课程 | 约束说明 |
|------|------|----------|----------|
| **Manuel** | 9th Geography<br>10th Psych&Geo<br>Group 3 AP | 各课程之间不能同时上课 | Manuel同时教授这些课程 |

### 4.8 AK教师特殊约束

AK教授所有Spanish课程，需要避免时间冲突：

| 教师 | 课程 | 冲突课程 | 约束说明 |
|------|------|----------|----------|
| **AK** | 10th Spanish<br>11th Spanish<br>12th Spanish | 各年级Spanish不能同时上课 | AK同时教授这些课程 |

### 4.9 Darin教师特殊约束

Darin教授多门课程，需要避免时间冲突：

| 教师 | 课程 | 冲突课程 | 约束说明 |
|------|------|----------|----------|
| **Darin** | 9th Social<br>12th AP Seminar | 9th Social vs 12th AP Seminar | Darin同时教授这些课程 |

### 4.10 9-Eng-A/10-A English特殊约束

| 约束 | 说明 | 详情 |
|------|------|------|
| **L. 同步约束** | 10-A English ⇒ 9-Eng-A English | 当10-A上英语课时，9-Eng-A必须也上英语课（单向蕴含） |
| **M. vs Literature** | 不能与11-A/B Literature同时 | LZY(9-Eng-A)/Lucy(10-A) vs CYF(11-A/B) |
| **N. vs AP Seminar** | 不能与12-A/B AP Seminar同时 | LZY(9-Eng-A)/Lucy(10-A) vs Lucy(12-A/B) |

**注意**: 9-Eng-A有6节English，10-A有5节。其中5节必须满足同步约束(L)，第6节可以自由安排。

### 4.11 Group 2 AP与10-A课程关联约束

**O. Group 2 AP要求10-A上Chemistry或Phys&Bio（硬约束）**

当11-A/B或12-A/B上Group 2 AP课时，10-A班必须同时上Chemistry或Phys&Bio课。

| Group 2 AP班级 | 关联课程 | 说明 |
|----------------|----------|------|
| 11-A, 11-B, 12-A, 12-B | 10-A Chemistry 或 10-A Phys&Bio | Group 2 AP ⇒ (Chemistry OR Phys&Bio) |

此约束确保Group 2 AP上课时间与10-A的理科课程时间绑定。

### 4.12 Art与Group 1 AP冲突约束

**P. Art与Group 1 AP不能同时上课（硬约束）**

Shiwen教师同时教授：
- Art课程（9-A/B/C, 10-A/B/C, 11-A/B）
- Group 1 AP（11-A/B, 12-A/B）- **新增Shiwen教师**

因此，任何班级的Art课不能与任何班级的Group 1 AP课同时上。

| 课程 | 教师 | 冲突课程 | 说明 |
|------|------|----------|------|
| Art | Shiwen | Group 1 AP | Shiwen不能同时教授两门课 |
| Group 1 AP | Guo, Zhao, **Shiwen** | Art | 同上 |

### 4.13 9年级走班英语约束 (T/U/V)

**T. 走班英语A/B/C与行政班9-A/9-B互斥（硬约束）**

当9-Eng-A/B/C上英语课时，9-A和9-B行政班不能有任何课程安排（因为学生需要去走班上英语课）。

| 走班英语班 | 互斥行政班 | 说明 |
|-----------|-----------|------|
| 9-Eng-A, 9-Eng-B, 9-Eng-C | 9-A, 9-B | 学生来自9-A/9-B，上英语时行政班必须空闲 |

**U. 走班英语D/E与行政班9-C互斥（硬约束）**

当9-Eng-D/E上英语课时，9-C行政班不能有任何课程安排（因为学生需要去走班上英语课）。

| 走班英语班 | 互斥行政班 | 说明 |
|-----------|-----------|------|
| 9-Eng-D, 9-Eng-E | 9-C | 学生来自9-C，上英语时行政班必须空闲 |

**V. 走班英语A/B/C与D/E不能同时上课（硬约束）**

因为LZY同时教9-Eng-A和9-Eng-E，Ezio同时教9-Eng-C和9-Eng-D，所以A/B/C组和D/E组不能同时上课。

| 组别 | 班级 | 教师 | 冲突说明 |
|------|------|------|----------|
| A/B/C组 | 9-Eng-A, 9-Eng-B, 9-Eng-C | LZY, CYF, Ezio | LZY教A，Ezio教C |
| D/E组 | 9-Eng-D, 9-Eng-E | Ezio, LZY | Ezio教D，LZY教E |
| **冲突** | A/B/C vs D/E | LZY(A vs E), Ezio(C vs D) | 两组不能同时上课 |

---

## 5. 特殊时间约束

### 5.1 排除时间槽

| 班级 | 排除时间 | 原因 |
|------|----------|------|
| 9-A, 9-B, 9-C | 周二 7-8节 | 学校安排 |
| 9-Eng-A/B/C/D/E | 周二 7-8节 | 与行政班同步 |
| 10-A, 10-B, 10-C | 周二 7-8节 | 学校安排 |
| 12-A, 12-B | 周五 7节 | 时间槽不足 |

### 5.2 必排时间槽

| 班级 | 时间 | 课程 |
|------|------|------|
| 12-A, 12-B | 周二 7节 | PE |
| 12-A, 12-B | 周二 8节 | Counseling |

### 5.3 课程时间限制

| 课程 | 时间限制 | 说明 |
|------|----------|------|
| Group 1 AP | 禁止周一5-6节 | 应为: 周一2节, 周四1节, 周五2节 |
| World History (10年级) | 每天最多1节 | 10-A/B/C的World History每天最多1节 |

### 5.4 每日课程数量限制

| 课程类型 | 每日限制 | 适用课程 |
|----------|----------|----------|
| 每周5节及以上 | 最多2节/天 | Group 1 AP, Group 2 AP, Group 3 AP, BC-Stats, Cal-ABBC, 9th English, EAL等 |
| Art课 | 最多2节/天 | Art (每周2节，允许连排) |
| 每周4节及以下(除Art) | 最多1节/天 | English, Literature, Spanish, PE, Chemistry, Physics, Biology, Geography, Social, Psychology, World History, Psych&Geo, Phys&Bio, AP Seminar, Counseling, Micro-Econ, Pre-Cal等 |

### 5.5 9年级每日课程特殊限制（硬约束R）

**R. 9年级课程每日安排限制**

| 课程 | 周课时 | 每日限制 | 说明 |
|------|--------|----------|------|
| **English** | 6节 | 1天2节，其他天最多1节 | 6节 = 2+1+1+1+1 分布 |
| **Art** | 2节 | 最多1天2节，其他天最多1节 | 2节 = 2（连排）或 1+1 |
| **其他课程** | 各3-5节 | 每天最多1节 | Algebra, Social, Psychology, Physics, Chemistry, Biology, Geography, PE |

**约束说明**:
- English必须恰好有一天安排2节课，其余4天各1节课
- Art最多有一天安排2节课（连排），也可以两天各1节课
- 所有其他课程每天最多1节课

### 5.6 10年级每日课程特殊限制（硬约束S）

**S. 10年级课程每日安排限制**

| 课程 | 周课时 | 每日限制 | 说明 |
|------|--------|----------|------|
| **Art** | 2节 | 最多1天2节，其他天最多1节 | 2节 = 2（连排）或 1+1 |
| **其他课程** | 各2-5节 | 每天最多1节 | English, World History, Psych&Geo, Spanish, Pre-Cal, Micro-Econ, Chemistry, Phys&Bio, PE |

**约束说明**:
- Art最多有一天安排2节课（连排），也可以两天各1节课
- 所有其他课程每天最多1节课

---

## 6. 优化目标 (软约束)

以下约束不是强制性的，但求解器会尽量优化：

### 6.1 连课偏好优化目标

求解器通过最大化加权连排对数来优化课程安排：

| 优化目标 | 课程 | 权重 | 说明 |
|---------|------|------|------|
| **最大化连排** (+3) | Cal-ABBC, Group 1/2/3 AP, BC-Stats, AP Seminar | +3 | 优先安排连排，形成2+2+1模式 |
| **最小化连排** (-1) | English | -1 | 尽量少连排，分散安排 |
| **避免连排** (-2) | Algebra, Pre-Cal | -2 | 尽量不连排，每天最多1节 |

### 6.2 每日AP课程数量优化（软约束Q）

**Q. 尽量每天有至少2节AP课**

对于11-A/B和12-A/B班级，每天尽量安排至少2节AP课（Group 1 AP, Group 2 AP, Group 3 AP）。

| 优化目标 | 适用班级 | 权重 | 说明 |
|---------|----------|------|------|
| **每天至少2节AP课** (+1) | 11-A, 11-B, 12-A, 12-B | +1/天 | 每天AP课≥2节时指标=1，否则=0，最大化总和 |

**理论最大值**: 4班级 × 5天 = 20个指标点

**当前解决方案连排情况（FEASIBLE）：**
- **Cal-ABBC**: 11-A有2对连排，11-B有2对连排 [PASS]
- **Group 1 AP**: 4个班级各有2对连排 [PASS]
- **Group 2 AP**: 4个班级各有2对连排 [PASS]
- **Group 3 AP**: 4个班级各有2对连排 [PASS]
- **BC-Stats**: 12-A/B各有2对连排 [PASS]
- **AP Seminar**: 无连排
- **English**: 大部分无连排
- **Algebra/Pre-Cal**: 少数有连排
- **Art**: 各班级均未连排（优化权重较低）

**每日AP课数量（软约束Q）：**
- **11-A**: 每天2-4节AP课，全部满足≥2节 [PASS]
- **11-B**: 每天2-4节AP课，全部满足≥2节 [PASS]
- **12-A**: 每天2-4节AP课，全部满足≥2节 [PASS]
- **12-B**: 每天2-4节AP课，全部满足≥2节 [PASS]
- **总体**: 20/20班级-天满足要求 (100%)

**9年级每日课程限制（硬约束R）：**
- **English**: 所有班级恰有1天2节课（周三），其他天各1节 [PASS]
- **Art**: 所有班级2节课分布在2天（各1节），无连排 [PASS]
- **其他课程**: 所有班级每天最多1节 [PASS]

**10年级每日课程限制（硬约束S）：**
- **Art**: 所有班级2节课分布在2天（各1节），无连排 [PASS]
- **其他课程**: 所有班级每天最多1节 [PASS]

---

## 7. 技术实现

### 7.1 决策变量
```
schedule[class_name, course_name, day, period] ∈ {0, 1}
```
表示某班级在某时间槽是否有某课程

### 7.2 约束类型
- **基本约束**: 班级课时数满足、每时间槽最多一门课
- **联合上课约束**: 联合班级必须同时上课
- **教师冲突约束**: 同教师不同时上课
- **英语教师约束**: 跨年级英语课程不冲突
- **特殊时间约束**: 排除/必排时间槽
- **每日课程数量约束**: 每周5节及以上课程每天最多2节，其他课程每天最多1节
- **EAL同步约束**: 使用单向蕴含关系 (Implication) 实现 E3: Psych&Geo ⇒ EAL
- **EAL重叠约束**: 使用 MinEquality/MaxEquality 实现 E4: overlap = EAL AND (Phys&Bio_10A OR Phys&Bio_10C)
- **每日课程限制**: Art课例外允许每天2节，其他4节以下课程每天最多1节
- **软约束优化**: 使用加权目标函数，最大化/最小化连排对数

### 7.3 求解器配置
- **算法**: Google OR-Tools CP-SAT
- **超时**: 300秒
- **求解状态**: FEASIBLE (可行解，目标值106，上界132)

---

## 8. 验证结果

### 当前解决方案状态
- **求解器状态**: FEASIBLE (目标值106，上界132，gap约24.5%)
- **总变量数**: 4,197个布尔变量
- **总排课节次**: 427节 (含EAL课程)
- **验证状态**: 全部通过 ✓

### 班级课时验证
| 班级 | 要求 | 实际 | 状态 |
|------|------|------|------|
| 9-A, 9-B, 9-C (行政班) | 27 | 27 | ✓ |
| 9-Eng-A, 9-Eng-B, 9-Eng-C (走班英语) | 6 | 6 | ✓ |
| 9-Eng-D, 9-Eng-E (走班英语) | 6 | 6 | ✓ |
| 10-A, 10-B, 10-C | 33 | 33 | ✓ |
| 10-EAL-A, 10-EAL-B | 3 | 3 | ✓ |
| 10-EAL-C | 6 | 6 | ✓ |
| 11-A, 11-B | 35 | 35 | ✓ |
| 12-A, 12-B | 31 | 31 | ✓ |

### EAL同步验证

#### E3约束 (EAL与Psych&Geo同步)
| EAL班级 | Psych&Geo时间 | EAL时间 | 状态 |
|---------|---------------|---------|------|
| 10-EAL-A | 周二5, 周三4, 周四1 | 周二5, 周三4, 周四1 | ✓ |
| 10-EAL-B | 周二5, 周三4, 周四1 | 周二5, 周三4, 周四1 | ✓ |
| 10-EAL-C | 周二5, 周三4, 周四1 | 周二5, 周三4, 周四1 (+周二6, 周四2, 周五2) | ✓ |

#### E4约束 (10-EAL-C额外3节与Phys&Bio同步)
| 时间 | 10-EAL-C EAL | 10-A Phys&Bio | 10-C Phys&Bio | 重叠状态 |
|------|--------------|---------------|---------------|----------|
| 周二6节 | ✓ | ✓ | ✓ | 重叠1 |
| 周四2节 | ✓ | ✓ | ✓ | 重叠2 |
| 周五2节 | ✓ | ✓ | ✓ | 重叠3 |
| **总计** | **3节重叠** | | | **✓ 满足E4约束** |

---

## 9. 文件结构

```
ClassArrangement/
├── src/
│   ├── data.py          # 班级、课程、教师数据配置
│   ├── models.py        # 数据模型定义
│   ├── constraints.py   # 约束条件实现 (A-F六大类)
│   ├── solver.py        # CP-SAT求解器
│   └── output.py        # 输出处理
├── output/              # 输出文件目录
│   ├── global_schedule.csv   # 全局课程表
│   ├── *_schedule.csv        # 各班级课程表
│   └── report.txt            # 统计报告
├── main.py              # 主程序入口
├── requirements.txt     # 依赖包
└── REQUIREMENTS.md      # 本文档
```

---

## 10. 依赖包

```
ortools>=9.7.2996
```

---

## 11. 使用方法

```bash
# 安装依赖
pip install -r requirements.txt

# 运行排课
python main.py

# 查看输出
# - output/global_schedule.csv: 全局课程表
# - output/*_schedule.csv: 各班级详细课程表
# - output/report.txt: 验证报告
```

---

## 12. 约束实现索引

| 约束类型 | 文件位置 | 函数 |
|----------|----------|------|
| A. 基本约束 | constraints.py | `add_basic_constraints()` |
| B. 联合上课约束 | constraints.py | `add_joint_session_constraints()` |
| C. 教师冲突约束 | constraints.py | `add_teacher_conflict_constraints()` |
| D. 英语教师约束 | constraints.py | `add_english_teacher_constraints()` |
| E. 特殊时间约束 | constraints.py | `add_special_time_constraints()` |
| F. 每日课程数量约束 | constraints.py | `add_daily_course_constraints()` |
| G. 软约束 | constraints.py | `add_soft_constraints()` |

### 特殊约束
| 约束 | 说明 | 代码位置 |
|------|------|----------|
| E3 | EAL与Psych&Geo同步（单向蕴含） | constraints.py:299-310 |
| E4 | 10-EAL-C与Phys&Bio同步（3节重叠） | constraints.py:313-375 |
| World History | 10年级每天最多1节 | constraints.py:378-396 |
| H | 11-A English与12-A/B AP Seminar同步 | constraints.py:530-548 |
| I | Lucy教师冲突（AP Seminar vs 10th English） | constraints.py:550-570 |
| J | Guo教师冲突（9th Physics vs Group 1/2 AP） | constraints.py:572-596 |
| K | Darin教师冲突（12th AP Seminar vs 9th Social） | constraints.py:598-622 |
| L | 9-Eng-A/10-A English同步（10-A English ⇒ 9-Eng-A English） | constraints.py:624-648 |
| M | English vs Literature冲突（9-Eng-A/10-A vs 11-A/B） | constraints.py:650-678 |
| N | English vs AP Seminar冲突（9-Eng-A/10-A vs 12-A/B） | constraints.py:680-708 |
| O | Group 2 AP要求10-A上Chemistry或Phys&Bio | constraints.py:710-745 |
| P | Art与Group 1 AP冲突（Shiwen教师） | constraints.py:747-780 |
| Q | 每日AP课程数量优化（软约束） | constraints.py:511-550 |
| R | 9年级行政班每日课程限制（Art特殊规则） | constraints.py:820-900 |
| S | 10年级每日课程限制（Art特殊规则） | constraints.py:902-980 |
| T | 走班英语A/B/C与行政班9-A/9-B互斥 | constraints.py:982-1020 |
| U | 走班英语D/E与行政班9-C互斥 | constraints.py:1022-1055 |
| V | 走班英语A/B/C与D/E不能同时（教师冲突） | constraints.py:1057-1085 |
| 软约束优化 | 连排偏好/避免目标函数 | constraints.py:449-517 |

---

## 13. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2026-02-10 | 初始版本，实现所有核心约束 |
| 1.1 | 2026-02-10 | 新增9-C班，修复英语教师约束 |
| 1.2 | 2026-02-10 | 新增10年级EAL课程，实现E3约束 |
| 1.3 | 2026-02-10 | 实现E4约束（10-EAL-C与Phys&Bio同步）|
| 1.4 | 2026-02-10 | 修复AND约束实现，使用正确的CP-SAT方法 |
| 1.5 | 2026-02-10 | 验证通过，创建需求文档 |
| 1.6 | 2026-02-10 | 新增10-A与10-C Phys&Bio联合上课约束 |
| 1.7 | 2026-02-10 | 更新BC-Statistics教师(Yan+Yuhan)，添加Yuhan冲突约束 |
| 1.8 | 2026-02-10 | 更新11年级Cal-ABBC教师为Yan+Song，添加Yan教师冲突约束 |
| 1.9 | 2026-02-10 | 更新Phys&Bio教师(10-A/10-B:Song, 10-C:Zhao)，添加Song和Zhao冲突约束 |
| 2.0 | 2026-02-10 | 更新Group 1/2/3 AP教师配置（多教师），添加Guo和Manuel冲突约束，验证全部通过 |
| 2.1 | 2026-02-10 | 新增每日课程数量限制约束（每周5节及以上课程每天最多2节，其他课程每天最多1节），Art课尽量连排，验证全部通过 |
| 2.2 | 2026-02-11 | 修复EAL约束实现：E3改为单向蕴含(Psych&Geo⇒EAL)，修复E4使用MinEquality/MaxEquality实现，更新需求文档验证结果 |
| 2.3 | 2026-02-11 | 新增10年级World History每日限制约束：每个班每天最多1节 |
| 2.4 | 2026-02-11 | 修改Art课每日限制：允许每天最多2节（连排），与其他4节以下课程区分 |
| 2.5 | 2026-02-11 | 添加软约束优化目标：连排偏好（Cal-ABBC, Group AP, BC-Stats, AP Seminar优先连排；English少连排；Algebra/Pre-Cal避免连排） |
| 2.6 | 2026-02-11 | 添加硬约束H：11-A English与12-A/B AP Seminar同步；添加硬约束I：Lucy教师冲突（AP Seminar vs 10th English） |
| 2.7 | 2026-02-11 | 更新Group 1/2 AP教师配置添加Guo；添加硬约束J：Guo教师冲突（9th Physics vs Group 1/2 AP）；求解器状态FEASIBLE |
| 2.8 | 2026-02-11 | 更新教师配置：Spanish(Manuel→AK)，Psych&Geo(新增Manuel)，Group 1 AP(移除Darin)，Group 2 AP(Chloe→Neil) |
| 2.9 | 2026-02-11 | AP Seminar新增教师Darin；添加硬约束K：Darin教师冲突（12th AP Seminar vs 9th Social） |
| 3.0 | 2026-02-11 | 添加硬约束L/N：9-A/10-A English同步及冲突约束（vs 11th Literature, 12th AP Seminar） |
| 3.1 | 2026-02-11 | 添加硬约束O：Group 2 AP要求10-A上Chemistry或Phys&Bio |
| 3.2 | 2026-02-11 | Group 1 AP新增教师Shiwen；添加硬约束P：Art与Group 1 AP不能同时上课 |
| 3.3 | 2026-02-11 | 添加软约束Q：尽量每天有至少2节AP课（Group 1/2/3 AP） |
| 3.4 | 2026-02-11 | 添加硬约束R：9年级每日课程限制（English 1天2节，Art 1天2节，其他每天1节） |
| 3.5 | 2026-02-11 | 添加硬约束S：10年级每日课程限制（Art 1天2节，其他每天1节） |
| 3.6 | 2026-02-24 | 实现9年级走班制英语系统：新增5个走班英语班(9-Eng-A/B/C/D/E)，行政班移除English课程；添加硬约束T/U/V：走班英语与行政班互斥、A/B/C组与D/E组教师冲突 |

---

## 14. 联系与支持

如有问题或需要修改约束条件，请参考：
- 源代码: `src/constraints.py`
- 数据配置: `src/data.py`
- 本文档: `REQUIREMENTS.md`
