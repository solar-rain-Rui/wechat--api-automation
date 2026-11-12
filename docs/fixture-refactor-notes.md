# Fixture 与测试数据处理函数整理记录（fixture-refactor-notes）

> 分支：`refactor/general-api`
> 整理原则：只做轻量整理——抽取真正重复的骨架逻辑，保留各业务的独立实现，不引入工厂类/设计模式/新依赖，不改变任何对外行为。
> 本次修改仅涉及：fixture 所在文件（conftest.py）、直接相关的 6 个测试用例文件。未触碰 BaseApi / WeComApi / Token / 配置 / 日志 / 业务 API / 断言 / Schema 等任何其他模块。

---

## 一、修改文件清单

| 文件 | 修改类型 | 改动量 |
|---|---|---|
| `frame/testcase/conftest.py` | 重点重构 | 367 行变更，净减约 60 行 |
| `frame/testcase/users/test_users.py` | 同步调用方式 | 4 处 |
| `frame/testcase/users/test_user_flow.py` | 同步调用方式 | 1 处 |
| `frame/testcase/tags/test_tags.py` | 同步调用方式 | 7 处（tag 6 + user 1） |
| `frame/testcase/tags/test_tag_flow.py` | 同步调用方式 | 1 处 |
| `frame/testcase/workflow/test_dp_user_mg_workflow.py` | 同步调用方式 | 1 处 |
| `frame/testcase/workflow/test_abnormal_workflow.py` | 同步调用方式 | 2 处 |

## 二、修改前的问题

### 问题 1：三个占位符函数骨架重复

`replace_auto_placeholder` / `replace_auto_placeholder_user` / `replace_auto_placeholder_tag` 三个函数中，「深拷贝 → 生成 uuid → 遍历字典 → 识别 `${auto}` → 按字段替换 → 递归嵌套 → 移除待删字段」这套骨架**逐字重复了三遍**（约 80 行），只有中间的字段替换规则不同。新增一个业务模块就要再抄一遍骨架。

### 问题 2：三个 Factory Fixture 对外形态不一致

- `department_factory` 返回 `SimpleNamespace`，用 `factory.create(data)` 调用
- `user_factory` / `tag_factory` 直接 `yield _create` 裸函数，用 `factory(data)` 调用

同一个项目两套调用方式，使用者必须记住"部门要用 `.create`，用户和标签直接调用"这种毫无业务含义的区别。

### 问题 3：批量清理逻辑重复

三个 factory 的 yield 后置清理是同构的 try/except 循环，重复三遍，仅资源名不同。

### 问题 4：死代码与调试残留

- 文件尾部约 90 行被注释的旧版 session 级清理代码（引用早已废弃的 `CREATED_DEPT_IDS` 全局列表）
- `token` / `department_api` fixture 中的调试 print
- 未使用的 `load_yaml` 导入
- `tag_factory` 中 `if tagid == "${auto}" or tagid is None: tagid = None` 的无效分支（tagid 为 `"${auto}"` 时引擎已将其移除，get 得到 None；把 None 赋成 None 没有任何作用）

## 三、修改后的设计

### 3.1 占位符处理：一个引擎 + 三张规则表

```
_process_auto(data, rules, list_rules=None)   ← 公共引擎（约 45 行，只写一遍）
 ├── rules:     {字段名: 替换规则}   _REMOVE 标记 / 可调用对象 / 常量
 └── list_rules: {字段名: 替换值}    列表中 "${auto}" 元素的替换值（用户的 department 列表）

replace_auto_placeholder(data, root_dept_id=1)        → 部门规则表（name/parentid/id）
replace_auto_placeholder_user(data, root_dept_id=1)     → 用户规则表（userid/name/mobile/email/position + department 列表）
replace_auto_placeholder_tag(data)                     → 标签规则表（tagname/tagid）
```

三个业务函数从各约 60 行的重复实现，变成各 10~20 行的"规则表声明"。**函数名、参数签名、返回值、对外行为完全不变**——`test_departments.py` / `test_users.py` / `test_tags.py` 中对这三个函数的直接 import 调用无需任何改动。

设计取舍说明：
- 引擎支持三种规则形态（删除标记 / 回调函数 / 常量），是为了让"parentid 直接换成根部门 id"这种常量替换和"name 生成唯一名"这种动态生成能共存于一张表，不需要为每个字段写 if-elif。
- 未在规则表中定义的字段仍按原逻辑统一替换为 `auto_{uuid}`，保证引擎是原有行为的超集，不会因为"未知字段"而漏处理。
- 嵌套字典递归时引擎会重新生成 uuid（与原三个函数的递归行为一致），不做跨层级共享 id。

