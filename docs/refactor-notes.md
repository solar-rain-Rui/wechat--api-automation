# 通用化改造记录（refactor-notes）

> 改造分支：`refactor/general-api`
> 改造原则：不推倒重写，在现有三层架构（apis / common / testcase）基础上做有明确目的的通用化解耦。
> 所有测试验证均在本机完成，验证结果如实记录（含无法验证的部分）。

---

## 一、核心改造：继承链与调用关系

### 改造前

```
BaseApi（通用 HTTP + 企业微信 Token 逻辑混在一起）
 ├── 直接 import frame.common.token_get.fetch_token（基类反向依赖具体业务）
 ├── 硬编码企业微信错误码 40014 / 42001
 ├── 硬编码 access_token 参数名
 └── Departments / Users / Tags / MessageApi 全部继承它
```

问题本质：**BaseApi 名为"通用基类"，实为"企业微信基类"**。想拿它去测任何非企微系统，都会连带引入企业微信的 token 模块与错误码。

### 改造后

```
BaseApi（纯通用 HTTP：发请求、记日志、返回原始 Response）
   └── WeComApi（企业微信专属：errcode 失效判断 + 刷新 + 重试一次 + 回写实例）
         ├── Departments
         ├── Users
         ├── Tags
         └── MessageApi
```

- BaseApi 对企业微信**零感知**（有单元测试 `test_base_api_has_no_wecom_dependency` 做源码级守护）
- 企业微信的所有鉴权细节收敛到 `WeComApi` + `token_get.py` 两个文件中
- 依赖方向修正：改造前是「基类 → 企微模块」的下沉耦合，改造后是「企微子类 → 企微模块」的平级引用

### 核心调用流程对比

改造前：

```
Departments.create(data)
 └─ BaseApi.send_api(req)
     ├─ requests.request(**req)
     ├─ r.json().get("errcode") in [40014, 42001]   ← 企微逻辑长在通用基类
     └─ fetch_token() → 注入 req["params"] → 重发   ← 新 token 不回写、请求字典被原地修改
```

改造后：

```
Departments.create(data)
 └─ WeComApi.send_api(req)
     ├─ super().send_api(req)          ← 通用层：记日志（URL 脱敏）+ 发请求
     ├─ _is_token_expired(r)            ← 响应非 JSON / 非字典时安全跳过
     └─ 命中失效码时：
         ├─ fetch_token(force=True)     ← 强制刷新（模块级缓存）
         ├─ self.token = new_token      ← 回写实例，后续请求直接用新 token
         └─ copy.deepcopy(req) → 注入新 token → super().send_api() 重试一次
```

---

## 二、修改明细表

