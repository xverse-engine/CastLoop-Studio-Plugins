---
name: studio-creation
description: Use when the user wants to find a saved CastLoop Studio SIT story, read its content or assets, or edit supported characters, locations, items, world settings and outline entries, or generate standalone text, images, speech, music and video through connected MCP tools.
---

# CastLoop Studio SIT story editing

Use the connected CastLoop Studio SIT MCP tools. This plugin operates on the test environment only.

## Project JSON import/export (only when exposed)

Use exportStory for saved portable JSON. It returns downloadUrl (one hour), expiresAt, filename and bytes. Download directly to a user-selected file without printing or loading the document into model context. It contains media references, not packaged bytes. Browser changes must be saved first; no ZIP or published build.

For import, get ONLY the byte size of the user-selected JSON file. Call prepareStoryImport(bytes). Use a local HTTP client to PUT the exact file to uploadUrl with ALL returned headers, including Content-Length and private ACL. For example curl.exe --fail --silent --show-error --request PUT --upload-file <path> with the returned headers. Do not print/read the JSON into context or base64-encode it. After successful HTTP upload call importStory(uploadId, name?). Clients without local upload capability must report that limitation and use Studio, not pretend to upload.

Import creates a NEW owned unpublished story, never overwrites, copies Studio media under existing quota, preserves external references, and detaches old tasks. No AI charge. Default JSON file limit is 20 MiB (server configurable); MCP arguments stay small. No ZIP. Temporary objects are cleaned after 24 hours by an hourly sweep. URLs and uploadId are temporary credentials: never publish them in reports. Keep the new storyId and read back graph/assets. Import is not idempotent: after uncertain save check returned storyId or search listStories before retry. If tools are absent report deployment mismatch, never use raw save APIs.


## Workspace and task management (only when exposed)

Use createStory for an explicitly requested new empty draft, and copyStory for a new unpublished copy of an owned story. Keep the returned storyId; do not silently switch the established target. Neither operation is idempotent: after a timeout search listStories before repeating. Copying a collaborator's story is not supported in this batch.

Use uploadStoryAsset with filename and exactly one public sourceUrl (up to 32 MiB) or base64 (up to 512 KiB decoded). Supported formats are PNG/JPEG/WebP, MP3/WAV and MP4/WebM. Do not read or upload unrelated local files. Larger local files require Studio's upload UI/API, not splitting into multiple fake assets. Successful uploads appear on the canvas. If applicationStatus=pending, retain assetId and retry applyStoryAsset instead of uploading again. This applies an existing story-owned asset to canvas, an image target or default BGM. Read the exact entity and character phase/state first. It does not generate, crop avatars, split dialogue frames or bind videos to dialogue nodes.

readGenerationTasks lists the current account's MCP image, story-subgraph and standalone media tasks; use retained taskIds for exact queries, since the default list is bounded active/recent records. manageGenerationTask applies only to individual MCP image tasks. cancel stops pending work only and does not promise a provider abort or refund. retry_application saves an existing successful result without new generation. retry_generation requires a failed task, explicit user intent for a new charge, allowNewCharge=true and a new stable requestId. Verify uncertain provider outcomes first; do not automatically retry failure or running tasks. Reuse that requestId for transport retries. This creates a new node/task while retaining the original. Subgraphs resume with original composeStoryFlow arguments, not this image control tool. Check actual status/read back; accepted is not saved.

## Establish the target

Use the story ID explicitly provided by the user or already established in the conversation. If the user provides a story title or asks for their stories, use `listStories` when the connected server exposes it. Omit `query` to list stories or provide a title substring to search. Results are saved metadata, not story documents. Follow `nextOffset` as needed; do not treat an incomplete page as the complete search result.

Resolve the target from returned `storyId` and `title` values. Duplicate titles remain separate stories: present the IDs and update times and ask the user to select when ambiguous. Do not choose a story merely because it is first or most recently updated. If no appropriate story is found, ask the user to clarify rather than guessing an ID. Recheck live permissions through the requested read or edit; search results do not grant access. A user's open editor page is not proof of the target story or its saved state.

