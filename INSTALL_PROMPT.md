# 安装提示词（复制粘贴给 AI 即可）

> 文中的仓库地址已替换为 `face2333/moleportal-weekly-mcp`，可直接使用。

---

## 主推版本 · 公开仓库（推荐发给同事这段）

```
帮我安装「运营周报数据」这个 skill，按下面的步骤做：

1. 运行：
   npx skills add face2333/moleportal-weekly-mcp --skill moleportal-weekly-mcp -y -g

2. skills CLI 固定装在 ~/.agents/skills/，确认一下：
   ls -d ~/.agents/skills/moleportal-weekly-mcp

   然后复制一份到 WorkBuddy 的技能目录（WorkBuddy 只读 ~/.workbuddy/skills/）：
   cp -R ~/.agents/skills/moleportal-weekly-mcp ~/.workbuddy/skills/

   ⚠️ 不要用 find ~ 去找它 —— 全盘搜索要一两分钟，而且会撞权限错误。

3. 最后告诉我三件事：
   - 技能最终装在哪
   - 我需要在 ~/.workbuddy/mcp.json 里配置 moleportal 的 MCP 地址和 Bearer Token
     （这两个我要去找管理员要，你不要猜）
   - 提醒我改完配置要重启客户端才会生效
```

---

> ⚠️ **两个已知坑**：
> 1. 对方机器要有 Node.js ≥ 18，否则报 `command not found: npx` → 去 [nodejs.org](https://nodejs.org) 装 LTS，或直接用备选 A
> 2. 国内网络下 npx 可能卡在下载环节几分钟无输出（npm 和 GitHub 都慢）→ 别干等，直接用备选 A，效果完全一样

## 精简版（对方会用终端时）

```
帮我安装 npx skills add face2333/moleportal-weekly-mcp --skill moleportal-weekly-mcp -y -g，
然后把生成的 moleportal-weekly-mcp 目录复制到 ~/.workbuddy/skills/ 下。
```

---

## 备选 A · GitHub 打包直链（没装 Node / npx 卡死时首选）⭐

不需要 Node、不需要 skills CLI、不需要登录，直接下载仓库压缩包，效果与 npx 安装完全一致：

```
帮我安装「运营周报数据」这个 skill：
1. 下载 https://github.com/face2333/moleportal-weekly-mcp/archive/refs/heads/main.zip
   到临时目录并解压
2. 把解压出来的 moleportal-weekly-mcp-main/skills/moleportal-weekly-mcp 整个目录
   复制到 ~/.workbuddy/skills/ 下
3. 删掉临时文件
4. 告诉我最终路径，并提醒我需要在 ~/.workbuddy/mcp.json 里配置 moleportal 的
   MCP 地址和 Bearer Token（这两个我去找管理员要，你不要猜），改完要重启客户端
```

> 原理：所谓"安装"就是把同一组文件放进技能目录，走不走 skills CLI 无所谓。

---

## 备选 A2 · 内网直链 zip（GitHub 访问不稳的环境用）

把技能目录打包成 `moleportal-weekly-mcp.zip` 放到内网或对象存储，提示词同上，把下载地址换掉即可。缺点是更新要重新发一次包。

---

## 备选 B · 本地目录（同一台机器上最快）

```
帮我安装这个 skill：
npx skills add /path/to/moleportal-weekly-mcp-publish/skills/moleportal-weekly-mcp -y -g
装完后复制到 ~/.workbuddy/skills/ 下。
```

---

## 发布者自检清单

推送到公开仓库前，逐项确认：

- [x] 仓库地址已替换为 `face2333/moleportal-weekly-mcp`
- [ ] 全仓搜不到真实 IP、Token、callerId、security
      ```bash
      grep -rniE "36\.133|bearer [a-f0-9]{16,}|caller[_ -]?id|security=" . || echo "干净"
      ```
- [ ] `references/` 未包含（服务端运维文档，含业务密钥）
- [ ] 没有 `.DS_Store`
- [ ] 自己先跑一遍验证能被发现：
      ```bash
      npx skills add face2333/moleportal-weekly-mcp --list
      ```
