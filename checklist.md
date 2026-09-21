# Chrome Web Store 全量检查项

配合 [SKILL.md](SKILL.md) 使用。按官方政策章节列出可执行检查。结论用 `PASS / BLOCKER / RISK / WARN / N/A / UNKNOWN`。

来源：https://developer.chrome.com/docs/webstore/program-policies/policies （Last updated 2025-05-22）

## 1. 包、Manifest、技术要求

### Manifest 与文件

- [ ] 存在 `manifest.json`，且提交包与本地审核包一致
- [ ] `manifest_version` 为 3（新提交应为 MV3）
- [ ] manifest 引用的所有文件都在包内，路径与大小写完全一致
- [ ] 有可用图标；action/default_icon、icons 尺寸齐全
- [ ] 扩展能在打包后的 `.crx` / zip 状态下加载，而不仅是 unpacked

### Code Readability（拒审 ID: Red Titanium）

允许：去空白、缩短变量名、合并文件。

不允许：

- [ ] 无混淆、无刻意隐藏功能
- [ ] 无用 Base64 / Unicode 转义 / 字符串拼装来藏逻辑
- [ ] 外部拉取的资源同样不可混淆

### API Use（Blue Nickel / Blue Potassium）

- [ ] 改 New Tab Page 只用 `chrome_url_overrides`
- [ ] 改默认搜索 / 启动页 / 主页只用 Settings Overrides API
- [ ] 搜索体验尊重用户已有搜索设置（NTP 用 `chrome.search`）
- [ ] 不存在“有官方 API 却另写一套绕过”的实现

### Manifest V3 远程代码（Blue Argon）

完整功能必须能从提交代码看出来。可拉数据，不可拉逻辑。

常见违规：

- [ ] 无指向包外资源的 `<script src="https://...">`
- [ ] 无 `eval()` / `new Function()` 执行远程字符串
- [ ] 无自研解释器执行远程“配置/命令”
- [ ] `import()`、动态脚本注入、远程 WASM 当逻辑用 → BLOCKER

允许的远程交互（逻辑仍须在包内）：

- 同步用户账号数据
- 拉 A/B 或功能开关配置（配置里不能有可执行逻辑）
- 拉图片等非逻辑资源
- 服务端运算（如私钥加密）

仅 Debugger API、User Scripts API 可在其文档用途内执行远程逻辑；豁免只覆盖这些 API 覆盖的代码。iframe / sandbox 页可加载远程代码，但仍须能判断完整功能，并遵守 Limited Use 与隐私政策。

审阅员看不懂完整功能 → 会被拒。

### 2-Step Verification

- [ ] 发布或更新前，开发者账号已启用 2SV

## 2. 单一目的与最低功能

### Quality Guidelines / Single Purpose（Red Magnesium / Copper / Lithium / Argon）

单一目的可以是：

- 窄主题（购物优惠、天气、新闻）
- 或窄浏览器功能（NTP、标签管理、搜索提供方）

检查：

- [ ] 能用一句话说明目的，且与 Dashboard 单一目的字段一致
- [ ] 没有捆绑无关功能（评分插件 + 插广告；邮件提醒 + 新闻聚合）
- [ ] 工具栏不是大杂烩入口
- [ ] 持久 UI（侧栏等）增强当前任务，不劫持浏览/搜索
- [ ] 主要目的不是“展示广告”（除非广告本身就是唯一目的且其余政策合规）
- [ ] NTP 不改用户默认网页搜索；多搜索源时默认项跟用户设置走
- [ ] action 图标不塞无关第二功能
- [ ] 权限与单一目的匹配；过宽权限会被当成暗藏第二目的

官方视为独立目的、通常不能和其他功能共存：

- 替换 override 页面（除非属于合规的 search-first 扩展）
- 用 override 改默认搜索（除非属于合规的 search-first 扩展）
- 向网页注入广告

企业域内发布的扩展可豁免单一目的，公开/unlisted 不行。

### Minimum Functionality（Yellow Potassium / Yellow Lithium）

