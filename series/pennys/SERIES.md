# The Pennys — daily interactive episode

An original cartoon family series. The Pennys (Dave, Sue, Ellie, Alfie and Crumbs the dog) have 30 days to
save a £1,000 deposit for three weeks in Australia. Every episode ends with an A/B/C choice, and viewers vote in the comments.
Each daily run counts yesterday's votes, plays out the winning choice, and posts the next episode at
**13:00 Europe/London**.

Story memory lives in `series/pennys/state.json` (day, fund, stats, characters, every episode's options,
votes, winner and post IDs). Read it first, and update it at the end of every run.

## Daily run procedure

1. **Set up.** `pip install --break-system-packages -q kokoro-onnx soundfile`. Work from the repo root.
2. **Load the story.** Read `state.json`. Today's episode number N = `state.day + 1`. If N > 30, run the finale
   (see below).
3. **Find yesterday's TikTok video.** Call Metricool `getScheduledPosts` (brandId `8305380`, timezone
   `Europe/London`) for the last 2 days and find the post whose `uuid` equals the last episode's `post_uuid`.
   Its `providers[0].id` is the TikTok video ID (only once `status` is `PUBLISHED`). Save it to the episode's
   `tiktok_video_id`. If it isn't published, tell the owner and stop.
4. **Count the votes.** Windsor `get_data`: connector `tiktok_organic`, fields
   `["comment_video_id", "comment_id", "comment_text", "comment_username", "comment_likes"]`,
   `date_preset` `"last_7dT"`, filter `[["comment_video_id", "eq", "<video id>"]]` (use `force_refresh` if
   the plan allows). Save the rows as JSON to `/tmp/comments.json`, then run
   `python3 -I series/pennys/tally.py /tmp/comments.json`. It counts one vote per username and prints
   `{"A": n, "B": n, "C": n, "winner": "X", "rule": "..."}`. Its tie and zero-vote rules are written in the
   script. With zero votes, the story says "nobody voted, so Crumbs chose".
5. **Play out the winner.** Decide what happens: money in or out, stat changes (happiness and house, 0–100),
   and sometimes a twist (good or bad, e.g. Crumbs eats the car keys, a neighbour pays for a repair). Keep it
   plausible and tense. They need about £33 a day on average; good choices should make £1,000 reachable by
   day 30, but never guaranteed. Then set up today's new problem or opportunity and write 3 new options,
   each with a clear trade-off.
6. **Write the episode** as `series/pennys/epNN/make.py`, copying the structure of `series/pennys/ep01/make.py`
   and using `studio/pennys.py` (room, characters with moods and poses, `hud`, `stats_panel`, `vote_card`,
   `result_bars`, `money_pop`, `jar`, `phone_card`). 60–75 seconds:
   - Open with a **title card** for the first ~2.4 s (copy the slide-away card in ep01's `hook` scene), e.g.
     "DAY N" / "£X TO GO" / one punchy line about today's drama. The first two seconds decide whether people stay.
   - Hook (1 line): "Yesterday, you voted ___" plus a cliffhanger.
   - Show the vote result with `result_bars` and the percentages.
   - Play out the outcome with the characters (2–4 lines), `money_pop` for money in or out, and the updated `hud`.
   - Introduce today's problem (1–2 lines), the new `vote_card` (options read out as "A: …, B: …, or C: …"),
     then end with the family on screen and "Comment A, B or C. Day N+1 tomorrow." Use the HUD with the
     *new* fund.
   - Same rules as CLAUDE.md for `lines` (numbers as words) and `display` (digits and `*highlights*`), and for
     checking stills before rendering.
7. **Render** to `videos/pennys-epNN.mp4`, look at 3–4 frames, then commit and push. Confirm the raw URL returns 200.
8. **Check the monthly limit, then schedule.** Count this calendar month's published and scheduled posts
   with `getScheduledPosts`. If the free plan's 20 are used up, don't schedule; tell the owner. Otherwise use
   `createScheduledPost` with the same `info` template as CLAUDE.md, at 13:00 today (one hour from now if
   it's later), with:
   `"text": "The Pennys, Day N: <one-line hook>. Comment A, B or C! #thepennys #youdecide #storytime #familylife #animation · AI voiceover"`
   and `"title": "The Pennys · Day N"`, plus `"videoCoverMilliseconds": 1300` so the title card is the cover.
   Keep `isAigc` false and the `· AI voiceover` ending.
9. **Save the story.** Update `state.json`: day = N, fund, stats, the previous episode's `votes` and `winner`,
   and a new episode entry (day, summary, options, post_uuid). Commit and push.
10. **Tell the owner.** `SendUserMessage`: yesterday's vote result, what happened, the new fund, and "Day N
    posts at 13:00" with the planner link. Then `SendUserFile` the episode.

## Finale (day 30)

Count the last vote, play it out, and reveal whether the fund reached £1,000. Make it emotional either way:
the trip, or a heartfelt near miss. Then message the owner suggesting season 2 ideas.

## Rules

- Votes come **only from comments**. Never offer viewers money, prizes or rewards for likes, follows or
  shares. TikTok treats that as fake engagement, and it can stop the account being recommended.
- Keep it family-friendly and kind: tease, don't humiliate. No real people, real brands made to look bad, or
  characters from other creators.
- Keep the characters consistent with `state.json`. The narrator voice for The Pennys is `bm_fable`
  (the owner's choice; pass `voice=P.NARRATOR` to `Video`, as ep01 does). Explainers keep `bm_george`.
- Stats are spoken and shown as real numbers ("Happiness: fifty out of a hundred", `stats_panel` with a value
  text), never vague words like "tiny".
- Keep the story consistent: money and stats on screen must match `state.json`.
