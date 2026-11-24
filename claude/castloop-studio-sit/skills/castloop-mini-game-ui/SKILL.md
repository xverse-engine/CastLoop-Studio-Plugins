---
name: castloop-mini-game-ui
description: 为 CastLoop Studio SIT 故事创作、预览或修改 H5 小游戏，也可根据提供的玩法资料整理独立玩法包。
---

# 小游戏创作

先读同目录的[原版制作指引](author-guide.md)，按其中的任务路由、设计提问、素材要求、验收及交付流程执行。涉及玩法目标、胜负条件、商业规则或故事去向的关键缺项，沿用原版的提问方式；普通默认值放进可编辑草稿。

## 故事输入

- 作者要新增独立玩法时，按原版“新增玩法”流程使用作者提供的资料。无需 storyId 或 Studio 连接。没有故事资料时交付玩法包；只有明确要求实现时才附独立引擎和测试。此时止于玩法阶段。
- 作者要为已有 Studio 故事制作时，沿用已指定的 SIT storyId；只给标题时用 listStories 定位，同名候选请作者选择。故事目标不明时先澄清，不能仅因消息里没有数字 ID 就切到独立玩法。
- 用 readStorySections 读已保存的故事信息，已知目标节点时用 readStoryNodes，确需跨节点上下文时用 readStoryGraph。依照原版检查封面、调性、字体和已有素材，按需读角色（readStoryCharacters）、地点和道具（readStorySections）。若作者直接提供离线故事资料，可以依原版制作本地故事预览；写回前仍需明确目标故事。

## 素材制作

生成可试玩 H5 时，取能代表本游戏的画面或主题图制作素材库封面，以静态 WebP 写入运行包根目录 `cover.webp`，并在 `runtimeFiles` 中声明。导入前核对封面实际可打开并已进入 generation-manifest.json。

先复用作者提供或已授权读取的合适素材。缺少图片、图像编辑、配音、音乐或其他素材时，优先使用当前 Agent 自带且适合该任务的能力，再依原版脚本加工、验证。只有宿主能力缺失或结果未达到原版验收要求时，才考虑 Studio 工具。

使用 generateMedia 兜底前核对它实际支持所需的素材类型，并确认可编辑的目标故事和付费授权。向作者说明成功结果会保存到该故事画布；没有已授权的目标故事时，保留本地进度并说明缺项。保留返回的任务 ID，用 readMediaTasks 查询已有任务，避免重复生成。

## 成品去向

开始时记下作者明确指定的交付位置和节点；去向未定可以先制作。读取故事仅授权取得本次需要的上下文。按原版完成相应交付物后，报告本地位置、版本和验证结果。独立玩法包与可试玩的 H5 成品分别标明。

对于可导入的游戏成品，按当前连接实际开放的工具确定可执行的去向：
- 作者已明确要求留在本地、存入个人库、存入某项目或应用到指定节点时，沿用该决定；只有目标有歧义或需覆盖已有内容时才澄清。
- 去向尚未决定且有可用的写入工具时，展示成品后一次询问去向。留在本地即可结束；存个人库用于跨故事复用；存项目库需要目标故事；应用到故事还需要目标节点。允许同时选择个人库与项目用途。
- 按选定范围写入并读回，分别报告入库结果与节点应用结果。仅要求入项目库时，到入库为止。

## Studio 成品入库与应用

先检查当前 SIT 连接暴露的工具。本地交付到此即可；选择云端时只上传原版组包脚本输出的版本目录。把目录内容打成 ZIP，使 index.html 和 generation-manifest.json 位于 ZIP 根层，保留资源相对路径。排除工程源码、私有原图、提示词及测试输出。压缩包与解压后的运行文件各限 20 MiB。

1. 调用 prepareMiniGameUpload(bytes)；本地 HTTP 客户端用返回的方法、地址和全部请求头上传 ZIP 原始字节。收到成功响应后继续。签名地址与 uploadId 仅限本次传输使用。
2. 调用 importMiniGame，提交 uploadId、displayName、与 H5 匹配的 miniGameData、editorSchema。作者已确认的权益参数可随 benefitPolicy 提交，保留显式的 0 和 false。library=personal 时省略 storyId；library=project 时传入明确的目标 storyId。保存返回的 assetId。相同版本内容、参数和目标重复导入可复用同一资产。
3. 用 listMiniGames 按库读回，按 nextCursor 分页。复用已保存资产时直接调用 copyMiniGame：项目来源传 sourceStoryId，个人来源省略；目标使用 library 及相应的 storyId。记录目标库返回的新 assetId。要同时存两处，只上传一次。
4. 应用前用 readStoryNodes 核对内容段、分支、现有互动与出口。按作者指定的位置选择一种：
   - 图文：绑定实际存在的一句对白，使用 after_line 锚点（sectionId、variantId、dialogueId），读完该句后触发。
   - 视频：传 `anchor={type:"video_time",sectionId,variantId,atMs}`，段内时刻以毫秒计。无法核实所选视频时长时停在项目库。
   - 节点出口：传 `exit={nextId,failureNextId}`，分别指定成功与失败去向，全部内容结束后触发。仅在作者同意替换已有选项或游戏出口时传 `replaceExit=true`。每次只选 anchor 或 exit。
5. 当前工具不能表达目标位置或缺少定位依据时，保留项目库资产，报告阻塞，停止写入节点。仅接受 triggerAtMs 的工具不能写入对白锚点或节点出口，禁止用 0、任意秒数或估算阅读时长代替。过程互动使用空闲 interactionId，重试沿用相同 ID 和位置。写后读回 generatedAsset、参数、实际位置和原有路由；无法对应真实内容或出现「待定位」「超出当前内容」时，插入验收判 FAIL。

若工具未开放或上传失败，保留本地包并说明哪一步未完成。