Older server deployments may not expose `listStories`. In that case, explain the limitation and ask for the explicit story ID; do not bypass the MCP connection with archive HTTP APIs.

Use the host's account connection flow for login and consent. Never request passwords, cookies, bearer tokens or API keys in chat. Do not bypass this plugin with raw HTTP or use the user's local credential files.

## Connection and authorization recovery

If no CastLoop tools are available, use the host's supported tool discovery first. An empty tool list alone does not prove token expiry or a server outage. If the host reports authentication required or an expired/rejected token, tell the user to open the MCP server connection for CastLoop Studio SIT and use its Authenticate/Reconnect action. Prefer a host-provided authorization button or link when available; never invent an OAuth URL, reuse an old authorization URL, or present the Studio homepage as an MCP authorization link. The callback, state and PKCE belong to the host. If the tools remain absent after authentication, ask the user to start a new conversation and check again.

Distinguish permission errors (insufficient_scope/forbidden) from token errors; do not repeatedly request login for an operation the account cannot perform. Do not claim this skill automatically refreshes credentials: refresh is handled by the client and authorization server. After connection recovery, read back any write whose outcome was uncertain before continuing; never automatically replay creation or generation. Report connection verification separately from story read/write verification.

## Item images (only when exposed by the live server)

Use `generate_item_images` for explicitly requested images of existing saved items. Read the target story/items first. Pass exact `storyId`, `targets: [{itemId}]`, `mode`, `requestId`, and `reason` according to the live schema. `fill_missing` preserves existing images; `regenerate` replaces selected item images. Prompt preparation and image generation can incur charges; do not infer image generation from requests to edit item descriptions.

Choose one unique requestId for each intended generation and keep it in the task record. `accepted` only acknowledges submission: poll `readImageTasks` using returned taskIds with reasonable intervals. Report saved, failed and application_pending separately. If application_pending, repeat the original requestId/targets/mode to retry saving the existing result without generating again. Never change requestId automatically after a timeout or failure. A new paid generation requires user intent. Do not call generic HTTP task endpoints or consume backend-owned tasks.

The backend saves item imageUrl, linked canvas media and image history without an open editor. Ask the user to save and close the same Studio story before testing and reload after completion; concurrent Studio autosave conflicts remain unresolved. Backend restarts do not guarantee automatic continuation. Only use these tools when actually available; do not treat this instruction as proof of deployment.

## Cover image (only when exposed)

Use `generate_cover_poster` for an explicitly requested single story cover. Pass storyId, mode, requestId and reason. Optional referenceImageUrls overrides default references; [] means no references. Without an explicit selection, the server prefers main-character artwork followed by saved cover references. Artwork is not required. Follow the live schema: this initial implementation uses the fixed default image model, not the browser's selected model.

Use the same accepted/taskIds/readImageTasks polling and retry rules as item images. Cover application saves coverPoster, linked canvas media and history. Do not automatically generate a cover when only item images were requested. No browser needs to remain open; save/close and reload Studio for comparison.

## Location images and dialogue frames (only when exposed)

Use `generate_location_images` for explicitly requested images of saved locations. Read locations first; pass `storyId`, `targets: [{locationId, assets: ["preview", "multiView"]}]`, `mode`, `requestId` and `reason`. Either asset can be requested independently. A requested multiview automatically generates its missing main image first; when both are regenerated, multiview references the new main. Regenerating only the main preserves the existing multiview. Do not infer image generation from location text edits.

Use `generate_dialogue_frame` for one explicitly requested dialogue frame. Follow the live schema for optional referenceImageUrls: omission uses the saved cover, [] disables references. The server saves the complete nine-slice frame and selected URL, preserving theme/font. Do not treat a plain image as a complete dialogue frame.

