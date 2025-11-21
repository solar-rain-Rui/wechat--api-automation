
# 企业微信接口自动化测试项目

本项目基于 **Python + Pytest + Requests + Allure + Mysql**构建企业微信接口自动化测试框架。
支持部门、用户、标签等模块的自动化测试，包括数据驱动、fixture 管理、业务流测试、冒烟测试、日志收集，以及测试数据的自动准备和清理。

项目主要用于练习接口自动化框架设计和提升测试工程能力。

---

##  功能特点

* **接口封装**：统一 BaseApi 封装 GET/POST 请求
* **YAML 数据驱动**：多模块的创建、查询、更新、删除用例全部支持
* **自定义断言**：支持 JSONPath 对关键字段断言、JSonschema对响应结构的验证
* **测试数据准备**：创建测试用例执行前，会自动创建对应的部门、用户或标签。
* **自动清理测试数据**：依据创建的 ID 或前缀清理（用户、标签、部门）
* **业务流测试**：模拟真实使用场景进行 end-to-end 测试
* **详细日志输出**：每次请求和响应都会记录
* **Allure 报告生成**：带有 feature / story / step 的可视化报告

---

##  项目主代码结构（示例）

```bash
frame                               # 项目主代码目录（企业微信接口自动化测试框架）
├── apis                            # 接口层：封装企业微信各模块的 API
│   ├── base_api.py                 # 所有 API 的基类，统一封装请求 
│   ├── departments.py  
    ├── users.py
    ├── tags.py  
    ├── wowork.py                   #获取access_token
│
├── common                          # 通用工具层
│   ├── logger.py                   # 日志封装
│   ├── assertions.py               # 自定义断言
│   ├── tools.py                    
│   └── config.py                   # 配置读取模块（如 token、URL 配置等）
│
├── config
│   └── dev.yaml               # 全局配置文件，例如企业微信 corp_id、secret 等
│   └── prod.yaml  
    └── test_env.yaml
├── datas                           # 数据驱动目录（YAML 测试数据）
│   ├── departments.yaml            
│   ├── users.yaml                  
│   └── tags.yaml                   
│
├── logs                            # 日志输出
│   ├── run.log                               
│
├── schema                          # JSON Schema 校验目录
│   ├── department_schema.json      
│   ├── user_schema.json            
│   └── tag_schema.json             
│
├── setup
│   └── prepare_test_data.py                   # 测试前置操作(准备数据)
│
└── testcase                        # 测试用例层（pytest）
    ├── departments                 # 部门模块测试用例
    │   ├── test_department.py
    │   └── test_department_flow.py # 部门业务流测试（主流程）
    │
    ├── users                       # 用户模块测试用例
    │   ├── test_users.py
    │   └── test_user_flow.py       # 用户模块业务流测试
    │
    ├── tags                        # 标签模块测试用例
    │   ├── test_tags.py
    │   └── test_tag_flow.py        # 标签模块业务流测试
    │
    └── smoke                       # 冒烟用例
        └── test_smoke_main.py     # 主链路冒烟测试（部门→用户→标签）
    └── test_env_switch.py          #多环境切换

```
---

##  如何运行

### 1. 安装依赖：

```bash
pip install -r requirements.txt
```

---

### 2. 运行所有用例：

```bash
pytest
```
---

### 3. 使用 Allure 生成测试报告：

```bash
pytest --alluredir ./allure-results
allure generate ./allure-results -o ./allure-report --clean
allure open ./allure-report
```

---

##  Allure 报告示例


---

##  测试覆盖范围
本项目覆盖了企业微信通讯录相关接口的核心自动化测试，包括：
✔ 正常用例 + 异常用例（如重复创建、非法参数等）
✔ 全流程业务流 + 冒烟测试覆盖
### 部门模块

* 创建部门
* 更新部门
* 查询部门
* 删除部门
* 部门业务流（创建 → 更新 → 查询 → 删除）

### 用户模块

* 创建用户
* 更新用户
* 查询用户
* 删除用户
* 用户业务流（创建 → 更新 → 查询 → 删除）

### 标签模块

* 创建标签
* 更新标签名称
* 查询标签
* 删除标签
* 标签业务流（创建 → 更新 → 查询 → 删除）

### 冒烟测试（Smoke Test）

验证核心业务链路是否可用，包括：

* 核心部门 + 用户 + 标签 的关键功能组合验证
* 关键接口可用性检查
* 聚焦“主流程跑通”，保证系统的可基本使用性
---
##  数据准备&清理
* 测试数据准备：用例执行前自动创建所需部门、用户、标签，保证数据存在
* 测试数据清理：
    - 用户：通过创建时记录的 userid 自动删除
    - 部门：通过创建时记录的 department_id 自动删除
    - 标签：通过标签名前缀匹配自动删除
 支持重复执行，避免后台污染
---

##  版本信息

### v1.1.0（当前版本）

* 调整项目结构
* 增加部门/用户/标签完整业务流
* 增强日志和断言
* 完整集成 Allure 报告



