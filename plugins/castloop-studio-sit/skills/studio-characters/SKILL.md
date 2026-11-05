---
name: studio-characters
description: Use when the user wants to read or edit character profiles in a saved CastLoop Studio SIT story through the connected MCP server.
---

# CastLoop Studio SIT characters

Use the connected CastLoop Studio SIT MCP tools. This plugin operates on the test environment only.

## Establish the target

Use the story ID explicitly provided by the user or already established in the conversation. If the user provides a story title or asks for their stories, use `listStories` when the connected server exposes it. Omit `query` to list stories or provide a title substring to search. Results are saved metadata, not story documents. Follow `nextOffset` as needed; do not treat an incomplete page as the complete search result.

Resolve the target from returned `storyId` and `title` values. Duplicate titles remain separate stories: present the IDs and update times and ask the user to select when ambiguous. Do not choose a story merely because it is first or most recently updated. If no appropriate story is found, ask the user to clarify rather than guessing an ID. Recheck live permissions through the requested read or edit; search results do not grant access. A user's open editor page is not proof of the target story or its saved state.

Older server deployments may not expose `listStories`. In that case, explain the limitation and ask for the explicit story ID; do not bypass the MCP connection with archive HTTP APIs.

Use the host's account connection flow for login and consent. Never request passwords, cookies, bearer tokens or API keys in chat. Do not bypass this plugin with raw HTTP or use the user's local credential files.

## Read

Call `readStoryCharacters` with `storyId`. It reads the current authenticated user's saved editable draft, not unsaved browser changes. The default page size is 20; follow `nextOffset` when the requested list extends beyond a page. Character IDs for subsequent calls are positive decimal strings; copy them from tool results rather than guessing.

If the user asks only to read or review, do not call a write tool. When necessary, explain that the user should save their editor draft before comparing the results.

## Edit

Call `composeCharacter` only for an existing character, with the explicit `storyId`, exact `characterId`, requested `updates` and a short `reason` grounded in the user's instruction. Resolve the character through a prior read when its exact identity or current fields are unknown. Ask for clarification only when the user's target or requested change is ambiguous.

The implemented fields are `name`, `persona`, `age`, and `targetHeightCm`. Follow the live tool schema for types and limits. Omit all unrequested fields. Empty persona or age clears that field, so do not send empty strings as placeholders. The default Narrator is protected.

A successful save returns `status: saved` and a save receipt. Read the affected character back to confirm, then report only the actual changes and the target story. For collaboration, writes affect the caller's editable draft rather than approving or publishing the main version.

If a request times out or its outcome is uncertain, read back before retrying. Do not blindly replay writes, fall back to whole-archive replacement, or claim success without a save receipt. Report permission and validation failures accurately.

## Current scope

Do not claim tools for character creation, image generation, voice assignment, phase/state changes, publishing, or background task recovery. Story listing/search is available only when `listStories` is actually exposed. Use only the tools actually exposed by this server. New tools must be implemented server-side and verified before these instructions expand.