Both tools incur prompt/image charges and use the item-image submission and recovery rules. Keep original requestId and arguments. Poll returned taskIds in groups of at most 100 until saved/failed; a failed predecessor blocks its dependent image. For application_pending, poll again before repeating the original request to finish application. The server saves asset fields, canvas and image history. Save and close the same Studio story before generation; reload after completion. These instructions require live tool availability, not merely this plugin version.

## Character and all images (only when exposed)

Use `generate_character_images` with explicit storyId, targets (characterId, optional exact phase/state, assets: illustration/avatar/turntable), mode, requestId and reason. Read phase/state names first. Omission selects the default phase/state. Avatar is shared by all states of a phase: request it from only one state per phase. A missing illustration is generated first; avatar and turntable use that cell's raw illustration. Avatar cropping does not call a paid image model. Illustration height processing may fall back to the original with warnings; report the warning without automatically regenerating. The backend saves image matrices, history and canvas. Narrator id=1 is protected. Changed phase/state axes can prevent writing: read back and report rather than silently selecting another cell.

Use `genAllImages` only when the user requests all five image categories for the story. It includes default-phase/state character illustration/avatar/turntable, location main/multiview, item previews, one cover and one complete dialogue frame. It does not generate every character variant. `resume` fills missing outputs; `regenerate` replaces all and needs explicit replacement intent. At most 100 assets per category. Optional coverReferenceImageUrls and dialogueFrameReferenceImageUrls override defaults; [] disables references. Default cover waits for newly generated protagonist artwork, and default frame waits for the new cover. A failed reference blocks dependent generation.

Keep the original requestId and all parameters. Retrying the same request uses its frozen plan and cannot include assets added later. New assets require an explicitly intended new request. Poll taskIds in chunks of at most 100; accepted is not completion. Do not promise restart takeover or cancellation. Report failed, saved, application_pending and warnings individually. Never use raw HTTP to fill missing tools on older deployments. Caster already provides these tools; this plugin's instructions guide external agents and do not change Caster's tool list.

## Read

Call `readStoryCharacters` with `storyId`. It reads the current authenticated user's saved editable draft, not unsaved browser changes. The default page size is 20; follow `nextOffset` when the requested list extends beyond a page. Character IDs for subsequent calls are positive decimal strings; copy them from tool results rather than guessing.

If the user asks only to read or review, do not call a write tool. When necessary, explain that the user should save their editor draft before comparing the results.

## Edit

Call `composeCharacter` with an explicit `storyId`, exact `characterId` (or `new` when creation is supported by the live schema), requested changes and a short `reason` grounded in the user's instruction. Resolve an existing character through a prior read when its identity or current fields are unknown. Ask for clarification only when the target or requested change is ambiguous.

Follow the live tool schema. Older deployments support only exact `updates.name/persona/age/targetHeightCm`; do not send newly supported parameters to them. Newer deployments also support `fields.name/persona/voiceProfile` generation instructions, voice/TTS settings and `phaseOperations/stateOperations`. Omit all unrequested fields. Empty persona or age clears it, so do not send empty placeholders. The default Narrator is protected.

Use `updates` for exact final values and `fields` for generation instructions, not both for the same text. Generation can incur charges. For `characterId=new`, omit voiceId and voiceSelectionMode: the server selects a voice. For existing characters, edit voiceProfile/voiceDescription without automatically changing the assigned voice; request `voiceSelectionMode=auto` only when matching is intended. Use `voiceSelectionMode=exact` plus a known voiceId for exact selection, never invent a catalog ID. TTS settings do not generate speech audio.

When the live tool explicitly documents it, exact updates with ttsLanguage=other and no fields create a character without model calls or voice selection. This creates a character with no assigned voice; do not choose other for users who requested a supported speech language merely to avoid a charge. Adding fields still requests text generation. Supply at least one effective change.

