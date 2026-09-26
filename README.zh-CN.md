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

## 适配层（可选）

- [pi](adapters/pi/README.md)：`pi-dev` / 只读 `pi-qa` 两个 subagent 和一个 `/wf` 命令。

## 许可

[MIT](LICENSE)