### 3.2 Factory Fixture：统一 SimpleNamespace 形态

```
改造前：
department_factory.create(data)      ← SimpleNamespace
user_factory(data)                   ← 裸函数
tag_factory(data)                    ← 裸函数

改造后：
department_factory.create(data)      ← SimpleNamespace（不变）
user_factory.create(data)            ← SimpleNamespace（新）
tag_factory.create(data)             ← SimpleNamespace（新）
```

统一后每个 factory 都暴露：
- `create(data)`：处理占位符 → 调接口 → 记录资源 id → 返回响应
- `created_ids`：本用例已创建的资源 id 列表（可直接断言/检查）

`get_created(index)` **只保留在 department_factory**——它有真实使用场景（`test_dp_user_mg_workflow.py` 需要用创建时的 name 做后续查询）。没有为了"形式完全一致"给 user/tag 添加无人调用的 `get_created`，避免出现无实际使用场景的接口。

**保留独立的业务差异**（未强行合并，原因：这三个流程的差异是真实的业务差异，不是重复）：
- department：id 从**响应体**中提取（`res.json().get("id")`），并保存完整创建数据供 name 查询
- user：id 是**本地生成后随请求提交**的（`processed["userid"]`），创建成功与否要检查 errcode
- tag：create 接口参数是 `tagname`/`tagid` 两个位置参数而非 json body，id 从**响应体**提取且要判断非空
- 响应对象上的 `created_userid` / `created_tagid` 属性机制原样保留（10+ 处测试代码依赖 `getattr(res, "created_userid")`）

### 3.3 批量清理：抽取 `_cleanup_created`

三个 factory 的 yield 清理段统一改为：

```python
yield factory
_cleanup_created(api.delete, created_ids, "部门")   # "用户" / "标签" 同理
```

单条清理失败不影响其余清理、失败记 warning 的行为与原实现完全一致。

### 3.4 清理项

删除了文件尾部约 90 行注释掉的旧清理方案、`token`/`department_api` 中的调试 print、未使用的 `load_yaml` 导入、tag_factory 的无效 if 分支。

## 四、为什么这样修改

1. **抽取的是"完全相同的骨架"，保留的是"真正不同的业务"**——这是本次整理唯一的判断标准。三个占位符函数的遍历/深拷贝/递归/移除逻辑逐字相同，是纯粹的重复；三个 factory 的 id 提取方式各不相同，是业务事实，合并它们需要引入回调参数化的通用工厂——那就是过度抽象，初学者讲解时也讲不清楚。
2. **统一调用方式比统一返回结构更重要**——`.create()` 的语义（"工厂的创建动作"）在三个业务上完全对齐后，测试代码的阅读负担消失了；而 `created_userid` 这类响应属性机制虽然没有 get_created 优雅，但它工作正常且被 10+ 处依赖，为改而改只会引入回归风险。
3. **`_cleanup_created` 是本次最典型的"适度抽取"**——8 行函数消掉 3 段同构代码，任何人 10 秒能看懂。

## 五、修改前后的调用方式对比

```python
# ===== 占位符处理（对外完全不变）=====
from frame.testcase.conftest import replace_auto_placeholder_user
data = replace_auto_placeholder_user(case["data"])        # 改造前后一致

# ===== 部门 factory（不变）=====
res = department_factory.create(case["data"])
dept_info = department_factory.get_created(0)

# ===== 用户 factory（改造前）=====
res = user_factory({
    "userid": "${auto}", "name": "${auto}",
    "mobile": "${auto}", "department": [1],
})
userid = getattr(res, "created_userid")

# ===== 用户 factory（改造后：仅加 .create）=====
res = user_factory.create({
    "userid": "${auto}", "name": "${auto}",
    "mobile": "${auto}", "department": [1],
})
userid = getattr(res, "created_userid")   # 属性机制不变

# ===== 标签 factory（改造前）=====
res = tag_factory({"tagname": "${auto}"})
# ===== 标签 factory（改造后）=====
res = tag_factory.create({"tagname": "${auto}"})
```

## 六、发现的遗留问题（本次保留原行为，如实记录）

1. **mobile 生成的注释与实现不一致**：原代码注释写"8 位，加上 138 共 11 位"，但 `random.randint(100000000, 999999999)` 实际生成 9 位数，拼上 138 后是 12 位。本次整理**忠实保留了原实现**（12 位），未修改行为——因为当前所有真实接口用例因 IP 白名单（60020）无法在本机验证，改动手机号格式属不可验证的行为变更。后续在可验证环境确认企微是否接受 12 位手机号后，应将范围改为 8 位数（`randint(10000000, 99999999)`）。
2. department_factory 创建失败（无 id 返回）时不检查 errcode，静默不记录——行为上无害（清理只处理成功创建的资源），保留原状。