| 修改文件 | 修改前的问题 | 修改后的设计 | 修改原因 | 面试可以怎么解释 |
|---|---|---|---|---|
| `frame/apis/base_api.py`（调整） | 企微错误码 40014/42001、fetch_token 导入、access_token 参数名硬编码在"通用基类"；无条件 `r.json()` 假定响应必为 JSON | 只保留：记请求日志（URL 脱敏）→ `requests.request` → 记响应日志 → 返回原始 Response；新增 `_mask_url()` 脱敏函数 | 职责分离的核心：通用层不应知道任何业务；非 JSON 响应（网关 502 HTML 页等）不再崩溃 | "我把模板方法反过来用了：父类只提供最稳定的 HTTP 发送能力，认证这种易变逻辑下放到子类扩展点里" |
| `frame/apis/weixin_base.py`（**新增**） | 不存在，企微逻辑只能长在 BaseApi 里 | `WeComApi(BaseApi)`：类属性 `TOKEN_EXPIRED_CODES = {40014, 42001}`；`send_api()` 中先走通用层，响应失效时强制刷新、回写 `self.token`、`copy.deepcopy(req)` 后重试一次 | 一层简单继承即可完成解耦，无需插件系统；重试用 `super().send_api()` 保证代理配置、日志行为与原请求完全一致 | "失效判断做成类属性而非 if-else 硬编码，换失效码只改一行配置；deepcopy 防止重试污染调用方的原始字典" |
| `frame/common/token_get.py`（调整） | 无缓存：4 个 session 级 API 实例各自失效时都会真实请求一次 gettoken | 模块级 `_token_cache` + `fetch_token(force=False)`；失效重试传 `force=True` | 多实例共享 token，失效事件只应触发一次真实刷新，其余实例直接命中缓存 | "用模块级缓存解决多实例重复刷新问题，force 参数区分'首次获取'和'失效后强制刷新'两种语义" |
| `frame/apis/contacts/departments.py`（调整，保留已有 base_url 改动） | ① token 拼 URL（`?access_token=`），刷新重试会与 params 注入冲突；② `log.info` 明文打印 token | 全部接口 token 统一走 `params`；`get()` 将查询参数与 token 合并进 params；删除 token 打印日志 | 统一传参后重试逻辑才有唯一注入点；token 明文进日志是安全隐患 | "URL 拼接和 params 传递对服务端等价，但只有统一为 params，token 刷新替换才有唯一注入点——这是重试逻辑正确性的前提" |
| `frame/apis/contacts/users.py`（调整，保留已有 base_url 改动） | `create` 拼 URL 传 token；残留调试 `print(">>> 创建用户请求体")` | token 走 params；删除调试 print | 与其他模块传参统一；调试残留不应留在接口层 | "清理调试代码也是重构的一部分，接口层应该只留业务请求构造" |
| `frame/apis/contacts/tags.py`（调整，保留已有 base_url 改动） | 模块级 `print(">>> LOADING Tags...")` 在 import 时执行；继承 BaseApi | 删除模块级 print；改继承 WeComApi | import 副作用会污染所有加载方输出；继承链对齐 | "import 时的 print 是典型的模块副作用问题，pytest 收集阶段就会触发" |
| `frame/apis/message/message.py`（调整） | real 分支 token 拼 URL；继承 BaseApi | token 走 params；继承 WeComApi | 传参统一 + 继承链对齐（mock 分支在 send_api 之前返回，不受影响） | "mock 分支不经过 send_api，说明解耦改造对 mock 路径零影响——这也是改造安全性的一个佐证" |
| `frame/common/config.py`（调整） | ① `Config.cf = 新实例` 的切换方式无效：消费方 `from ... import cf` 持有旧实例引用；② 密钥只能写死在 yaml | ① 新增 `reload(env)` 原地替换 `self.data`，所有持有 cf 引用的模块立即生效；② `_apply_sensitive_overrides()` 支持从环境变量 `WECOM_CORPID` / `WECOM_CORPSECRET` 读取并覆盖 yaml 值；③ 内置 10 行 `_load_dotenv()` 极简 .env 加载器（不引入 python-dotenv 依赖），系统环境变量优先于 .env 文件 | 实例引用断裂是真实 bug（`--env dev` 切换失效）；密钥不落盘是安全刚需 | "Python 的 `from x import y` 是值绑定不是名字引用，重新赋值模块属性改变不了已导入的绑定——所以我改成原地 reload 同一个实例，所有引用自然生效" |
| `conftest.py`（根目录，调整） | `Config.cf = Config(f"{env}.yaml")` 环境切换失效 | `cf.reload(env)` 原地重载 | 同上，这是环境切换 bug 的调用侧修复 | "bug 在赋值方式，修复在调用方式，两头对齐才能闭环" |
| `frame/config/*.yaml`（3 个，调整） | 明文真实 corpid/corpsecret 已提交到 Git 并推送到 GitHub 远程 | 全部替换为 `REPLACE_WITH_YOUR_CORPID` 占位符；真实值迁移到本地 `.env`（已被 Git 忽略） | 密钥入库是最高优先级安全问题 | "密钥治理分三步：入库的改占位符、真实的放本地 .env、CI 用仓库 Secrets 注入环境变量。因为历史提交里仍能看到旧密钥，必须去企微后台轮换" |
| `.env.example`（**新增**） | 不存在 | 标准示例文件，说明 WECOM_CORPID / WECOM_CORPSECRET 两个变量与优先级规则 | 团队协作规范：别人拿到代码知道要配什么 | "example 文件是配置项的'接口文档'" |
| `.gitignore`（调整） | 只忽略 `.idea/`、`__pycache__`、`*.pyc`；logs、allure 产物、.pytest_cache 全部入库 | 补充 `.env`、`logs/`、`*.log`、`allure-results/`、`allure-report/`、`.pytest_cache/` | 测试产物与日志（含 token 明文）不应入库 | "gitignore 是仓库安全的第一道闸门，日志文件里 876 处 access_token 明文就是教训" |
| `frame/logs/api_object.log`（取消跟踪） | 已被 Git 跟径跟踪，文件含 token 明文 | `git rm --cached` 移出索引，本地文件保留 | 敏感内容继续留在仓库里等于泄露持续存在 | "gitignore 只对未跟踪文件生效，已跟踪文件必须先 rm --cached" |
| `frame/testcase/test_env_switch.py`（调整） | `print(cf.data)` 将含密钥的全量配置打到终端与 CI 日志 | 只打印配置文件名与 base_url，注释说明不打印原因 | 与密钥治理配套的安全修复 | "测试输出也要过安全审查，print 全量配置等于把 .env 内容贴到 CI 日志上" |
| `frame/testcase/unit/`（**新增**） | 框架层（BaseApi/WeComApi）没有任何不依赖真实环境的单元测试 | `test_base_api.py`（4 条）+ `test_weixin_api.py`（10 条），全部 monkeypatch `requests.request` 与 `fetch_token` | 核心改造逻辑必须有独立验证；且基线中 126 条用例因 IP 白名单无法本机验证，单元测试是唯一可靠的回归手段 | "接口自动化框架本身也需要测试——monkeypatch 掉网络边界后，token 失效重试这种分支逻辑才可能被确定性验证" |

