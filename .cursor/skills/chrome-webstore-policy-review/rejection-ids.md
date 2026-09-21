# Chrome Web Store 官方拒审编号

来源：https://developer.chrome.com/docs/webstore/troubleshooting

邮件里的编号是 `颜色 + 元素`，例如 `Yellow Magnesium`。先对上 ID，再只深挖对应政策。

| ID | 政策主题 | 常见原因 | 先查什么 | 典型修复 |
|----|----------|----------|----------|----------|
| Blue Argon | MV3 远程代码 | 包外 `<script>`；`eval`/执行远程字符串；远程命令解释器 | 所有 HTML/JS 的脚本源、`eval`、`new Function`、动态 `import` | 逻辑改到包内；远程只留数据 |
| Yellow Magnesium | 功能不工作 | 缺文件、路径/大小写错误、审核时服务挂了、与商店描述不符 | 按提交包测试，不要只测 dev 版；核对 manifest 文件列表 | 修打包；错误状态要可见；依赖账号/网络须写明 |
| Purple Potassium | 权限过多 | 申请了但没用；比功能所需更宽 | `permissions` / `optional_permissions` / `host_permissions` 对代码 | 删未用权限；改用更窄权限；申诉时写清每项用法 |
| Yellow Zinc | 元数据不足 | 缺图标/标题/截图/描述；标题或说明无意义 | 商店列出的四大件 + 描述是否解释功能 | 补齐并写清主要功能 |
| Red Nickel / Red Potassium / Red Silicon | 欺骗行为 | 不做描述所说；做了未披露的事；冒充或抄袭 | 标题/图标/描述/截图 vs 实际代码 | 功能与文案对齐；停止冒充和抄代码 |
| Purple Lithium | 隐私政策披露 | 无政策；链接放错位置；打不开；不是政策页；没写收集/使用/共享 | Dashboard Privacy Policy 框，浏览器打开该 URL | 放到指定字段；写收集、使用、共享 |
| Grey Zinc | 非法活动 | 扩展从事或推广非法活动 | 功能与内容 | 主功能违法则下架；否则删除违规部分 |
| Grey Copper | 在线赌博 | 内置赌博；给赌博站算赔率；导流；有现金/有价奖品的技能游戏 | 功能、外链、奖励 | 主功能则下架；否则删除 |
| Grey Lithium | 色情内容 | 自带色情；展示色情；导流到色情站；主要为色情站增强 | 内容、外链、目标站点 | 此类扩展不允许；成人站集成须标 Mature |
| Grey Magnesium | 仇恨内容 | 仇恨言论或导向仇恨内容 | 内容与 UGC 审核 | 主功能则下架；UGC 必须有审核 |
| Grey Nickel | 非全家宜 | 有不适合全年龄内容且未标 Mature | Dashboard Mature 开关 | 删除内容或标 Mature |
| Grey Potassium | 暴力内容 | 无端暴力、威胁、欺凌 | 内容与外链 | 主功能则下架；否则删除 |
| Red Magnesium / Red Copper / Red Lithium / Red Argon | 单一目的 | 多个无关目的；action 塞无关功能；NTP 乱改搜索；插广告 + 其他功能 | 功能清单、NTP、广告注入、override | 拆成多个扩展；广告只能单独做；NTP 搜索用官方 API |
| Purple Nickel | 显著披露 | 未显著说明数据用法；未先征得同意 | 安装后第一次打开的 UI，不只看商店描述 | 产品内披露 + 明确同意动作 |
| Purple Copper | 安全传输 | HTTP 传用户数据；发到不安全域 | 网络请求、WebSocket | 改 HTTPS/WSS；不要把数据放 query/header |
| Purple Magnesium | 其他用户数据 | 非用户可见功能却采集浏览记录；公开披露用户数据 | content script、webRequest、日志、分享 | 停采或做成显著用户功能；禁止公开披露 |
| Grey Silicon | 挖矿 | 本机挖矿或提供挖矿功能 | 后台脚本、WASM、远程任务 | 删除；主功能则下架 |
| Blue Zinc / Blue Copper / Blue Lithium / Blue Magnesium | 违禁产品 | 绕过付费墙/登录；下 YouTube 等版权内容 | 下载、解锁、解析功能 | 删除；主功能则下架 |
| Yellow Argon | 关键词堆砌 | 描述里无关或过量关键词 | 长描述、短描述 | 删堆砌；站点/品牌 ≤ 5 个 |
| Yellow Lithium | 纯跳转 | 唯一功能是打开另一个应用/网页/扩展 | action 点击后发生什么 | 这类不允许，建议下架 |
| Yellow Nickel | 垃圾与滥用 | 重复扩展；刷评/刷量；垃圾通知；未确认代发消息 | 账号下其他扩展、通知代码、分享功能 | 合并重复项；停刷量；发信需确认 |
| Blue Nickel / Blue Potassium | 绕过 Overrides API | 不用官方 API 改 NTP 或地址栏搜索 | NTP 实现、搜索劫持 | 改用 Overrides API，或不要改 |
| Red Zinc | 欺骗安装 | 营销藏扩展；误导 CTA；缩小商店窗 | 落地页、广告、推荐页、CTA 文案 | 重新做合规安装流；开发者对联盟投放负责 |
| Red Titanium | 混淆 | 包内混淆代码 | Base64、`\u0063` 一类编码、加密 JS | 提交可读代码；minify 可以 |
| Yellow Potassium | 最低功能 | 只有 manifest；无价值；功能只是外链；标题党 | 实际能否独立完成描述中的功能 | 让扩展自己提供价值 |
| Grey Titanium | 联盟广告 | 未披露；无相关用户操作就插入 | 改 URL、写 cookie、自动填优惠码 | 披露 + 当次操作 + 当次真实利益 |
| Blue Titanium | 规避执行 | 改商店状态躲审核；卡用户在违规旧版 | 更新通道、多包策略 | 立刻停止；继续做会封号 |

## 编号怎么用

1. 从邮件抄下全部 ID（一封信可能有多个）。
2. 用本表定位政策，不要凭 Impersonation、Spam 等口语自行发挥。
3. 只对相关项做深度取证，输出里写：`官方编号 → 政策 → 证据 → 修复`。
4. 同一违规只能申诉一次；敷衍申诉可能丧失后续申诉权。
5. 下架默认全局生效，除非邮件写了地域限制。修复后要提交修订版，不是只发邮件解释。

## 权限误用速查（Purple Potassium）

| 权限 | 真正给什么 | 不需要它的情况 |
|------|------------|----------------|
| `activeTab` | 用户唤起扩展后，临时访问当前标签 | 已有宽 host 权限；只用 action 图标；`tabs.sendMessage`；普通 `tabs.query` |
| `tabs` | 读取任意标签的 `url` / `pendingUrl` / `title` / `favIconUrl` | 调用 tabs API 方法本身；已有宽 host 权限（host 已含这些数据） |
| `cookies` | 在扩展源里用 `chrome.cookies`，或读 SameSite 等细节 | 只用 `document.cookie` 或 Cookie Store API |
| `storage` | 使用 `chrome.storage` | 只用 `localStorage` / `sessionStorage` / IndexedDB |

## 申诉时要附的证据

- 权限类：每个权限对应的文件、函数、用户场景
- 功能不工作：复现步骤、账号要求、审查员可能碰到的空态
- 远程代码：证明远程响应只是数据，逻辑在包内哪几个文件
- 隐私：Dashboard 截图 + 隐私政策 URL + 政策中对应段落
- 单一目的：功能列表为什么同属一个窄主题或窄浏览器功能
