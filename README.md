# moleportal-weekly-mcp

用自然语言拉取 **Mole Portal 周维度运营数据**（抽奖活动参与 / 企微社群消息 / 小程序 KPI），并可在**本机**渲染成一份单文件 HTML 周报看板。

装好之后你不需要记任何命令，直接问 AI 就行：

- 「拉一下本周的运营周报数据」
- 「上周抽奖活动参与情况怎么样，哪些活动掉得厉害」
- 「本月社群消息 Top10 群是哪些」
- 「出一份周报看板」

---

## 一、你需要准备什么

向**管理员**索取两样东西（本仓库不包含任何凭据）：

| 项目 | 说明 |
|---|---|
| MCP 服务地址 | 形如 `https://<host>/mcp` |
| Bearer Token | 形如 `Bearer <一串字符串>` |

把它们填进客户端的 MCP 配置（WorkBuddy 是 `~/.workbuddy/mcp.json`）：

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

业务侧密钥（callerId / security）固化在服务端，你接触不到也不用管。

---

## 二、安装

### 方式 A：复制一段话给 AI（推荐）

把 [`INSTALL_PROMPT.md`](INSTALL_PROMPT.md) 里的提示词整段复制，粘贴给你的 AI 助手即可。

### 方式 B：自己敲一行

```bash
npx skills add face2333/moleportal-weekly-mcp --skill moleportal-weekly-mcp -y -g
```

> skills CLI 固定把技能装在 `~/.agents/skills/`。而 WorkBuddy 读的是 `~/.workbuddy/skills/`，
> 所以装完要再复制一份过去才能生效 —— 提示词里已包含这一步。

### 方式 C：手动放文件夹

把 `skills/moleportal-weekly-mcp/` 整个目录拷到你的技能目录（WorkBuddy 是 `~/.workbuddy/skills/`），重启客户端即可。

---

## 三、目录结构

```
skills/moleportal-weekly-mcp/
├── SKILL.md                          # 技能主文件（AI 读的操作规范）
├── USAGE.md                          # 给人看的使用说明
├── scripts/render_report.py          # HTML 看板渲染脚本（仅用标准库）
└── templates/运营周报看板_template.html
```

---

## 四、更新

```bash
npx skills update moleportal-weekly-mcp -g
```

---

## 五、说明

- 数据来自**生产环境**，每次查询都是实时拉取，不是缓存快照。
- HTML 看板在你的**本机**渲染，服务器只提供数据、不产出文件。
- 输出中不含手机号等个人明细。
- 所有使用者查到的是同一个项目的数据，需要切换项目请联系管理员调整服务端配置。
