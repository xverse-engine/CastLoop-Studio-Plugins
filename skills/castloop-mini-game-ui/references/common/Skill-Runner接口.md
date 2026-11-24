# 自定义小游戏 Skill 接入契约

随 Skill 分发的接口快照，与 XNarratorServer 的 `docs/mini-game-skill-runner-api.md` 同步。下文“本仓库”指创作端后端 XNarratorServer；Skill 本体在本包 `skill/castloop-mini-game-ui/`。后续接口变更应同步此快照，配置中的版本仍为 1.2。

## 范围

本阶段支持**提交生成、恢复/查询任务、项目素材库查看、跨节点选择、参数表单编辑、草稿保存与 H5 模拟预览**。Editor 入口是节点互动编辑器 → 小游戏素材下拉框 → 自定义，选中后才显示创作表单。创作者只填写玩法描述，无需编写 JSON；Skill 同时生成 H5 包、游戏参数及关键参数表单定义。新增创作入口沿用前端 SIT 开关；后端接口不按 SIT/PRD 裁剪。

调用关系：Editor → XNarratorServer（登录、作品权限、任务记录）→ 受信任 Skill Runner（安装 Skill、调用模型/工具、生成及验证 H5 包）→ 独立游戏资源域名 → Editor 沙箱 iframe。

Skill 是生成规范，不是 HTTP 执行器。开发同事需要部署最终 Skill/references、模型工具执行环境，并实现下述 Runner 协议；只复制 SKILL.md 不会自动生成游戏。本仓库不内置最终 Skill、模型密钥或生成的 H5 副本。生成结果自动进入所属项目的小游戏素材列表；作者显式选择后写入当前互动草稿，不自动覆盖其他节点。不登记消费端游戏或自动发布。Caster/MCP 暂不增加工具，后续可复用此业务接口。

## 部署配置

```dotenv
# 留空 URL 时关闭生成能力，不影响原有故事功能。
MINI_GAME_SKILL_RUNNER_URL=https://internal-runner.example/api/v1
MINI_GAME_SKILL_RUNNER_TOKEN=<server-only-secret>
MINI_GAME_SKILL_ID=castloop-mini-game-ui
MINI_GAME_SKILL_VERSION=1.2
MINI_GAME_PREVIEW_ORIGINS=https://games.example
```

生产使用 HTTPS，本地允许 localhost/127.0.0.1/::1 的 HTTP。预览 Origin 可逗号分隔、不能有路径，必须是与 Editor/账户服务隔离且无登录 Cookie 的资源域名。启用 URL 后缺少其他合法配置会拒绝启动。`available=true` 仅代表配置齐全，不是 Runner 探活或真实生成成功的证明。

复用 generation_tasks，无新数据库迁移。POST 沿用 JWT 和 AI 余额守卫，再检查作品编辑权限。Runner 必须复用平台批准的供应商服务、额度与用量记账，按服务端 userId/storyId/taskId 归属；本适配器只提供余额准入与任务记录，不实现 Runner 内部模型计费。不可接入绕过额度的执行器。

## Editor API

前缀 `/api/v1/projects/{storyId}/mini-games`，沿用现有登录认证。身份来自认证上下文，不接受客户端 userId、Skill 名称、执行 URL 或资源白名单。

| 方法/相对路径 | 作用 |
| --- | --- |
| GET `/generation-capabilities` | available、skillId、skillVersion、previewOnly=true、reasonCode |
| POST `/generations` | HTTP 202，返回 `{task}`，同请求 ID/参数返回原任务 |
| GET `/generations?nodeId=1&interactionId=2` | 当前账号/作品/节点/互动的任务 `{tasks:[]}` |
| GET `/generations/{taskId}` | 返回 `{task}`；进行中查 Runner，终态读本地记录 |
| GET `/assets?before=<cursor>` | 项目所有作者成功生成的素材，每页 100，返回 `{assets,nextCursor}`；无节点/互动限制 |
| GET `/assets/{taskId}` | 项目授权后的不可变素材 `{asset}`，用于重新打开和预览 |

asset 为 `{taskId,storyId,artifact,benefitPolicy}`，不含提示词、作者身份或任务请求。成功任务记录作为项目素材保留，不参加临时任务删除；资源域必须相应长期保留包及预览 URL。分页游标是正整数 ID 字符串，不使用短期活跃任务列表。所有读取先校验项目成员权限。

