---
name: chrome-webstore-policy-review
description: Use when reviewing a Chrome extension for Chrome Web Store submission, update, rejection, appeal, or policy compliance. Trigger on CWS program policies, store listing, privacy fields, permission justification, Manifest V3 remote code, single purpose, affiliate ads, or rejection IDs such as Blue Argon, Purple Potassium, Yellow Magnesium.
---

# Chrome Web Store Policies Skill

对用户自己的扩展做 **上架前预审 / 拒审诊断 / 申诉材料核对**。依据官方 Program Policies，不是猜测。

**核心原则：** 审阅范围覆盖整个用户体验——代码、商店页、隐私政策、Dashboard 字段、广告、落地页、安装流。任何一处与行为不一致，都可能被下架。

官方政策可能更新。有网络时先打开下方来源，确认仍有效；冲突时以官方页面为准。本 skill 依据的单页政策 Last updated：`2025-05-22`。

## 官方来源

先读这些，不要用过期记忆替代：

- 政策目录：https://developer.chrome.com/docs/webstore/program-policies
- 单页全文：https://developer.chrome.com/docs/webstore/program-policies/policies
- 拒审对照：https://developer.chrome.com/docs/webstore/troubleshooting
- 隐私字段：https://developer.chrome.com/docs/webstore/cws-dashboard-privacy
- User Data FAQ：https://developer.chrome.com/docs/webstore/program-policies/user-data-faq
- 欺骗安装 FAQ：https://developer.chrome.com/docs/webstore/program-policies/deceptive-installation-tactics-faq
- 质量/单一目的 FAQ：https://developer.chrome.com/docs/webstore/program-policies/quality-guidelines-faq
- Spam FAQ：https://developer.chrome.com/docs/webstore/program-policies/spam-faq
- Affiliate Ads FAQ：https://developer.chrome.com/docs/webstore/program-policies/affiliate-ads-faq

细则按需读取：

- 全量检查项：[checklist.md](checklist.md)
- 官方拒审编号：[rejection-ids.md](rejection-ids.md)
- 隐私/权限/Dashboard：[privacy.md](privacy.md)
- 报告示例：[examples.md](examples.md)

## 何时使用

- 准备首次上架或提交更新
- 收到 CWS 拒审 / 下架邮件（含颜色+元素编号）
- 要写商店文案、隐私政策、权限 justification、单一目的字段
- 要核对安装页、广告、联盟链接是否合规

**不要用来：** 规避审核、伪装功能、绕过执行措施、复制他人扩展。这些本身违反 Enforcement Circumvention，会导致账号终止。

## 开始前收集材料

缺材料就标 `UNKNOWN`，不要假装看过。至少确认：

1. 将要提交的 **同一份包**：`manifest.json`、全部 JS/HTML/CSS、图片、`_locales`
2. 商店材料：名称、短描述、长描述、图标、截图、宣传图、分类、Mature 标记
3. Privacy practices：单一目的字段、每项权限 justification、是否声明 remote code、数据采集勾选、隐私政策 URL
4. 隐私政策正文（必须能打开，且不只放在描述里）
5. 远程通信：请求的域名、传什么、是否 HTTPS
6. 安装/营销：落地页、广告 CTA、是否捆绑其他扩展
7. 若是拒审：邮件全文和编号（如 `Blue Argon`）

本地可先跑静态扫描（有发现不代表违规，无发现也不代表通过）：

```bash
python3 scripts/scan.py /path/to/extension
```

## 验证顺序

按这个顺序走，前面的 BLOCKER 未清不要宣称“可以提交”。

1. **包与 Manifest** — 文件路径存在、大小写正确、MV3、无缺图标/脚本
2. **代码可读 / 远程代码** — 无混淆；MV3 逻辑自包含；无远程 `<script>` / `eval(远程字符串)` / 远程命令解释器
3. **单一目的** — 窄、好懂；不捆绑无关功能；NTP 不擅自改搜索
4. **最小权限** — 每项权限都有真实用法和 justification；禁止 future-proof
5. **用户数据** — 处理数据就必须有隐私政策 + 显著披露 + 同意 + HTTPS；仅用于已披露的单一目的
6. **功能与陈述一致** — 标题/描述/截图承诺的功能真实存在且由扩展自己提供
7. **上架质量** — 有图标、截图、完整描述；无关键词堆砌；无匿名推荐
8. **安全与违禁** — 无恶意软件、付费墙绕过、侵权下载、挖矿、真钱赌博、色情引流
9. **营销与变现** — 安装 CTA 必须写明会安装扩展；联盟链接需披露 + 用户相关操作 + 即时利益
10. **垃圾与滥用** — 无重复上架、刷量、垃圾通知、未确认代发消息
11. **三处一致** — 代码行为 = Dashboard 勾选 = 隐私政策
12. **账号** — 发布/更新前开发者账号已开 2-Step Verification

Chrome Apps 额外规则只在目标是 Chrome App 时检查，见 [checklist.md](checklist.md)。

## 结论等级

