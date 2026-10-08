---
name: moleportal-weekly-mcp
description: 通过服务器端 moleportal_mcp（MCP）拉取库米云微 Mole Portal OpenAPI 的周维度运营数据，返回结构化 JSON —— 抽奖活动参与（stat-range）、企微社群消息（weekly-chat）、小程序 KPI（weekly-wxmp）。用于运营周报数据分析、环比同比、活动分组对比、社群 TOP 群排行、小程序趋势。触发词：运营周报、周报数据、本周数据、抽奖参与、社群消息、小程序数据、环比、moleportal、库米、周维度分析。既能返回结构化数据供分析，也能在本机渲染出 HTML 周报看板（模板随 skill 分发）。
agent_created: true
---

# Mole Portal 周维度运营数据（MCP 版）

通过服务器 MCP 调用 `cli-anything-moleportal`，拿到**结构化 JSON** 后自行分析、出表、画图。

> 与另一个技能的分工：
> - **本技能** = 走服务器 MCP，返回 JSON 数据，由 Agent 自由分析（第三方用户也能用，凭据在服务器端）
> - `kumi-weekly-report` = 本地独立脚本，一次性生成 HTML 看板，中间数据不可见

---

## 一、接入 MCP 服务（首次使用必做）

⚠️ **前置检查：动手前先确认本机已配置 `moleportal` 这个 MCP 服务**（WorkBuddy 看 `~/.workbuddy/mcp.json`，其它客户端各有各的配置文件，字段一致）。

若配置里**没有** `moleportal`，**停下来向用户索要**这两样，绝对不要猜、不要凭记忆编造：

1. **MCP 服务地址** —— 形如 `https://<host>/mcp`
2. **Bearer Token** —— 形如 `Bearer <一串字符串>`

拿到后帮用户写进配置文件的 `mcpServers` 段：

```json
{
  "mcpServers": {
    "moleportal": {
      "type": "http",
      "url": "<管理员给你的 MCP 地址>",
      "headers": {
        "Authorization": "Bearer <管理员给你的 Token>"
      }
    }
  }
}
```

> 改完配置文件后，客户端通常需要重启、或在连接器管理页点击信任，才会生效。

接入后可用工具：`moleportal_cli_run`（执行）、`moleportal_cli_help`（查帮助）、`moleportal_cli_version`（版本号）。

**业务侧凭据（callerId / security / base-url）已固化在服务器 MCP 进程环境中，调用方无需也不应传。** 若返回 `Missing OpenAPI config` 说明服务器端环境没配上，需联系管理员，不要自行在参数里塞密钥。

---

## 二、调用规范（两个必踩的坑）

### ⚠️ 坑 1：只用 `argv` 传参，禁止用 `options`

服务端 `options` 字段存在 pydantic 校验缺陷 —— 传字符串或对象都会报
`Input should be a valid string`，**该字段实际不可用**。所有参数一律平铺进 `argv` 数组：

```json
{"argv": ["openapi", "weekly", "weekly-chat", "--range-this", "2026-08-31,2026-09-06"], "timeout_s": 120}
```

### ⚠️ 坑 2：组级参数的位置

`--caller-id` / `--security` / `--openapi-base-url` 是 `openapi` **组级**参数，必须放在 `"openapi"` **之后**、子命令之前。一般不需要传；如确需覆盖：

```json
{"argv": ["openapi", "--caller-id", "XXX", "--security", "YYY", "weekly", "weekly-chat", "--range-this", "..."]}
```

### 其它约定

- `json_output` 保持默认 `true`（自动加 `--json`，输出为 JSON）
- `timeout_s` 给 **120**（上限 180；实测三个命令均在 20 秒内返回）
- argv 里**不要**写二进制名，从 `openapi` 开始

---

## 三、三个数据命令

### 1. `weekly stat-range` — 抽奖活动参与

```
argv: ["openapi","weekly","stat-range",
       "--range-this","2026-08-31,2026-09-06",
       "--range-last","2026-08-24,2026-08-30",
       "--suffixes","zys,gyp,lxc,wyy,mxl"]
```