Batch phase/state operations use add/update/remove. Only update may include a replacement name; remove omits description. Operations run phases first, then states, then settings, saved together. Preserve protected defaults and the five-phase limit. Independent add/remove tools are also available when exposed; do not apply the same change through both paths. Removed references do not mean cloud assets were deleted. After uncertain creation outcomes, read characters before retrying to avoid duplicates.

A successful save returns `status: saved` and a save receipt. Read the affected character back to confirm, then report only the actual changes and the target story. For collaboration, writes affect the caller's editable draft rather than approving or publishing the main version.

If a request times out or its outcome is uncertain, read back before retrying. Do not blindly replay writes, fall back to whole-archive replacement, or claim success without a save receipt. Report permission and validation failures accurately.

## Report changes clearly

Use the actual saved entity name, type and change in user-facing summaries, not internal IDs alone. Keep stable IDs for tool calls, evidence, troubleshooting and disambiguating duplicate names. If shortening a long name or adding a translation, label it as an explanatory short name/translation, not a saved rename. For renames, state the old and new names. Never guess an ID from a name.

For text edits, state the location and a short actual difference, for example “World settings → World rules: appended … at the end”. Do not copy the whole story. Distinguish tool-reported save, independent readback and user-confirmed Studio display. Claim other fields unchanged only when actually compared. Explain retained test changes and incomplete cleanup.

Report only the requested outputs that actually completed. Character profiles, assigned voices, voice descriptions, images, synthesized speech and videos are separate results. An empty image after text-only creation is expected; a selected voice does not imply a voice description or audio was generated. Do not generate paid missing outputs merely to fill an empty card.

`historyVersionKey` is a storage key returned by saving; it can repeat across saves. It is not a unique immutable version or an undo token. Confirm `status=saved` and independently read back affected data; do not infer success/failure from a changed/unchanged key. Skill wording does not prove the server's live tool descriptions have updated.

For acceptance tests, follow the task sheet's short meaningful names and keep the full runId-to-entity-ID mapping in local evidence. Do not rename existing test entities to retrofit the new naming rule.

## Supported execution scope

Only use tools and parameter branches exposed by the connected server. This package's new instructions do not prove server deployment. Do not claim image generation, speech synthesis, publishing or background recovery from profile-editing tools. Do not bypass missing branches with raw HTTP or whole-archive replacement.

## Additional story reads (when exposed)

Use `readStorySections` to read saved story metadata, worldInfo, outline, locations or items. Follow pagination when the requested scope exceeds one page. Outline positions are one-based. Reading an asset does not imply that asset creation, editing or generation tools are available.

Use `readStoryNodes` for explicit relevant node UIDs, or `readStoryGraph` when complete cross-node context is necessary. Use stable node IDs, not display numbers or guessed titles. Respect effective outputs: explicit exits override stale legacy routes; insertion-ending conditions are not normal edges. Components preserve the saved dialogue data, including canonical and legacy representations; do not invent missing branches or IDs.

When available, use server-returned `publication` metadata to check node protection. `published` and `pendingLocked` are separate; published nodes can still allow some edits. `editableFields` / `restrictedFields` cover only `composeStoryFlow.modifyNodes`, not routing, deletion, dialogue or general write permission. A read-only connection still needs write authorization to modify anything. Missing metadata or `status=unknown` does not mean unpublished or unlocked. Readback is advisory: each save revalidates current permissions and publication constraints. For authorized automatic selection of an unpublished test node, require known state, published=false, pendingLocked=false and the requested fields in editableFields; otherwise ask the user to confirm or report the test blocked. Do not probe protection by writing.

If a graph/node result says `complete=false`, inspect its reason, omitted fields and missingNodeIds. Request fewer relevant nodes when detail is too large. Do not claim to have inspected omitted content or silently substitute another story/node.

## Outline changes (when exposed)