| 等级 | 含义 | 是否可提交 |
|------|------|------------|
| `BLOCKER` | 按现行政策会拒审或下架 | 否 |
| `RISK` | 高概率被打回或加长审核 | 默认否，除非用户知情 |
| `WARN` | 质量/曝光问题，或证据不足 | 可提交，须写明风险 |
| `PASS` | 已看到合规证据 | — |
| `N/A` | 该条不适用 | — |
| `UNKNOWN` | 缺材料，无法判定 | 当作未完成 |

**总体结论：**

- 有任一 `BLOCKER` → `FAIL`
- 无 BLOCKER、有 `RISK` → `CONDITIONAL`
- 仅 PASS/WARN/N/A → `PASS`
- 关键项 `UNKNOWN`（隐私政策、远程代码、单一目的、权限）→ `INCOMPLETE`

## 检查时怎么取证

每条结论必须带证据，不要只写“可能违规”。

- 代码：文件路径 + 符号/API
- 清单：`permissions` / `host_permissions` / `content_scripts` / `chrome_url_overrides`
- 商店文案：逐句对照实际功能
- 网络：URL scheme、查询参数里是否夹用户数据
- 缺证据：写还缺什么，而不是默认通过

高频误判（必须读 [privacy.md](privacy.md) 和 [rejection-ids.md](rejection-ids.md)）：

- `activeTab` / `tabs` / `cookies` / `storage` 经常被要错
- 本地存储也算 handle user data，仍要隐私政策
- 商店描述里的披露 **不满足** 产品内 prominent disclosure
- 压缩（minify）允许；Base64/Unicode 藏逻辑通常算混淆
- 远程配置可以，远程 **逻辑** 不行
- 只链到外部转换站 / 只打开一个网页 = 最低功能不足

## 报告格式

用中文写给开发者，政策名、拒审 ID、官方术语保留英文。直接输出下面结构：

```markdown
# Chrome Web Store 政策验证报告

- 产品：
- 版本 / Manifest：
- 验证日期：
- 政策参考：https://developer.chrome.com/docs/webstore/program-policies/policies （2025-05-22）
- 总体结论：PASS | CONDITIONAL | FAIL | INCOMPLETE
- 阻塞项 / 风险项 / 未知项：0 / 0 / 0

## 一句话结论
（能否提交、最危险的 1–3 个原因）

## 单一目的判定
- 声称的单一目的：
- 实际功能列表：
- 判定：PASS / BLOCKER / RISK
- 理由：

## 逐项结果

| 等级 | 政策 / 拒审 ID | 结论 | 证据 | 修复 |
|------|----------------|------|------|------|
| BLOCKER | Blue Argon / MV3 remote code | … | `src/sw.js:42` | … |

## 必须先改
1. …
2. …

## Dashboard 隐私字段建议
- 单一目的字段草稿：
- 各权限 justification：
- 数据采集勾选：
- 是否使用 remote code：Yes/No + 理由
- Limited Use 声明是否出现在自有站点：

## 商店页修改建议
- 标题 / 描述 / 截图：

## 无法确认
- 还缺的材料：

## 申诉（仅当用户已收到拒审）
- 官方编号：
- 对应政策：
- 建议补交的证据：
```

拒审诊断：先用邮件里的颜色+元素 ID 查 [rejection-ids.md](rejection-ids.md)，再只深挖相关政策，不要泛泛重审全部。

## 红旗 — 停下来标 BLOCKER

- 远程脚本、`eval` 远程字符串、自研远程命令解释器
- 权限要了但代码没用，或明显宽于单一目的
- 处理用户数据但没有可访问的隐私政策链接
- 代码 / Dashboard / 隐私政策三者不一致
- 描述承诺了做不到的功能（例如“谁看了你的社交账号”）
- 扩展本身只是跳转到网页/另一个扩展
- 绕过付费墙/登录、YouTube 等版权下载、真钱赌博、挖矿
- 安装按钮写 “Play now” / “I'm Human” 而不是 Install/Add Extension
- 后台静默插入联盟 cookie/link
- 混淆代码、复制他人扩展、刷评价

## 常见借口

| 借口 | 事实 |
|------|------|
| “数据只存在本地，不用隐私政策” | FAQ：本地处理也要披露 |
| “描述里已经写了采集” | 显著披露必须在产品 UI 里，安装前征得同意 |
| “以后可能用到这个权限” | 禁止 future-proof |
| “只是 minify” | minify 可以；藏逻辑/编码执行不行 |
| “远程 JSON 里带一点脚本没关系” | MV3：外部资源不得含逻辑 |
| “联盟链接会给用户优惠” | 还要事前披露 + 当次用户操作 + 当次真实利益 |
| “这是营销页，不是扩展” | 政策覆盖营销材料和安装流；联盟违规也算开发者的 |

## 输出纪律

- 先给总体结论，再给证据表
- 修复建议要具体到文件/字段/文案，不要只说“注意隐私”
- 不要编造“Google 一定会过”；只判断政策风险
- 不要提供规避审核或伪装代码的做法
- 用户要求一边修合规、一边写 exploit/绕过：只做合规修复