| 参数 | 必填 | 说明 |
|---|---|---|
| `--range-this` | ✅ | `'起,止'`，本周区间 |
| `--range-last` | 否 | 上周区间，传了才算环比 |
| `--suffixes` | 否 | 活动名后缀分组，默认 `zys,gyp,lxc,wyy,mxl` |
| `--page-size` | 否 | 分页大小，默认 500 |

返回结构：

```
thisWeek  : { range, activities[{activityId,name,suffix,records,uniqueUsers}],
              totalRecords, totalUniqueUsers, bySuffix{suffix:{records,uniqueUsers}} }
lastWeek  : 同上（传 --range-last 才有）
comparison: { recordsGrowth, usersGrowth, bySuffix{suffix:{thisRecords,lastRecords,
              recordsGrowth,thisUsers,lastUsers,usersGrowth}} }
```

**注意**：`activities` 是全量活动明细，输出可达 19KB+。分析时**优先看 `totalRecords` / `bySuffix` / `comparison`**，需要查具体某个活动才翻 `activities`；用 `--suffixes` 限定后缀可显著缩小输出。

### 2. `weekly weekly-chat` — 企微社群消息

```
argv: ["openapi","weekly","weekly-chat",
       "--range-this","2026-08-31,2026-09-06",
       "--range-last","2026-08-24,2026-08-30",
       "--top-n","6"]
```

返回：`thisWeek{totalMessages, speakerCount, groupCount, memberCount, topGroups[{rank,groupId,groupName,messageCount}]}`、`lastWeek`、`comparison{messageGrowth, speakerGrowth}`。

### 3. `weekly weekly-wxmp` — 小程序 KPI

```
argv: ["openapi","weekly","weekly-wxmp","--target-date","20260903","--days-back","6"]
```

| 参数 | 必填 | 说明 |
|---|---|---|
| `--target-date` | ✅ | `YYYYMMDD` 格式（注意无横线），通常取**昨天**（数据 T+1） |
| `--days-back` | 否 | 趋势图天数，默认 6（含目标日共 7 天） |

返回：`summary{visitTotal, shareUv, sharePv}`、`trend{sessionCnt, visitUv, visitUvNew, stayTimeSession, visitDepth}`、`growth{各指标的 current/dayAgo/weekAgo/monthAgo + dayGrowth/weekGrowth/monthGrowth}`、`trendChart[{date,sessionCnt,visitUv,visitUvNew}]`。

---

## 四、出 HTML 看板（skill 侧渲染）

HTML 模板随本 skill 分发，渲染在本机完成 —— **服务器只提供数据，不产出文件**。

### 第 1 步 · 一次拿全量数据

```json
{"argv": ["openapi","weekly","full-report","--data-only",
          "--this-start","2026-08-31","--this-end","2026-09-06"], "timeout_s": 120}
```

`--data-only` 只返回结构化数据、**跳过 HTML 渲染**，stdout 是纯净 JSON（进度信息走 stderr）：

```
{ "status":"success", "thisWeek":"...", "lastWeek":"...", "p1":{...}, "p2":{...}, "p3":{...} }
```

存到临时文件（如 `/tmp/weekly_data.json`）。用 `--data-only` 时**不要传** `--output`。

#### ⚠️ 坑 3：返回体约 15–40KB，可能超出部分客户端的 MCP 单次返回上限

`full-report --data-only` 的输出是完整 JSON（活动多的周会更大），部分客户端会报 `result exceeds maximum allowed tokens`。此时**不要**改用三个子命令拼数据（那样会拿到不一致的口径，见下）。正确做法：MCP 会把完整结果落盘并给出文件路径，用 python 从落盘文件里取：

> 注：输出**不含手机号明细**（已剔除，避免明文进入上下文与产物），需要人数看 `totalUniqueUsers` / `uniqueUsers` 即可。

```python
import json
wrapper = json.loads(open("<落盘文件路径>", encoding="utf-8").read())
data = json.loads(wrapper["stdout"])          # stdout 是纯净 JSON
json.dump(data, open("/tmp/weekly_data.json","w",encoding="utf-8"),
           ensure_ascii=False, indent=2)
```