## 七、验证方法与实际结果

### 7.1 占位符函数行为验证（新增引擎与原实现等价性）

用代表性输入直接调用三个函数断言输出（部门：name 唯一化/parentid 根部门/id 移除；用户：五字段规则 + department 列表替换 + 嵌套 dict 递归；标签：tagname/tagid），并验证**原始数据未被修改**（深拷贝生效）：

```
部门 OK: {'name': 'test_部门_ec562e4d', 'parentid': 1, 'extra': 'auto_ec562e4d'}
用户 OK: {..., 'mobile': '138850637936', 'department': [5, 2], 'nested': {...}}
标签 OK: {'tagname': 'test_标签_698d2108'}
=== 三个占位符处理函数行为验证全部通过 ===
```

### 7.2 全量回归（与基线逐项对比）

| 指标 | 改造前基线 | 改造后 |
|---|---|---|
| 总体 | 126 failed, 22 passed | **126 failed, 22 passed** |
| departments 失败分布 | 30（flow 1 + 单接口 29） | 30（完全一致） |
| users 失败分布 | 46（flow 1 + 单接口 45） | 46（完全一致） |
| tags 失败分布 | 46（flow 1 + 单接口 45） | 46（完全一致） |
| workflow 失败分布 | 4（abnormal 3 + dp 1） | 4（完全一致） |
| 通过用例 | 22（mock 消息 7 + 环境切换 1 + 单元测试 14） | 22（无丢失） |

126 条失败全部仍是 errcode 60020（企业微信应用 IP 白名单限制，环境问题），失败原因与失败集合和基线完全一致——**本次整理未改变任何测试行为**，无新增失败、无丢失通过。

### 7.3 无法本机验证的说明

真实接口用例（departments/users/tags/workflow 共 124 条 + 消息部分场景）因 IP 白名单无法在本机跑通，本次通过「失败集合逐文件比对 + 占位符函数直接断言 + mock 用例全通过」三重方式验证等价性。

## 八、面试时如何解释这些设计

1. **"三个占位符函数你怎么去重的？"**
   "我只抽了完全一样的骨架——深拷贝、递归遍历、`${auto}` 识别、待删字段收集——做成一个 `_process_auto` 引擎；每个业务只剩一张规则表。关键是判断标准：骨架相同才抽，字段规则是业务差异，保留在各自函数里，所以三个函数名和签名都没变，测试代码零感知。"
2. **"为什么 factory 不做成一个通用工厂类？"**
   "三个 factory 真正重复的只有清理循环，我抽了 8 行的 `_cleanup_created`；但 id 的提取方式三个业务完全不同——部门从响应取、用户本地生成随请求提交、标签接口是位置参数——合并它们需要回调参数化，可读性反而下降。'发现重复'和'克制地合并'同样重要。"
3. **"为什么不把 created_userid 这种响应属性也统一成 get_created？"**
   "它被十几处 getattr 依赖，工作正常。重构的第一原则是不引入回归风险——收益是形式统一，风险是全量改测试代码，这笔账不划算。我在文档里记录了它，留给有真实验证环境的时机再动。"
4. **"你怎么证明这次整理没改坏东西？"**
   "三步：改造前先跑基线并记录失败分布；改造后全量回归，126 个失败逐文件比对，集合完全一致（都是 IP 白名单的环境问题）；另外对三个占位符函数用代表性输入直接断言输出和'原始数据未被修改'，这是能脱离真实环境做的最严格验证。"
5. **"发现的 mobile 12 位问题你为什么不顺手修掉？"**
   "因为修了没法验证——所有真实接口被 IP 白名单挡着。不可验证的行为变更宁可不动、如实记录。这是重构的纪律问题，不是能力问题。"

---

## 附：Git diff 统计

```
 frame/testcase/conftest.py                         | 367 +++++++++------------
 frame/testcase/tags/test_tag_flow.py               |   2 +-
 frame/testcase/tags/test_tags.py                   |  14 +-
 frame/testcase/users/test_user_flow.py             |   2 +-
 frame/testcase/users/test_users.py                 |   8 +-
 frame/testcase/workflow/test_abnormal_workflow.py  |   4 +-
 frame/testcase/workflow/test_dp_user_mg_workflow.py|   2 +-
 7 files changed, 170 insertions(+), 229 deletions(-)
```
