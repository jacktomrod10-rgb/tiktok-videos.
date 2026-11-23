# Everyday Genius — daily TikTok pipeline

This repo is the working folder for the owner's faceless TikTok account **Everyday Genius**:
short animated explainers on how everyday things secretly work. Each daily run makes ONE
video, publishes the file here, and schedules it on TikTok through Metricool.

## Fixed facts

| Thing | Value |
| --- | --- |
| GitHub repo | `jacktomrod10-rgb/tiktok-videos.` (the name ends with a dot) — clone to `/home/claude/tiktok-videos._` |
| Public file URL | `https://raw.githubusercontent.com/jacktomrod10-rgb/tiktok-videos./main/videos/<file>.mp4` |
| Metricool | brand/blogId `8305380`, timezone `Europe/London`, TikTok account linked (jackrodgers102) |
| Metricool plan | Free: **20 published posts per calendar month**, resets on the 1st |
| Post time | **19:00 Europe/London**, same day as the run (if it's already past 18:30, use one hour from now) |
| Voice | Kokoro `bf_emma` (British female), set in `studio/kit.py` |
| Stats (optional) | Windsor connector `tiktok_organic`, account `_000od0_ziCgbX4rS4Lw3KlPBn_Doym-UYGw` (read-only) |

## Daily run procedure

1. **Set up.** `pip install --break-system-packages -q kokoro-onnx soundfile`. Voice models download
   automatically from GitHub on first use. Work from the repo root.
2. **Pick the topic.** First unticked line in `topics.md`. Episode number = number of ticked topics + 1.
3. **Research.** Look up every factual claim you plan to use (WebSearch/WebFetch). Each claim needs one
   primary/official source or two independent reputable ones. Drop any claim you can't verify. If the
   topic doesn't hold up, mark it `[x] SKIPPED: reason` and take the next one. Save the sources to
   `videos/<YYYY-MM-DD>-<slug>/sources.md` (claim → URL).
4. **Write the script** as `videos/<YYYY-MM-DD>-<slug>/make.py`, copying the structure of
   `examples/uk_plug.py`:
   - Target **60–75 seconds** of speech: about 170–200 words in 8–12 lines.
   - Line 1 is the hook, 10 words or fewer, a surprising claim ("X is secretly genius", "You've been
     using X wrong", "There's a reason X is Y").
   - Last line ends with "Follow for more everyday genius."
   - `lines` = what the voice says: write numbers, years and units as words ("nineteen forty-seven",
     "thirteen amps"). `display` = the captions: digits allowed, mark 1–3 key words per line with `*word*`.
5. **Voice.** `python3 -I videos/<dir>/make.py tts`. Read the printed phonemes; if a word or number is
   mispronounced, respell it in `lines` and rerun. Check the TOTAL is 58–80 s.
6. **Visuals.** One `@V.scene(...)` per idea, 4–7 scenes, using the kit (`Pen`, `pill`, `tick`, `cross`,
   `sparkle`, `big_number`, `flow_dots`, `bar_chart`, `arrow`). Rules:
   - Draw simple flat diagrams of the thing being explained; something should move at all times.
   - Keep everything inside x 60–1000, y 300–1150 (captions live around y 1270, the top bar above 300).
   - No real people, no brand logos or mascots, no copyrighted characters. Naming a brand as a fact is fine.
7. **Check stills before rendering.** `python3 -I videos/<dir>/make.py stills <t1> <t2> ...` at the busiest
   moment of every scene, then **Read the contact sheet image** and fix overlaps, clipped labels or empty
   frames. Repeat until clean.
8. **Render.** `python3 -I videos/<dir>/make.py render videos/<YYYY-MM-DD>-<slug>.mp4`. Pull 3–4 frames from
   the finished file with ffmpeg and look at them.
9. **Publish the file.** `git add` the mp4, `make.py` and `sources.md`; commit; then
   `git -c push.negotiate=true push`. Confirm the raw URL returns HTTP 200 with `curl -sIL`.
10. **Schedule in Metricool** with `createScheduledPost` (blogId `8305380`). Use this `info`, filled in:
    ```json
    {"autoPublish": true, "descendants": [], "draft": false, "firstCommentText": "", "hasNotReadNotes": false,
     "media": ["<raw URL>"], "mediaAltText": [], "providers": [{"network": "tiktok"}],
     "publicationDate": {"dateTime": "<YYYY-MM-DD>T19:00:00", "timezone": "Europe/London"},
     "shortener": false, "smartLinkData": {"ids": []},
     "text": "<hook sentence>. <question for comments>? #howitworks #everydaygenius #<topic> #<topic> #learnontiktok · AI voiceover",
     "tiktokData": {"disableComment": false, "disableDuet": false, "disableStitch": false,
                    "privacyOption": "PUBLIC_TO_EVERYONE", "commercialContentThirdParty": false,
                    "commercialContentOwnBrand": false, "title": "<short title>", "autoAddMusic": false,
                    "photoCoverIndex": 0, "isAigc": false}}
    ```
    - The caption is one line (TikTok drops line breaks) and **must end with `· AI voiceover`**. The owner
      chose this caption disclosure instead of TikTok's AI badge, so keep `isAigc` false.
    - If Metricool returns a plan or post-limit error, don't retry. Tell the owner (step 12).
11. **Log it.** Tick the topic in `topics.md` with the date, episode number and Metricool `uuid`. Commit and push.
12. **Tell the owner.** `SendUserMessage`: the title, "posts at 19:00", the Metricool `plannerUrl`, and a note
    that they can delete it there before then if they don't like it. Then `SendUserFile` the mp4.
    If anything failed, post nothing broken: send one message saying what failed and what's needed.

## Content rules

- Topics: how everyday objects, systems and inventions work. Keep them international, not UK-only, unless
  the topic is inherently British.
- Avoid: medical or health advice, financial or investment advice, politics, news, crime, anything about
  real private individuals, and dangerous "how to" content (no DIY electrics instructions etc.).
- No superlatives ("the safest", "the first") unless a source says so explicitly.
- Vary the hooks and the scene layouts from day to day, so the feed doesn't look templated.
- When fewer than 5 topics are left unticked, research and append 10 new ones that fit these rules.

## Mondays: quick performance check (optional, only if time allows)

Read the last 7 days of video stats (Windsor `tiktok_organic`, or Metricool analytics) and append 3–5 lines
to `notes/performance.md`: which videos held viewers best and what to do more of. Reorder the next few
topics in `topics.md` to match.