选择素材时，节点草稿保存 `generatedAsset:{storyId,taskId}`、gameId/gameVersion/protocolVersion、克隆的 miniGameData 与 benefitPolicy。各节点参数独立；修改参数不修改原始素材，也不影响其他节点。预览从授权资产接口解析 URL，核对版本身份并校验当前参数，不使用草稿自带任意 URL。消费端登记尚未接入，包含 generatedAsset 的发布请求会明确失败。

提交示例：

```json
{
  "clientRequestId":"uuid-generated-once-for-this-submission",
  "nodeId":1, "interactionId":2,
  "prompt":"制作一个找出三处机关的小游戏，成功后继续故事。",
  "miniGameData":{},
  "benefitPolicy":{
    "defaults":{"diamondCost":10,"freeUses":1,"membership":true,"rewardedAd":true},
    "benefits":{"skip":{"diamondCost":20,"freeUses":0}}
  }
}
```

body ≤64 KiB，prompt 非空且 ≤16000 UTF-8 字节；节点/互动为正安全整数。miniGameData 为不透明 JSON 对象，≤32 KiB、深度≤16，拒绝 prototype 类危险键。nodeId/interactionId 关联当前草稿，本阶段不据此读取/改写后端节点。不会递归把 miniGameData.storyId 当成作品授权字段。

Editor 新请求发送 `miniGameData:{}`，不要求作者编辑参数。API 仍兼容显式覆盖，例如 `{"levelId":2,"difficulty":"normal"}`；重试旧请求时保留原始数据与 ID，不改成新请求。参数生成规则见下文 Runner 契约。

benefitPolicy 沿用宿主 1.1 的 clear/swap/retry/skip；默认 10 钻/1 次/会员可用/广告可用，显式 0 和 false 优先。其他权益键须先扩展平台协议，不能由生成代码自行授予。

任务：`{taskId,storyId,status,progress,request,artifact,previewOnly:true,errorCode}`。status 为 pending/running/succeeded/failed，progress 为 0–100；request 保留原参数。列表沿用现有活跃任务和最近 30 分钟终态窗口，最多读取当前作品最近 100 个同类任务后按互动过滤；按 ID 查询不受列表窗口限制，仍遵循既有任务保留期。

提交仅 creator/admin/editor；查询要求当前作品成员且为任务所属账号。通用 generation_tasks 不能读取/消费小游戏任务。错误：401 未登录，403 无权限，400 无效参数，409 请求 ID 参数冲突，503 未配置，502 查询暂不可用。

## Runner API（开发同事实现）

Server 向配置 URL 下发请求，带 `Authorization: Bearer <server-token>`，禁止重定向，单次超时 30 秒。POST 快速确认接受，耗时生成在后台运行。

### POST `/generations`

带 `Idempotency-Key: <taskId>`；JSON 如下：

```json
{
  "taskId":"mg_<server-derived-id>","userId":"authenticated-author-id",
  "storyId":42,"nodeId":1,"interactionId":2,
  "prompt":"作者的描述","parameterMode":"generate_from_description","miniGameData":{},
  "benefitPolicy":{"defaults":{"diamondCost":10,"freeUses":1,"membership":true,"rewardedAd":true}},
  "skillId":"castloop-mini-game-ui","skillVersion":"1.2",
  "protocolVersion":"1.1","imageFormat":"webp","previewOnly":true
}
```

Skill 标识、版本、协议、图片格式、parameterMode、previewOnly 由 Server 固定。缺省 benefitPolicy 使用上文默认值，显式参数优先。Runner 先持久化 taskId，并保证重复请求不会启动第二次生成/收费，再返回 HTTP 200/202：`{"taskId":"mg_...","status":"running","progress":10}`。

`parameterMode=generate_from_description` 是 Skill 的必需执行约定：

- 根据 prompt 推导关卡、难度、目标、次数等该游戏实际需要的参数，同时生成读取这些参数的 H5；不得要求作者补写 JSON。
- `miniGameData` 是 API 可选的显式覆盖内容，不是生成结果。优先级为显式覆盖值（包括 0/false）→ 描述中指定的要求 → Skill 默认值；不同游戏自行定义数据结构，Server 不展开解释。
- 将完整、可运行的最终参数放进 `artifact.miniGameData`，与本次 H5 包保持一致。成功前用这些参数验证页面初始化与玩法；不能只返回空占位参数而要求前端填充。
- Editor 预览自动传递 `artifact.miniGameData`，不回退到原请求的空对象。权益仍遵守独立的 benefitPolicy 与平台回调，参数生成不允许绕过扣款、会员或广告校验。

