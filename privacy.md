# 隐私、权限与 Dashboard 字段

来源：

- https://developer.chrome.com/docs/webstore/program-policies/user-data-faq
- https://developer.chrome.com/docs/webstore/cws-dashboard-privacy
- Limited Use 正文：https://developer.chrome.com/docs/webstore/program-policies/policies

## 什么叫 handle user data

采集、传输、使用、共享都算。包括：

- 登录（含 Google 登录等第三方）
- 收集任何 PII 的表单
- 截图、剪藏、抓取用户正在看的页面
- 后台读云服务里的联系人、邮件、文件
- 浏览活动：域名、URL、HTTP 请求/响应、cookie 等站点存储

**只存在用户设备上，或只用 `chrome.storage.sync`，也要隐私政策。**

例外：用户自己指定服务器的协议客户端（FTP/IRC）。与该用户指定服务器之间的传输，Limited Use 那一节可不适用；开发者自己的注册邮箱等数据仍适用。

与本机原生程序之间的传输，不要求加密。发到远程服务器必须加密。

## 用户数据举例

姓名、地址、电话、邮箱、用户名、证件/账号号码、支付与健康信息、登录态与认证 cookie、网页内容与资源、表单、浏览活动、私人通信、用户生成内容。

## 不处理用户数据时

无额外 User Data 义务。仍要核对：代码是否其实在读页面、URL、账号或表单。很多扩展自以为“不处理”，实际上 content script 已经在 handle。

## 处理用户数据时的最低线

1. Dashboard 指定字段放隐私政策链接
2. 传输使用现代加密（HTTPS / WSS）
3. 遵守 Limited Use
4. 安装前在 **产品 UI** 显著披露，并获得明确同意
5. Dashboard 勾选、隐私政策、代码行为三者一致

不一致的后果：可下架该开发者全部产品、停用现有用户、封关联账号。

## 隐私政策要写什么

至少覆盖：

- 收集什么（含自动日志、扩展回传、权限拿到的持久标识）
- 怎么用（提供功能、识别用户、邮件等）
- 什么情况下与谁共享
- 建议补充：安全措施、用户如何访问/修改/删除、保留期限

链接必须：

- 填在 Privacy practices 的 Privacy Policy 框，不要只写在商店描述
- 可公开访问
- 打开后就是政策正文，不是首页或 404

## 显著披露（prominent disclosure）

必须同时做到：

1. 说明将收集哪些用户数据、如何使用
2. 用户用明确动作表示同意后，才能开始收集
3. 出现在产品 UI 里，用户同意前就能看见
4. **不能只出现在隐私政策、ToS 或商店描述**

安装后如果数据实践发生变化，必须再次显著披露。

合格形态：首次运行弹窗 / 选项页开关，列出数据类型 + 用途 + “同意并继续”。

不合格：只有商店长描述；只有外链隐私政策；默认勾选、滚动即同意。

浏览活动还有加严：必须服务于商店页和 UI 都显著写明的 **用户可见功能**。没有交互 UI、只在后台采浏览数据（含发奖励）——违规。

合格的用户可见功能例子：popup 显示当前域名 WHOIS；给网页加批注；NTP 列出最近访问。

不合格：只有一个“我们会采集历史”的对话框，然后继续在后台采集。

## Limited Use 四要素

1. **Allowed use**：只为提供或改进已披露的单一目的 / 用户可见功能
2. **Allowed transfer**：仅当为实现该目的、守法、安全反滥用、或并购且用户事先明确同意
3. **Prohibited advertising**：不得用作用户数据做个性化 / 重定向 / 兴趣广告
4. **Prohibited human interaction**：人不能读原始用户数据，除非用户同意读特定数据、安全调查、守法、或聚合匿名后仅内部运营

“必要”= 与单一目的成比例，符合用户预期。广告画像、泛市场研究不是必要。

可以做分析，但须披露、成比例、不采无关数据。

自有站点（首页或一跳之内，通常写在隐私政策）必须有肯定句，例如：

> The use of information received from Google APIs will adhere to the Chrome Web Store User Data Policy, including the Limited Use requirements.

## Dashboard：Privacy practices

审阅员主要靠这些字段理解扩展。填不准会直接拒。

### 1. 单一目的

窄、好懂，与代码和商店描述一致。写功能，不写口号。

可用：`在用户当前购物网站显示可用优惠券，并在点击后应用用户选择的优惠码。`

不可用：`提升浏览体验的全能工具。`

### 2. 每个权限的 justification

对 `manifest.json` 里每一项权限写：

- 哪个功能用到
- 为什么更窄的权限不够
- 对应文件或 API

没有用到的权限：先从 manifest 删掉再提交，不要在表单里编理由。

### 3. Remote code

MV3 不能加载并执行远程文件。若确实不用，选 **No, I am not using remote code.** 代码却在拉远程脚本 → 必拒。

用了却不声明、不解释 → 必拒。声明了会加长审核，仍可能因政策失败。

### 4. 数据用途勾选

勾选实际收集的类型，并勾 Limited Use 认证。这些内容会展示给 Chrome 用户，必须和隐私政策一致。

## 权限最小化

required 和 optional 都算。能用 optional 就不要一上来 required。

常见收敛：

| 过宽 | 先考虑 |
|------|--------|
| `<all_urls>` / `*://*/*` | 具体 host、或 `activeTab` |
| `tabs` | host 权限或 `activeTab` 是否已够 |
| `webRequest` / `declarativeNetRequest` 过宽 | 是否只服务单一目的 |
| `cookies` | 是否其实只用页面内 cookie |
| `storage` | 是否其实只用 Web Storage |
| `identity` / `identity.email` | 是否真有登录功能 |

更新若新增权限，用户会看到提示。不要为了“以后可能用”提前加。

建议在商店页或扩展 About 页列出权限及原因。

## 安全传输

- 用户数据走 HTTPS / WSS
- 静态存储建议 RSA / AES；不用 IETF 拒绝的套件
- 即使用 HTTPS，也不要把敏感数据放在 URL 或请求头
- 用 DevTools 看扩展发出的所有请求，包括 content script 所在页面里的请求

## 验证时的三处对照表

| 数据或权限 | 代码是否发生 | 隐私政策是否写 | Dashboard 是否勾/解释 | 产品 UI 是否披露 |
|------------|--------------|----------------|------------------------|------------------|
| 当前 URL / 浏览记录 | | | | |
| 页面内容 / 截图 | | | | |
| 账号邮箱 | | | | |
| 表单或剪贴板 | | | | |
| 发往 `api.example.com` | | | | |
| 第三方 SDK / 分析 | | | | |

任一列是“有”、另一列是“无” → `BLOCKER` 或 `RISK`。