---

## 三、修复的实际 Bug 清单

| # | Bug | 位置 | 修复方式 | 验证结果 |
|---|---|---|---|---|
| 1 | `--env dev/prod` 环境切换完全失效（实例引用断裂） | config.py + 根 conftest.py | `cf.reload(env)` 原地重载 | ✅ `pytest frame/testcase/test_env_switch.py --env dev` 输出 `当前加载的环境配置文件: config/dev.yaml` |
| 2 | token 刷新后不回写实例，session 内每条失效请求都重新 gettoken | base_api.py（原） | WeComApi 刷新后 `self.token = new_token`；token_get 增加模块级缓存 | ✅ 单测 `test_token_expired_refresh_and_retry_once` 断言 `api.token == "new_token"` |
| 3 | 拼 URL 传 token 时，刷新重试会同时携带新旧两个 access_token（旧在 URL、新在 params） | departments.py / users.py / message.py | token 统一改走 params，重试只有唯一注入点 | ✅ 单测 `test_expired_code_and_stale_token_not_leaked_to_retry_params` 断言重试 params 中无旧 token |
| 4 | 重试直接原地修改调用方传入的 req 字典 | base_api.py（原） | `copy.deepcopy(req)` 构造重试请求 | ✅ 单测 `test_token_expired_refresh_and_retry_once` 比对原字典与深拷贝快照 |
| 5 | `params=None` 时重试注入 `req["params"]["access_token"]` 会抛 TypeError | base_api.py（原） | `dict(req.get("params") or {})` 自动补齐 | ✅ 单测 `test_retry_with_params_none` |
| 6 | 非 JSON 响应在 `r.json()` 处直接崩溃，且无法判断是否需要重试 | base_api.py（原） | WeComApi `_is_token_expired()` 捕获 ValueError，非 JSON/非字典视为未失效 | ✅ 单测 `test_non_json_response_no_retry` / `test_json_not_dict_no_retry` |
| 7 | token 明文进入日志（departments 打印 token；send_api 打印含 token 的 URL） | departments.py / base_api.py | 删除 token 打印；`_mask_url()` 对 access_token 脱敏 | ✅ 单测 `test_mask_url_hides_access_token` |
| 8 | 真实密钥明文提交在 Git 仓库（3 个 yaml）且已推送远程 | frame/config/*.yaml | 占位符 + 本地 .env + .env.example；已跟踪日志移出索引 | ✅ 脚本校验 yaml 无真实值；`git check-ignore .env` 通过。⚠️ **必须去企微后台轮换密钥**（历史提交仍含旧值） |
| 9 | `print(cf.data)` 泄露全量配置 | test_env_switch.py | 只打印文件名与 base_url | ✅ 改后运行输出不含密钥 |

---

## 四、改造中两次自检发现并修正的问题

1. **`.env` 加载路径错误**：`_load_dotenv` 初版用两层 `dirname`（指向 `frame/`），而 `.env` 在项目根目录（需三层）。首次全量运行暴露为 133 个 `获取 access_token 失败` 错误，修正路径后恢复与基线一致。教训：路径计算必须写注释说明层级。
2. **终端换行截断**：pytest 的 FAILED 摘要行在 PowerShell 中被折行，导致 22 条失败原因初看"不含 60020"；改用临时文件 + `Select-String` 完整读取后确认全部为 60020 及其级联失败（如"factory 未返回 created_tagid"——前置创建失败导致），与基线一致。

---

## 五、其他模块检查结论（检查后未修改，属正常设计）

| 模块 | 检查结论 |
|---|---|
| pytest fixture 链（token → 4 个 api fixture） | session 作用域合理（token 一次获取、实例全会话共享）；依赖为单向链，无循环 |
| factory fixture（department/user/tag） | function 作用域合理；yield 清理逻辑正确；创建失败时不记录 id（避免删除无效 id）；uuid 唯一化避免用例间数据交叉污染。**检查通过，未修改** |
| `replace_auto_placeholder*` 三个预处理函数 | 存在结构重复，但本次改造范围外（测试数据层），记录为后续改进 |
| assertions.py（jsonpath 断言） | 仅支持相等断言，当前用例够用，不扩展 |
| schema.py（jsonschema 校验） | 工作正常，required 宽松属可接受设计 |
| logger.py | 双输出正常；无轮转策略属可接受（记录为后续改进） |
| message.py mock 分支 | 与测试数据特征耦合（如判断 `"not_exist_user_999"`），属测试便利性设计，不在本次核心范围（未影响 token 解耦），记录为后续改进 |
| settings.py 的 MOCK_MESSAGE 开关 | 模块级常量，当前可用，不改 |
| tags.py 的 get/get_users 方法重复 | 非本次核心问题，不删（删除会改动现有测试用例），记录为后续改进 |
| test_department_flow.py 调用 `get(dep_id)` 传参不符 | 潜在 bug（形参是 params 却传入 id），但该用例因 IP 白名单本机无法运行验证，**不修改无法验证的测试代码**，记录为后续改进 |
| hello.py（语法错误的残留文件） | 未被 Git 跟踪的本地文件，按约束不擅自删除，建议本人确认后自行处理 |
| tools.py 的 CREATED_DEPT_IDS 等全局列表 | 无引用的死代码，无危害，记录为后续清理项 |

---

## 六、验证记录

### 基线（改造前，本分支未提交改动之上）

```
126 failed, 8 passed, 5 warnings in 85.79s
```
- 126 个失败全部为 errcode **60020**（企业微信应用未将本机 IP 加入可信 IP 白名单），属环境限制而非代码缺陷
- 8 个通过：mock 模式消息用例（MOCK_MESSAGE=True）+ 环境切换用例

### 改造后全量

```
126 failed, 22 passed, 5 warnings in 61.52s
```
- 通过数 8 → 22：新增 14 条单元测试全部通过，原有 8 条通过用例**无一条丢失**
- 失败数 126 → 126：失败用例集合与基线一致（126 条中 104 条摘要直接含 60020，其余为 60020 的级联失败，如"factory 未返回 created_tagid"），**未引入任何新失败类型**
- 运行时间 85.79s → 61.52s：主要因 departments 等不再拼 URL、异常路径行为一致，属正常波动

### 新增单元测试（14/14 通过，0.12s，无网络依赖）

`frame/testcase/unit/test_base_api.py`（4 条）：
1. `test_send_api_forwards_request_and_returns_response` — 通用转发 + 代理配置
2. `test_send_api_supports_non_json_response` — 非 JSON 响应不崩溃
3. `test_base_api_has_no_wecom_dependency` — 源码级隔离守护（不得出现 token_get/40014/errcode）
4. `test_mask_url_hides_access_token` — 日志脱敏

`frame/testcase/unit/test_weixin_api.py`（10 条）：
1. `test_normal_response_no_refresh_no_retry` — 正常响应不刷新不重试
2. `test_token_expired_refresh_and_retry_once` — 40014 刷新/回写/重试/不改原字典
3. `test_retry_only_once_even_if_still_expired` — 最多重试 1 次（防请求风暴）
4. `test_both_expired_codes_trigger_refresh`（参数化 40014/42001）
5. `test_other_error_no_retry` — 60020 等其他错误码不触发重试
6. `test_non_json_response_no_retry` — 非 JSON 不做失效判断
7. `test_json_not_dict_no_retry` — JSON 非字典不崩溃不重试
8. `test_retry_with_params_none` — params 缺失自动补齐
9. `test_expired_code_and_stale_token_not_leaked_to_retry_params` — 重试不残留旧 token

### 无法本机验证的用例（如实说明）

以下 126 条用例因**企业微信应用的 IP 可信白名单限制（errcode 60020）**无法在当前网络环境通过，改造前后行为一致，未因本次重构变好或变坏：
- `frame/testcase/departments/`（30 条）
- `frame/testcase/users/`（46 条）
- `frame/testcase/tags/`（46 条）
- `frame/testcase/workflow/`（4 条）
- 说明：基线与改造后失败原因逐条比对一致。要真实通过需在企业微信管理后台将出口 IP 加入应用可信 IP，或在可白名单网络下运行。

---

## 七、遗留不足与后续改进建议（本次不实施）

1. **轮换企业微信密钥（用户必须手动做）**：真实 corpsecret 已存在于 Git 历史并推送远程，仅改当前文件无法消除历史泄露，需到企微后台重置 secret。CI 需配置 `WECOM_CORPID` / `WECOM_CORPSECRET` 仓库 Secrets。
2. 三个 `replace_auto_placeholder*` 函数收敛为"引擎 + 字段映射"。
3. 三个 factory fixture 对外形态统一（SimpleNamespace vs 裸函数）。
4. 测试文件中 12 处重复的 "${auto} 前置创建" 逻辑、14 处重复的 schema_path 拼接收敛。
5. tags.py 的 `get`/`get_users` 方法二选一；users.py 与 departments.py 的 method 大小写统一。
6. message.py mock 分支与测试数据特征解耦。
7. `test_department_flow.py` 中 `department_api.get(dep_id)` 传参问题（需在可运行环境验证后修复）。
8. logger 增加轮转与保留期；assertions 扩展包含/非等断言。
9. requirements.txt 固定版本；CI 与 README 描述对齐。
10. yaml 中已定义但未消费的 `group` 字段接入 pytest marker 或 Allure 分组。

---

## 八、值得重点学习的设计点

1. **模板方法的反向运用**：BaseApi 是"最稳定的能力"，认证是"最易变的能力"，把易变的放进子类扩展点（`send_api` 的重写）而不是基类。
2. **`from x import y` 的绑定语义**：这是环境切换 bug 的根因，也是 Python 面试高频题。
3. **模块级缓存 + force 参数**：用最朴素的方式解决"多实例共享凭证"的刷新风暴。
4. **deepcopy 防御请求字典污染**：测试框架中 fixture/参数化传入的数据被原地修改会导致诡异失败，防御性拷贝是接口层重试的正确姿势。
5. **重试上限**：失效重试"最多一次"是防止请求风暴的底线设计。
6. **monkeypatch 单测框架层**：把网络边界 mock 掉之后，分支逻辑才可被确定性、快速地验证（14 条用例 0.12s）。
7. **密钥治理三件套**：占位符 + 本地 .env（gitignore）+ CI Secrets，以及"入过库的密钥必须轮换"的安全常识。

## 九、面试官可能追问的问题方向

1. "你说的解耦，具体解掉了什么？" → 追问依赖方向：为什么基类 import 子类所属业务模块是反向依赖。
2. "token 刷新后别的实例怎么办？" → 模块级缓存的取舍：实例各自回写 + 刷新端全局缓存。
3. "为什么重试要 deepcopy？不拷贝会出什么 bug？" → 参数化数据被 fixture 共享、原地修改污染后续断言。
4. "如果换成飞书/钉钉，你的框架要改多少？" → 新增一个 XxxApi(BaseApi) 子类 + 一份鉴权模块，BaseApi 与测试层零改动。
5. "环境切换那个 bug 是怎么发现的？" → `--env dev` 后打印的配置文件名没变；根因是 import 绑定语义。
6. "为什么不直接上 pytest-xdist/插件化认证 Provider？" → 拒绝过度设计：当前规模两层继承是复杂度最低的解。
7. "你的 126 条失败怎么保证不是你改坏的？" → 基线先行 + 失败集合逐条比对 + 单元测试覆盖新逻辑。
8. "密钥泄露了怎么办？" → 轮换 > 改文件 > 清历史（清历史需改写 Git，风险高且有协作影响）。