Use `patchStoryOutline` only for explicitly requested outline edits. Read the current outline first. Apply operations sequentially with one-based positions; update/remove must include the exact expectedName at that position after prior operations. Rename a chapter in place rather than adding a replacement. Do not infer deletion from omission. Omit remainingRequest: it is a Caster follow-up field, not an MCP execution instruction.

This tool modifies the outline, not graph nodes or published content. Require the returned saved status and receipt to report a save. After uncertain outcomes, read back before retrying; replaying an add operation can create duplicates. If the requested tool is absent, explain the current server limitation instead of editing an archive through raw HTTP.

## Asset and world composition (when exposed)

Use composeLocation/composeItem/composeWorldSetting only when exposed and requested. Read current sections first for existing targets, use stable IDs, and follow the live schema for new versus existing and modify versus rewrite. These tools compose asset/world text, not images. Generation may incur charges; require a saved receipt and read back the requested changes. Do not infer that character completion enables story graph writes, project creation/copying, or generation task management.

## Exact story node edits (when exposed)

Use composeStoryFlow only for branches exposed by the live schema. The modifyNodes branch edits existing section name, description, isKeyNode, isEnding and hintBeforeChoice with exact values. Read node UIDs and current fields first; do not use display numbers. Each node appears once per call. Preserve unrequested fields and verify the saved receipt followed by readStoryNodes. isEnding only changes the legacy flag, not actual routing or explicit exits; do not use it to claim connections were removed. Never substitute patchStoryOutline or raw archive writes for missing operations.

If the live schema exposes addNodes, use it for explicitly requested exact new section nodes, not AI generation. Provide name and optional synopsis, existing entry/exit UIDs, choice text and position. Additions, modifications and explicit deletions share a maximum of 100 operations per call. An existing start successor must be the insertion exit; do not insert twice from the same start in one call. Ending additions ignore the exit. New nodes contain no dialogue. Check addedNodeIds, saved receipt, and read back the new nodes plus modified anchors. Existing publication protections still apply; modifyNodes editableFields do not authorize routing changes. Repeating addNodes creates more nodes, so read back after uncertain outcomes before retrying. Older servers without addNodes cannot create nodes. Independent choice/routing edits, dialogue editing and subgraph generation remain unavailable unless the live schema explicitly exposes them.

If deleteNodes is exposed and the user requests deletion, read the relevant nodes and incoming/effective routes first. Use disconnect to clear incoming targets, rewire with a surviving rewireTargetId, or auto to connect only when there is exactly one surviving successor (otherwise disconnect). cascadeDelete defaults false; enable it only when deleting orphan successors is within the user's request. It can delete more nodes than explicitly listed. Starts, insertion endings, operation anchors and rewire targets are protected from cascading; starts and operation anchors cannot be explicitly deleted. Read deletedNodeIds and verify remaining routes, including timed choices and game exits. This does not delete COS media or populate browser trash; do not promise undo. If the save outcome is unknown, read back before taking further action. Missing fields or unavailable older servers are not permission to bypass MCP with raw archive writes.

## Choices and dialogue content (when exposed)

Use addChoices/modifyChoices/deleteChoices for requested text and normal targetNodeId changes (-1 clears the normal target). Preserve timeout routes; game exits and insertion-ending routes are not editable through these branches. Read actual choice IDs first.

Use addDialogueComponents/modifyDialogueComponents/deleteDialogueComponents for requested content. Read the actual component and branch first; branchId selects the branch, otherwise the first unconditional branch (or first branch) is used. dialogues replaces that branch's entire line list, with new IDs and without old line audio; omit it to preserve lines. rawText is exact text, not automatic script parsing. Other branches and media remain. Use known character/location IDs from this story. Real new dialogue removes original template placeholders. Do not send a component in both deletion and modification.

All exact node/choice/dialogue lists share a 100-operation cap. Use IDs returned by one call in later calls, not guessed IDs within the same batch. Read contentChanges and the saved receipt, then read back affected nodes. Unknown outcomes require readback before retry; no automatic replay of creation. Publication metadata for modifyNodes does not grant dialogue/routing permission.