- [ ] 目的不是“安装/启动另一个应用、主题、网页或扩展”
- [ ] 点击图标不只是打开一个网站或安装后立刻跳转宣传页
- [ ] 没有坏掉的功能、失效站点
- [ ] 价值由扩展自己提供，不是只链到外部转换/查询站
- [ ] 不是换皮模板（“每日一词”和“每日一句”那种空壳）
- [ ] 包内不能只有 manifest

### Feature Products（曝光限制，通常不是拒审）

以下可能仍可上架，但不会被官方推荐：VPN、视频下载器、杀毒、宗教/政治、非全家宜、bots、加密货币、非生产构建、赌博内容、开发者信誉差。标 `WARN`。

## 3. 隐私、权限、数据

细节与 Dashboard 文案见 [privacy.md](privacy.md)。

### Privacy Policy（Purple Lithium）

若 handle 用户数据（采集、传输、使用、共享；**含仅本地**）：

- [ ] Dashboard 指定字段有隐私政策链接（不要只写在描述里）
- [ ] 链接可打开，且确实是隐私政策页
- [ ] 写清：收集什么、怎么用、与谁共享

### Limited Use

- [ ] 只用已披露的方式使用数据
- [ ] 只采集单一目的（及运维：维护、安全、性能）所需数据
- [ ] 浏览记录仅用于商店页和 UI 里显著描述的用户可见功能
- [ ] 第三方传输仅限：实现目的、守法、反滥用、并购且用户事先明确同意
- [ ] 人不可读原始用户数据（除非用户明确同意读特定数据 / 聚合匿名内部运营 / 安全 / 守法）
- [ ] 禁止：个性化广告、卖给广告平台/数据经纪、用于信贷
- [ ] 自有网站上有 Limited Use 声明，例如：`The use of information received from Google APIs will adhere to the Chrome Web Store User Data Policy, including the Limited Use requirements.`

### Use of Permissions（Purple Potassium）

- [ ] 每项 required / optional / host permission 都有对应代码路径
- [ ] 能用更窄权限就不用宽权限（能 `activeTab` 就不要 `<all_urls>`）
- [ ] 没有为未来功能预申请权限
- [ ] Dashboard 里每一项都有具体 justification

### Disclosure（Purple Nickel）

- [ ] 安装前显著披露采集内容与用途
- [ ] 用户需做出明确同意动作
- [ ] 披露不在隐私政策/ToS 里才出现；商店描述也不够
- [ ] 安装后若改变数据实践，必须再次显著披露

### Handling（Purple Copper / Purple Magnesium）

- [ ] 用户数据传输使用 HTTPS / WSS 等现代加密
- [ ] 不要把用户数据放进 query / header（日志会泄漏）
- [ ] 不公开披露支付或认证信息
- [ ] 无已知可被利用的安全漏洞

## 4. 上架信息

### Listing Requirements（Yellow Zinc / Yellow Argon）

- [ ] 描述非空，有图标，有截图
- [ ] 标题、描述、分类、开发者名、图标、截图真实、完整、不过时
- [ ] 隐私字段与隐私政策、实际行为一致
- [ ] 无关键词堆砌：无价值的网站/品牌/地区清单；同一词不自然重复超过 5 次
- [ ] 支持站点/品牌若必须列出，描述里不超过 5 个，其余用链接或截图
- [ ] 无未署名或匿名用户推荐

### Misleading or Unexpected Behavior（Red Nickel / Potassium / Silicon）

- [ ] 标题、图标、描述、截图不虚假
- [ ] 不包含做不到的功能（“谁查看了你的账号”）
- [ ] 安全/杀毒/隐私类扩展确实有可辨别的监控或保护
- [ ] 改设置需用户知情同意，且容易还原
- [ ] 没有未披露的附带行为

## 5. 安全生态

### Malicious and Prohibited（Blue Zinc / Copper / Lithium / Magnesium, Grey Silicon）

- [ ] 无病毒、木马、恶意软件、间谍软件、钓鱼
- [ ] 不破坏 Google 或第三方基础设施
- [ ] 不绕过付费墙或登录限制
- [ ] 不协助未授权获取/下载/串流版权内容（含 YouTube 视频下载）
- [ ] 无加密货币挖矿（本机挖或提供挖矿功能都不行）