#### ⚠️ 坑 4：`full-report` 的 p1/p2/p3 结构与三个子命令**不同**，不要张冠李戴

不要用 `stat-range` / `weekly-chat` / `weekly-wxmp` 的返回去拼 `full-report` 的 p1/p2/p3 —— 字段和口径都对不上：

| | `full-report` 里的结构 | 子命令返回 |
|---|---|---|
| p1 | `suffixRows[]`（含 name/activityIds/idsText）、`thisCampaigns`、`lastCampaigns`；`comparison` **只有数字**，无 `recordsGrowth` 字符串 | `activities[]` 全量明细、`comparison.bySuffix` 带 growth 字符串 |
| p2 | `comparison` **恒为 null**；`topGroups[]` 每项带 `memberCount` / `lastMessageCount` / `lastRank` | `comparison` 有 `messageGrowth` / `speakerGrowth`；`topGroups` 无上周对比 |
| p3 | `targetDate` 取**本周最后一天**；`trendChart` 为 **14 天**（上周+本周） | `--target-date` 单日，`trendChart` 7 天 |

`groupRows` 的 `lastVal` 直接取 `topGroups[].lastMessageCount`（`lastRank` 为 null 表示上周未入榜）。

### 第 2 步 · 你来写复盘分析（这层是模型的活）

基于 `p1/p2/p3` 自己推理，产出如下结构的 JSON，存为 `/tmp/analysis.json`：

```json
{
  "highlights": [{"title": "社群活跃度提升 45%", "desc": "消息 1393→2022，增量主要来自 4 个腰部群…"}],
  "risks":      [{"title": "土秀才抽奖·wyy 明显回落", "desc": "132→101（-23.5%），建议排查奖品与推送时段…"}],
  "activityRows": [{"name":"会员日抽奖·gyp","thisVal":210,"lastVal":240,"change":"↓ 30 (-12.5%)","flag":"down","note":"连续下滑，建议…"}],
  "groupRows":    [{"name":"土秀才孙士梅十五红群","thisVal":307,"lastVal":207,"change":"↑ 100 (+48.3%)","flag":"up","note":"稳居 TOP1，建议…"}],
  "wxmpRows":     [{"name":"打开次数","thisVal":23,"lastVal":30,"change":"↓ 7 (-23.3%)","flag":"down","note":"周日效应，建议看活动日数据…"}],
  "globalItems":  [{"title":"综合判断","desc":"抽奖回落、社群升温，活跃重心向社群转移…"}],
  "plans":        [{"title":"优化抽奖活动","desc":"回落组优先，调整奖品配置与推送时段…"}]
}
```

`flag` 取值：`up` / `down` / `flat`。写不出内容的数组留空即可，页面显示"暂无"。

**分析质量要求**（别写正确的废话）：
- 每条都要有**具体数字 + 一个可执行动作**，不要"建议持续关注"这类空话
- 优先解释**异常值**：跌幅 ≥20% 的、新晋或跌出榜单的、连续多周同向的
- 允许给归因假设（活动排期、奖品、推送时段、节假日），但要说明是推测
- 数据不足以支撑结论时明说"数据不足"，不要硬编

### 第 3 步 · 渲染

```bash
python3 "<SKILL_DIR>/scripts/render_report.py" \
    --data /tmp/weekly_data.json \
    --analysis /tmp/analysis.json \
    --output ~/Desktop/运营周报_2026-09-06.html
```

> **`<SKILL_DIR>` = 本 SKILL.md 所在的目录。** 加载本技能时你已经拿到了它的完整路径（形如 `/Users/xxx/.workbuddy/skills/moleportal-weekly-mcp`），直接填进去即可 —— 这是唯一可靠的定位方式。
>
> ⚠️ **不要用 `find ~` 全盘搜索来定位**，三个理由：
> 1. **慢** —— 全盘搜索要一两分钟
> 2. **漏** —— 会在 `Pictures` / `Library` 等目录撞权限错误，可能正好跳过目标目录
> 3. **错** —— 机器上常有多份副本（不同 agent 各装一份），`head -1` 取到哪份全凭运气，可能用错版本的脚本
>
> 只有在确实拿不到自身路径时，才用这条有序兜底（快、无权限问题）：
>
> ```bash
> for d in ~/.agents/skills ~/.workbuddy/skills ~/.codex/skills ~/.cursor/skills; do
>   [ -d "$d/moleportal-weekly-mcp" ] && echo "$d/moleportal-weekly-mcp"
> done
> ```

