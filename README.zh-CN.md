# 多 Agent 开发流程

[English](README.md)

只有一个文件 [WORKFLOW.md](WORKFLOW.md)，任何 AI 编码 agent 读完就能照做：

**计划 → 你批准 → 实现 + 真实检查 → 独立审查（最多 3 轮）→ 你授权合并/推送。**

没有安装器、没有脚本、不依赖任何插件。委派模型任务统一通过 pi CLI 调用，需要先安装 pi 并配置认证。适用于 Claude Code、Codex、Cursor、Gemini CLI、pi、Copilot，以及任何会读取项目指令文件的 agent。

## 快速开始

在你的 AI agent 里打开项目，粘贴：

```text
Set up this workflow in my project: https://github.com/jasperhan99/multi-agents-workflow
```

agent 会先给你看改动，再加两样东西：项目根目录的 `WORKFLOW.md`，以及它所读指令文件里的一行引用。之后正常提需求就行，例如"给 CLI 加一个 --verbose 参数"。它会先出计划，等你回复"好"再动手。

以后要更新，再粘贴同一句话即可。给 agent 看的详细安装步骤在[英文 README](README.md#setup-instructions-for-ai-agents)。

## 手动安装

```bash
curl -fsSL https://raw.githubusercontent.com/jasperhan99/multi-agents-workflow/main/WORKFLOW.md -o WORKFLOW.md
```

```bash
echo "Before any development task, read WORKFLOW.md and follow it." >> AGENTS.md
```

如果你的 agent 读的是 `CLAUDE.md`、`GEMINI.md` 等文件，就把 `AGENTS.md` 换成对应文件。

## 工作方式

- **任务文件** `workflow/T-NNN-*.md` 记录每个任务的计划、批准、检查结果和审查结论，是唯一的事实来源；新会话从这里恢复。
- **独立审查**：审查者不能是写代码的同一个上下文。协调者通过 pi CLI 启动全新的只读会话，并明确指定 provider 和模型。pi 不可用时报告阻塞；只有你明确授权，才改用手动新会话审查。
- **你始终掌控**：没有你的明确答复，不会合并、推送或部署；产品、安全、架构等高风险决定会先问你。

WORKFLOW.md 用英文写，agent 会用你的语言回复。这是给 agent 的指令，不是强制机制；需要真正保证时，用分支保护、CI 和最小权限凭据。

## 模型配置与选择

在项目的 `AGENTS.md` 里为每个角色指定模型。协调者每次调用 pi 都会显式传入这些值；没有这张表时，会先问你：

```markdown
## Workflow models
| Role | Provider | Model | Thinking |
| --- | --- | --- | --- |
| Implementer | anthropic | claude-sonnet-5-5 | medium |
| Reviewer | openai-codex | gpt-6-sol | high |
```

- **实现者**：选快、便宜、够用的编码模型。一个任务的大部分 token 花在这里。
- **审查者**：能力不低于实现者，最好换一个模型家族，避免和作者有相同的盲点。它只读 diff 和证据文件，输入很小，用强模型成本也不高。
- **thinking 等级**：可选 `off` 到 `max`；一般实现用 `medium`，审查用 `high`。
- 用 `pi --list-models` 查看你能用的模型 ID，用 `pi auth check --provider P --model M` 确认凭据可用。协调者不会依赖 pi 的默认模型，也不会在失败时悄悄换模型。

## 为什么用 pi 调用不同模型

- **一个 CLI 覆盖多家模型**：Anthropic、OpenAI（含 Codex 订阅）、Google、智谱以及各类网关，都用同样的 `--provider` / `--model` 参数。换审查模型只需改表里一行。
- **与宿主 agent 无关**：Claude Code、Codex、Cursor、Gemini CLI 都能执行 shell 命令；各家原生 subagent 不通用，而且大多只能用自家模型。
- **隔离看得见**：`--print --no-session` 保证全新、不保存历史的上下文，审查时禁止 `--continue` / `--resume` / `--fork`；`--tools read,grep,find,ls` 和 `--no-extensions` 让审查者没有 shell、不能改文件。
- **可审计**：每次调用就是一条命令，任务文件记录角色、模型、thinking、命令（不含密钥）、退出码和结果。

## 对长任务的好处

- **状态在文件里，不在对话里**：计划、批准、决定、检查结果、审查结论都写在 `workflow/T-NNN-*.md`，代码在 Git 分支上。换会话、换 agent、电脑重启后都能接着做。
- **每个 worker 都从干净的上下文开始**：没有越来越长的历史，也没有压缩（compaction）丢信息；第 3 轮审查和第 1 轮一样清醒。
- **协调者上下文增长很慢**：它只收到简短报告（改了哪些文件、检查结果、结论），而不是实现者全部的读文件、跑测试记录。
- **有上限**：最多 3 轮审查，之后交回给你，不会无限循环烧 token。大需求自然拆成多个任务文件分别完成。

## 为什么省 token

普通的长对话每一轮都要把全部历史重新发给模型，越往后每一步越贵。这个流程的做法：

1. 实现者成百上千次工具调用只留在它自己那次调用里，用完即弃，审查者和协调者都不用为它付费。
2. 审查者读的是 diff、改动文件列表和检查结果，而不是产生代码的整段对话。
3. 贵的模型放在输入最小的审查环节，便宜的模型做输入最大的实现环节。
4. 已批准计划里的"不做什么"和"完成标准"减少跑偏返工。

代价也要说清楚：每次全新调用都要重新读 WORKFLOW.md、任务文件和相关代码，所以一行的小修改用单个 agent 更省；任务越长、风险越高、跨会话越多，这个流程越划算。

完整说明（选型示例、取舍、故障排查）见英文[指南](docs/GUIDE.md)。

## 适配层（可选）

- [pi](adapters/pi/README.md)：`pi-dev` / 只读 `pi-qa` 两个 subagent 和一个 `/wf` 命令。

## 许可

[MIT](LICENSE)
