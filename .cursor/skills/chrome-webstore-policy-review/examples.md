# 报告示例

## 示例 A：可以提交（PASS）

用户：帮我按 Chrome Web Store 政策预审这个优惠券扩展。

材料齐：MV3 包、商店文案、隐私政策 URL、Dashboard 草稿。扫描无远程脚本、无 `eval`。

```markdown
# Chrome Web Store 政策验证报告

- 产品：Shop Coupons
- 版本 / Manifest：1.2.0 / MV3
- 验证日期：2026-09-20
- 政策参考：https://developer.chrome.com/docs/webstore/program-policies/policies （2025-05-22）
- 总体结论：PASS
- 阻塞项 / 风险项 / 未知项：0 / 0 / 0

## 一句话结论
可以提交。单一目的清楚，权限与披露对齐，未见远程逻辑或违禁功能。

## 单一目的判定
- 声称的单一目的：在当前购物站点展示并应用优惠券
- 实际功能：content script 读商品价；popup 列出优惠券；用户点击后写入优惠码
- 判定：PASS
- 理由：功能都属于“购物优惠”这一窄主题，没有搜索劫持或广告注入

## 逐项结果

| 等级 | 政策 / 拒审 ID | 结论 | 证据 | 修复 |
|------|----------------|------|------|------|
| PASS | Single purpose | 仅优惠券 | `src/popup.js`, `src/content.js` | — |
| PASS | Purple Potassium | `activeTab` + 三个购物 host | manifest `host_permissions` | — |
| PASS | Purple Lithium | 政策 URL 可打开并写明收集 URL 与账号 | https://example.com/privacy | — |
| PASS | Purple Nickel | 首次运行弹窗 + 同意按钮 | `src/consent.js` | — |
| PASS | Blue Argon | 无远程脚本；配置 JSON 无逻辑 | `src/sw.js` 只 fetch `/flags.json` | — |
| WARN | Listing | 描述写了 6 个支持站点 | 商店长描述 | 描述保留 5 个，其余放截图或链接 |

## 必须先改
无阻塞项。建议提交前把站点列表收到 5 个以内。

## Dashboard 隐私字段建议
- 单一目的：在用户当前购物网站显示可用优惠券，并在用户点击后应用其选择的优惠码。
- `activeTab`：用户打开 popup 时读取当前购物页价格。
- `storage`：保存用户已选优惠券，使用 `chrome.storage.local`。
- 数据采集：Website content、Product interaction
- Remote code：No
- Limited Use 声明：已写在隐私政策末段

## 无法确认
无。
```

## 示例 B：不能提交（FAIL）

用户：这个“新标签页 + 加速 + 壁纸”扩展能不能上架？

```markdown
# Chrome Web Store 政策验证报告

- 产品：Super Start Tab
- 版本 / Manifest：3.0.1 / MV3
- 总体结论：FAIL
- 阻塞项 / 风险项 / 未知项：4 / 2 / 1

## 一句话结论
不要提交。单一目的失败，且存在远程代码和未披露的联盟 cookie。

## 单一目的判定
- 声称的单一目的：美化新标签页
- 实际功能：替换 NTP、改默认搜索、注入比价条、后台写联盟 cookie
- 判定：BLOCKER
- 理由：NTP、搜索覆盖、购物注入是三个独立目的；搜索未用官方 Overrides / `chrome.search`

## 逐项结果

| 等级 | 政策 / 拒审 ID | 结论 | 证据 | 修复 |
|------|----------------|------|------|------|
| BLOCKER | Red Magnesium | NTP + 搜索 + 购物条 | `manifest.json` overrides + `src/inject.js` | 拆成三个扩展；NTP 搜索走 `chrome.search` |
| BLOCKER | Blue Argon | 远程脚本 | `ntp.html` `<script src="https://cdn.example.com/ntp.js">` | 把脚本打进包内 |
| BLOCKER | Grey Titanium | 无操作写 affiliate cookie | `src/sw.js` `chrome.cookies.set` | 删除静默写入；若保留须披露+用户点击+当次折扣 |
| BLOCKER | Purple Lithium | 描述里写了隐私链接，Dashboard 字段为空 | 商店描述第 4 段 | 填到 Privacy Policy 指定框 |
| RISK | Purple Potassium | 申请了未使用的 `history` | manifest 有，代码无引用 | 删除权限 |
| RISK | Yellow Argon | “wallpaper, wallpapers, new tab wallpaper…” 重复 9 次 | 长描述 | 改成自然段落 |
| UNKNOWN | Purple Nickel | 未见首次运行披露 | 包内无 consent UI | 补产品内同意，或确认从未采集数据 |

## 必须先改
1. 去掉远程 `ntp.js`，逻辑进包。
2. 删除默认搜索修改和后台联盟 cookie。
3. 只保留一个窄目的。
4. 在 Dashboard 指定字段填写可访问的隐私政策。
```

## 示例 C：拒审诊断

用户：邮件写了 `Purple Potassium` 和 `Yellow Magnesium`，怎么改？

不要重写整份政策。先查 [rejection-ids.md](rejection-ids.md)：

```markdown
# Chrome Web Store 拒审诊断

- 官方编号：Purple Potassium；Yellow Magnesium
- 总体结论：FAIL（按邮件，两项都未修）

## Purple Potassium — 权限过多
- 政策：Use of Permissions
- 证据：`tabs` 只用于 `chrome.tabs.query({active:true})` 取当前标签，官方说明此场景不需要 `tabs`
- 修复：删除 `tabs`；当前标签信息改用 `activeTab` 或已有 host 权限
- 申诉补充（若你认为权限必要）：写明读取任意标签 URL 的具体用户场景和代码路径

## Yellow Magnesium — 功能不工作
- 政策：Minimum Functionality / 描述一致性
- 证据：描述写“一键导出 PDF”，popup 按钮在未登录时无提示；审核员无测试账号会视为坏掉
- 修复：
  1. 用提交包（不是本地 unpacked）复现
  2. 未登录显示明确空态和登录入口
  3. 在单一目的字段写清“需要 example.com 账号”
- 若本地完全正常：用开发者支持表单问审查员具体失败步骤

## 申诉
两项都是可修问题。先提交修订版。若权限项你有反证，用详情页 Appeal 一次说明，不要同时发敷衍申诉。
```

## 反例：不要这样输出

- “整体感觉没问题，可以试试上架。”（无证据、无等级）
- “隐私方面注意一下。”（不指出字段、URL、代码）
- “把代码混淆一下就能过。”（教规避，禁止）
- “远程脚本改成 Base64 再 eval。”（仍是 Blue Argon / Red Titanium）