### 内容安全

- [ ] 无色情、商业色情引流（Grey Lithium）。非性裸露可能影响曝光
- [ ] 不适合全年龄 → Dashboard 标 Mature（Grey Nickel）
- [ ] 无仇恨言论、无端暴力、欺凌、极端组织募资（Grey Magnesium / Potassium）
- [ ] 无违法活动、无处方药交易等（Grey Zinc）
- [ ] 无真钱赌博/预测市场，不给赌博站算赔率或导流（Grey Copper）
- [ ] 不协助销售管制品：药品、酒、烟草、烟花、武器、赌博、医疗器械

模拟赌博若无真钱/有价值奖品，须明确写无真钱，并遵守其余政策。

## 6. 营销与变现

### Impersonation & IP

- [ ] 不冒充公司/组织/其他扩展，不谎称授权或官方
- [ ] UI 不模仿系统或浏览器警告
- [ ] 不链到仿 CWS 站点
- [ ] 元数据不出现虚假 “Editor's Choice” / “Number One”
- [ ] 不侵犯商标、版权等

### Deceptive Installation（Red Zinc）

覆盖广告、推荐页、落地页、安装流。开发者对联盟投放负责。

- [ ] 营销清楚说明会安装 Chrome 扩展及其单一目的
- [ ] CTA 明确是安装扩展：`Install Extension` / `Add Extension` / `Download Extension`
- [ ] CTA 不是 “Play now”、“I'm Human”、填快递单号再跳商店
- [ ] 不缩小商店窗口来藏元数据
- [ ] 一次安装流不捆绑其他扩展或优惠
- [ ] 不要求先装别的软件、点广告、写评价才能用宣传功能
- [ ] 无 typosquat 域名引流

### Ads

- [ ] 广告本身也要符合内容政策与分级
- [ ] 产品内不用 AdSense
- [ ] 广告标明来源，可经设置或卸载去掉
- [ ] 广告不冒充系统通知
- [ ] 不强迫点广告或交个人信息才能用基本功能
- [ ] 在第三方网站旁展示广告须：已披露、标明来源、不干扰原站广告/功能、不仿原站

### Affiliate Ads（Grey Titanium）

- [ ] 商店页、UI、安装前都披露联盟计划
- [ ] 仅在提供与核心功能相关的直接利益时插入（折扣/返现/捐赠）
- [ ] 每次插入前都有相关用户操作（例如用户点“应用优惠码”）
- [ ] 无后台静默写购物 cookie、改 URL 联盟参数、偷偷替换优惠码
- [ ] 找不到优惠时不插入联盟链接

### Accepting Payment

- [ ] 付费才能用基本功能 → 安装前描述写清
- [ ] 标明卖家是开发者不是 Google
- [ ] 支付与退款政策清晰；按 PCI / 适用法律处理卡数据
- [ ] 不处理 Google 禁止的交易

## 7. 垃圾、重复、通知

### Spam and Abuse（Yellow Nickel）

- [ ] 同一开发者/关联账号没有多个体验重复的扩展
- [ ] 本地化不是拆多个扩展的理由，应做在同一个扩展里
- [ ] 无刷安装、刷评、激励下载
- [ ] 不给自己的扩展写评价
- [ ] 通知不作广告/钓鱼/骚扰
- [ ] 代发消息前让用户确认内容和收件人
- [ ] 符合 Google Webmaster Quality Guidelines

允许的重复例外（须在描述和单一目的字段写明）：

- 仅特定 host，且 manifest 权限也锁到该 host
- 仅域内 Publish to Domain（公开/unlisted 不算）
- 企业白标且 unlisted
- 公开测试版须标题和描述标明 BETA，并链到正式版

### Chrome Apps（仅 Chrome App）

打包应用应：用平台能力，不只套网站；能检测离线并自动恢复。

打包/托管应用不应：依赖本地可执行文件（除 Chrome runtime）；WebView 别人的站；在非沙箱环境动态下载执行脚本；滥用通知。