### GET `/generations/{taskId}`

返回 HTTP 200 当前状态；失败用 status=failed，Server 对外只给固定错误码，不透传供应商密钥、堆栈或内部提示词。成功结构：

```json
{
  "taskId":"mg_<server-derived-id>","status":"succeeded","progress":100,
  "artifact":{
    "gameId":"custom-puzzle-unique-id","gameVersion":"1.0.0","protocolVersion":"1.1",
    "displayName":"机关试炼",
    "packageRoot":"stories/42/mini-games/custom-puzzle-unique-id/1.0.0",
    "previewUrl":"https://games.example/stories/42/mini-games/custom-puzzle-unique-id/1.0.0/index.html",
    "miniGameData":{"levelId":2},
    "editorSchema":{"version":1,"fields":[{"path":["levelId"],"label":"关卡","type":"select","options":[{"label":"第一关","value":1},{"label":"第二关","value":2}]}]},
    "files":[{"path":"index.html","bytes":1024,"sha256":"<64 lowercase hex characters>"},{"path":"cover.webp","bytes":2048,"sha256":"<64 lowercase hex characters>"}]
  }
}
```

每个游戏独立目录，与 storyId/gameId/gameVersion 一致；每次生成用新 ID 或新版本，不能覆盖旧包。清单必须包含 index.html 和素材库卡片封面 cover.webp；无重复/越界路径；≤256 个文件、总计≤20 MiB。图片仅 WebP；其他可用 HTML、JS/MJS、CSS、JSON、WOFF/WOFF2/TTF、MP3/OGG/WAV、MP4、TXT。

新生成结果必须提供非空 displayName 和 editorSchema（version=1、fields 数组最多 32 项；确实无需参数时 fields=[]）。字段声明 path（1–8 段对象键）、label、type，可选 description、min/max、maxLength、options。type 仅 string/number/integer/boolean/select；下拉选项为 `{label,value}`，value 仅字符串或有限数字。每条路径必须已存在于 miniGameData，默认值符合类型、上下限和枚举；禁止原型键、重复路径、代码、动态组件或 HTML 表单。重要参数由 Skill 声明，隐藏数据原样保留，编辑器不推测游戏内部结构。历史已保存但缺少 schema 的素材只提供默认参数预览，不提供 JSON 输入框。

Server 检查清单、URL 白名单、扩展名、大小/哈希格式与参数，**不下载产物核验字节**。Runner 必须验证真实 MIME/文件头、大小/哈希和所有资源引用（含内嵌图像），保证图片同精度 WebP、协议兼容、无外部支付，再报 succeeded。资源域配置相应 CSP/CORS，使 opaque-origin iframe 可加载资源；限制网络、导航及账户访问。预览 URL 必须覆盖约定保留期，不能返回很快失效且无法刷新的地址。

## 重试与恢复边界

- 先存请求再提交 Runner。同账号/作品/clientRequestId 派生同 taskId；不同参数 409，JSON 键顺序/MySQL 格式化不影响幂等。
- 提交超时保留原任务和 MINI_GAME_SUBMISSION_UNCONFIRMED；查询失败暂停自动轮询，可手动重试，不另起生成。Runner 对确定未接受的任务须返回明确 failed；状态未知时不能假报失败允许再次收费。
- Runner 是执行状态来源，小游戏任务不参加本地 worker 的 12 分钟失活判失败；关闭重开可再查询。成功任务作为项目素材保留，其他终态仍按既有保留期清理；未实现后台自动接管、取消或跨任务重新生成的原子事务。
- 预览使用 BrowserMergeGame 的 `sandbox="allow-scripts"` 与私有 MessagePort，不启用 same-origin、弹窗/导航权限，前端再次拒绝 Editor 同源 URL。
- mock host 模拟存档、结果、钻石、会员、广告；可以切换模拟会员/广告可用。不扣真实钻石、不播放真实广告，不代表消费端上线验收。

## 联调

开发同事部署 Skill Runner/独立游戏资源域 → 配置五个环境变量 → SIT 编辑器打开自定义小游戏面板 → 提交描述、观察进度与预览 → 验证网络中断、关闭重开、切换故事、无权限账号、模拟权益回调。确认当前互动没有被替换。

本阶段用 fake Runner 和 mock host 验证接口；真实模型生成、资源部署及模型费用链路仍需部署后联调。故事草稿可选择生成素材，消费端登记和正式发布另行接入。
