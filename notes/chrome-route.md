# Posting through Chrome (tested 23 Nov 2026)

Works through the Claude in Chrome extension on the owner's PC (Google Chrome, signed in to TikTok as
@how.its.genius). The built-in browser in the Claude app does NOT work: TikTok's page blocks fetching
files from other sites (CSP), and the pane blocks popups opened by Claude.

**Check the account first.** The owner's Chrome was also signed in to a different TikTok account (@donut.wired).
Before uploading, open https://www.tiktok.com/profile in a new tab and confirm it redirects to @how.its.genius.
If it doesn't, stop and ask the owner to switch accounts. Never post to another account.

Steps that worked:
1. Make an upload copy of 3.3 MB or less (the Chrome upload tool's limit is about 3.8 MB). Two-pass x264 at
   the bitrate that gives about 3.3e6 bytes, AAC 96k. It looks the same as the original for these flat
   animations:
   `VB = (3.3e6*8/duration - 96000)/1000` kbps, `-preset slow -pass 1/2`, `-movflags +faststart`.
2. Open https://www.tiktok.com/tiktokstudio/upload in a new tab, `find` the hidden file input, and call
   `file_upload` with the path. The editor opens with "Uploaded".
3. The page has Description, Cover, "When to post: Now / Schedule" (scheduling IS available on this personal
   account, up to 10 days ahead), "Who can see this post", and under "Show more" the AI-generated content
   switch (leave OFF: the owner uses the "· AI voiceover" caption instead).
4. **Only press Post or Schedule after the owner says yes in chat for those videos.** Standing or scheduled
   instructions don't count. To back out, use Discard, then confirm Discard in the in-page box.
