---
name: castloop-mini-game-ui
description: 根据作者的玩法、UI 和故事资料设计、制作或修改可试玩的 H5 小游戏，生成可复用的 Studio 运行包。
---

# 小游戏创作

先阅读当前对话、附件、设计文档、UI 稿和已有故事选区。提到的资料尚不可读时，请作者指出位置。Caster 可使用消息附件和可读取的画布素材，MCP 可使用本地文件和 Studio 故事。先核对内容，再归纳已知要求。

只询问会影响成品的缺项。确认玩家目标、输入操作、反馈、胜负条件、时长、难度与可调整参数。确认视觉风格、布局、关键状态和需要制作的素材。作者已给答案就沿用；作者委托设计时提出可试玩的方案。Caster 可用选项卡收集选择。按需确认存档、权益和故事去向。

## 制作与试玩

实现可操作的开始、进行、结果和退出流程。优先使用已有素材和 Agent 自带的生成能力，Studio 素材工具兜底。将一张静态 WebP 封面放在根目录 cover.webp 并列入 runtimeFiles。用 miniGameData 和 editorSchema 描述默认参数与可编辑字段，运行时读取宿主 initialParams。

在 MCP 本地工程以 game-package.json 声明入口、宿主桥、能力、结果码、权益、存档版本和全部运行文件。执行：

    node scripts/validate-runtime.mjs <工程目录>
    node scripts/assemble-runtime.mjs <工程目录> <独立输出目录>

组包时会再次校验，输出 mini-games/<gameId>/<gameVersion>/ 和 generation-manifest.json。Caster 在草稿卡试玩，保存时由 Studio 的 Go 后端校验和组包。分别实玩各结果路线、退出和参数变体，区分静态检查和实际试玩结果。

## 参数、权益和章节隔离

每个插入点使用自己的参数。权益由平台决定，保留显式 0 和 false。按宿主协议提交结果，由故事决定去向。按需查阅 references/common 中的宿主协议、商业与权益、存档与发布、全局UI、自然语言创作、生成与验收。

记录作者指定的去向，尚未指定时在成品试玩后选择本地交付、个人库、项目库或应用到节点。写入节点前核对故事、内容段和具体位置，写入后读回资产、参数和位置。
