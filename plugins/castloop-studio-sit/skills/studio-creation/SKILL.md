---
name: studio-creation
description: Use when the user wants to find a saved CastLoop Studio SIT story, read its content or assets, or edit supported characters, locations, items, world settings and outline entries through connected MCP tools.
---

# CastLoop Studio SIT story editing

Use the connected CastLoop Studio SIT MCP tools. This plugin operates on the test environment only.

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

All node/choice/dialogue lists share a 100-operation cap. Use IDs returned by one call in later calls, not guessed IDs within the same batch. Read contentChanges and the saved receipt, then read back affected nodes. Unknown outcomes require readback before retry; no automatic replay of creation. Publication metadata for modifyNodes does not grant dialogue/routing permission. AI subgraph generation remains unavailable.