脚本仅用标准库，模板默认取 skill 包内的 `templates/weekly_report_template.html`。

### 第 4 步 · 渲染后自检（别跳过）

```bash
grep -cE '\{\{[A-Za-z_-]+\}\}' <输出.html>   # 应为 0，非 0 说明有占位符没替换
```

顺带确认产物里没有手机号明文（应为 0）：

```bash
grep -oE '"1[0-9]{10}"' <输出.html> | sort -u | wc -l
```

同时建议用脚本把 `analysis.json` 里每个 `thisVal/lastVal` 与 `p1.suffixRows` / `p2.topGroups` 的对应字段**交叉校验一遍**，防止分析里写的数字与数据源漂移。

---

## 五、数据解读必须避开的 5 个坑

1. **`visitTotal` 是累计值，不是当日值** —— 它只增不减（如 5661），所以它的日/周/月"增长"恒为正，**没有环比意义**。要看真实波动用 `sessionCnt` / `visitUv` / `visitUvNew`。
2. **小程序接口不支持多日范围查询**（上游会报 code 61501），`weekly-wxmp` 内部已按单日循环绕过，`--target-date` 只能传单日。
3. **社群消息为 0 不等于没运营** —— 需该项目开通企微会话存档才有数据；全 0 时应提示"会话存档可能未开通"，而不是断言"社群无活跃"。
4. **抽奖活动筛选窗口是"上周一 ~ 本周日"**，跨 14 天；窗口外（已结束或未来）的活动不参与统计，活动数看起来少于全量 197 个属正常。
5. **环比阈值参考**：周维度波动 ±5% 以内通常算正常噪声；**跌幅 ≥20%** 才值得单列预警。

---

## 六、标准作业流（拉全量三块数据）

1. 先确认时间范围 —— 用户说"本周"→ 取所在自然周的**周一 ~ 周日**；"上周"→ 上一个完整自然周。用 `date` 命令核对星期几，不要凭感觉。
2. 依次调用三个命令（`stat-range` → `weekly-chat` → `weekly-wxmp`），可并行发起。
3. 汇总时按「抽奖 / 社群 / 小程序」三段组织，每段给：本周值、上周值、环比、异常点。
4. 异常判定：跌幅 ≥20% 的分组单列预警；`visitTotal` 不要做环比结论；社群全 0 提示会话存档。
5. **不要只罗列数字** —— 必须给出至少一条可执行的判断或建议（哪个活动该查、哪个群值得跟）。

### 输出规范

- **用中文指标名**（本周参与人数、社群消息总数、发言人数…），不要把 `totalRecords`、`speakerCount` 这类英文字段直接甩给用户
- 增长率用 **红涨绿跌**（国内习惯）：涨用红色、跌用绿色
- 数字用千分位；百分比保留 1 位小数
- 用户要表格就出表格，要图表建议就给出图表方案，不要在纯数据场景下硬塞大段文字

---

## 七、排查

| 现象 | 原因 / 处理 |
|---|---|
| `Input should be a valid string` | 用了 `options` 参数 → 改平铺进 `argv` |
| `No such option: --caller-id` | 组级参数放错位置 → 必须在 `openapi` 之后 |
| `Missing OpenAPI config` | 服务器 MCP 进程环境缺凭据 → 联系管理员配，不要在参数里传 |
| `No such command 'weekly'` | 服务器端 CLI 版本未注册 weekly → 需重新部署 `weekly_report.py` |
| 返回体很长被截断 | `stat-range` 明细所致 → 加 `--suffixes` 缩小范围 |

需要 curl 直连排查时，向管理员索取调试示例 —— 本公开版不含服务端运维文档。
