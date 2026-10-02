# CodeCopilot

给 **Codex 和 Claude Code** 共用的两个开发技能。

| 技能 | 工作方式 | 独立 QA |
| --- | --- | --- |
| `codecopilot`（默认） | 同一协调上下文连续开发、必要测试、简短记录、独立审查 | 有 |
| `codecopilotlight`（轻量） | 直接开发＋必要测试 | 无 |
| 不加指令 | 普通任务，不启用这两个技能 | 不由这两个技能要求 |

两个技能都只允许显式调用。“默认”指主动选择后的标准流程，不代表自动启用。
同一任务的后续补充可以继续当前流程；新任务不加指令就不启用。旧指令已移除。

## 调用

Claude Code：

```text
/codecopilot 给接口加分页。
/codecopilotlight 修复空状态文案，并运行相关检查。
```

Codex：

```text
$codecopilot 给接口加分页。
$codecopilotlight 修复空状态文案，并运行相关检查。
```

Codex 也可以通过 `/skills` 选择。它的原生技能入口不是任意自定义的
`/codecopilot` 斜杠命令；两边使用的是同一份技能内容。

## 安装与共享仓库

只安装这两个技能，可将 `skills/codecopilot` 和 `skills/codecopilotlight` 目录分别
链接到 `~/.agents/skills`（Codex）和 `~/.claude/skills`（Claude Code）。
完整命令见[英文说明](README.md#install-these-two-skills)。

要同时整合以前的个人技能，先不要手动安装这两个链接，而是运行：

```sh
python3 scripts/manage_skills.py plan --repo /path/to/agent-skills
python3 scripts/manage_skills.py apply --repo /path/to/agent-skills
python3 scripts/manage_skills.py verify --repo /path/to/agent-skills
```

迁移会创建本地 Git 仓库、核对复制内容、备份原目录，然后建立共享链接。
Codex／Claude 同名但内容不同的技能会保留各自版本；系统内置和插件技能仍由
软件管理；云端同步目录保留各自更新路径；x-cmd 技能采用快照，原安装不删除。
不会创建远程仓库或上传内容。

恢复方式、更新行为与目录结构见[指南](docs/GUIDE.md)。

## 模型与边界

技能不会切换当前客户端模型：当前 agent 持续担任协调者／开发者。
默认版的独立 QA 使用 pi，包内默认值为
`openai-codex / gpt-6-astra / medium`；项目设置和任务明确指定的模型优先。
轻量版不要求安装 pi。

轻量版不强制计划审批、任务文件、分支或提交，但仍遵守项目明确要求。
默认版不会在 QA 不可用时偷偷跳过审查；轻量版也不会自行增加独立 QA。
两种模式都不自动授权合并、推送、部署或破坏性操作。

## 名称与历史

当前项目为 [codecopilot-skills](https://github.com/jasperhan99/codecopilot-skills)；独立个人技能集合建议命名为 **agent-skills**。
安装不会擅自重命名远程仓库。

旧版文档和 pi 适配层归档在 `docs/legacy/`。
之前两轮配对实验中，优化版平均约 223 秒，原版约 244 秒，属于温和改善，
不是稳定的提速承诺。见[实验摘要](docs/BENCHMARK.md)。

包本身采用 [MIT](LICENSE)；迁入的第三方技能保留原许可。