## AI story subgraphs (only when exposed)

Use composeStoryFlow.generateSubgraphs only when the live schema exposes it and the user requests AI-generated plot. This is a paid text-generation operation, separate from exact node edits and image generation. Save and close the same Studio story before acceptance testing; MCP reads saved content, not browser changes. Use one subgraph per call, with storyId, reason and a unique requestId, and do not mix it with exact edit lists.

Read the actual entry/exit nodes and publication metadata first. Require known, structurally editable entries; unknown status is not permission to write. Starts with an existing successor must include that successor among exits. Defaults are nodeNum=5, layerNum=3, endingNum=2 and expandDialogue=false. Counts must follow live limits; endingNum counts generated graph terminals including returns to supplied exits, not necessarily story endings. The server uses its default text model and saved story language/context. expandDialogue generates text mapped to existing characters, without creating characters, binding locations, synthesizing speech or generating images.

Keep the exact requestId and arguments in the task record. A saved result includes taskId and added/modified node IDs; read back nodes and routes independently. If a save response was lost, a recovery may return readBackVerified=true instead of a historyVersionKey. Do not fabricate a receipt. Repeat the original request only to retrieve its result or apply a retained generated result, never change requestId automatically. request_id_conflict means the arguments changed; generation_target_changed means the story targets changed; generation_not_resumable means running/interrupted/failed and does not authorize another paid generation. Report the error and ask for user intent before a new request. Deduplication lasts only while task records are retained; do not replay old archived requests as if permanently idempotent.

This is synchronous generation with durable result recovery, not a guarantee of unattended completion after disconnect/restart. Do not poll readImageTasks for story subgraphs. Missing schema on an older server is BLOCKED, not permission to call raw HTTP. Caster keeps its own existing confirmation and browser application flow.

## Standalone generation (only when exposed)

Use generateMedia for standalone text, image, speech, instrumental music or text-to-video. It still requires an editable saved storyId for ownership and billing, but no characters, graph or reference images. Resolve the intended story first; create an empty story only if requested. Do not confuse generic images with the asset-specific image tools that also update characters/locations/items/covers/dialogue frames.

Obtain authorization for paid generation, keeping already authorized scope and budget. Supply a stable requestId per intentional generation and preserve the exact arguments for transport retries. Record taskId immediately. Repeat the same request to recover the task; changing arguments with the same ID conflicts. Failed/interrupted tasks are not automatically regenerated. Never change requestId just to work around a timeout. Idempotency is limited by task retention, not permanent.

For speech, prompt is the exact text to speak, not an instruction to rewrite. Supply a known valid voiceId and language (zh-CN/en-US/ja-JP); use an existing character voice or a user-provided valid ID, never invent one. Voice search is not added by this package. For image/video only, aspectRatio is optional (default 16:9). For video only, durationSeconds is 4–10 (default 5), resolution is 720p. Music is instrumental. Other model/provider options and reference-media video are not exposed in this batch. Do not send irrelevant options.

Poll readMediaTasks with the returned taskIds, at a reasonable interval (e.g. 10–15 seconds), stopping on final success/failure. A query error is not generation failure and must not trigger new generation. Video acceptance/submission is not completion; its final status and URL come from readMediaTasks. readGenerationTasks can find recent tasks and points to this result tool. manageGenerationTask remains limited to the documented asset-image tasks, not these standalone requests.

On success, report the generated text or media URLs. These results do not automatically replace story content and do not provide a save receipt. The existing music service may also record generated music in the music library. If the user asks to use a result on canvas or a supported asset/BGM target, explicitly call uploadStoryAsset/applyStoryAsset and verify the saved application separately. Respect the upload size/format limits; a video result does not mean it has been bound to a story dialogue. No publishing, universal cancellation, automatic paid retry or restart takeover is implied.
