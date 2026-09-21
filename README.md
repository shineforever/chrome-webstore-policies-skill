# Chrome Web Store 政策验证 Skill

按 [Chrome Web Store Program Policies](https://developer.chrome.com/docs/webstore/program-policies) 对扩展做上架前预审、拒审诊断和隐私字段核对。

政策单页版本：Last updated **2025-05-22**。官方页面优先于本仓库。

## 能做什么

- 对照官方政策检查代码、商店页、隐私政策、Dashboard 字段、安装流
- 把官方拒审编号（如 `Blue Argon`、`Purple Potassium`）映射到原因和修复
- 输出带证据的中文验证报告：`PASS` / `CONDITIONAL` / `FAIL` / `INCOMPLETE`

## 安装

### 当前仓库直接用

本仓库已放好 Cursor project skill：

`.cursor/skills/chrome-webstore-policy-review/`

在本项目里提到 CWS 审核、上架、拒审、隐私字段时，Agent 应加载该 skill。

### 装到其他项目

把整个 skill 目录拷过去：

```bash
cp -R .cursor/skills/chrome-webstore-policy-review \
  /path/to/your-extension/.cursor/skills/chrome-webstore-policy-review
```

或装成个人 skill（所有项目可用）：

```bash
mkdir -p ~/.cursor/skills
cp -R .cursor/skills/chrome-webstore-policy-review \
  ~/.cursor/skills/chrome-webstore-policy-review
```

根目录的 `SKILL.md` 与 `.cursor/skills/.../SKILL.md` 内容相同，复制任一处即可。

## 使用

对 Agent 说例如：

- 按 Chrome Web Store 政策预审这个扩展
- 邮件里是 `Purple Potassium`，帮我看怎么改
- 帮我写单一目的字段和每个权限的 justification

本地可先跑静态扫描（只标可疑点，不是最终结论）：

```bash
python3 scripts/scan.py /path/to/extension
```

## 文件

| 文件 | 作用 |
|------|------|
| `SKILL.md` | 验证流程、结论等级、报告模板 |
| `checklist.md` | 按政策章节的全量检查项 |
| `rejection-ids.md` | 官方拒审编号对照 |
| `privacy.md` | 用户数据、显著披露、Dashboard 字段 |
| `examples.md` | 合格 / 不合格 / 拒审诊断示例 |
| `scripts/scan.py` | 静态预检 |

## 范围

只用于开发者对自己产品的合规检查。不提供规避审核、伪装功能或绕过执行措施的做法。
