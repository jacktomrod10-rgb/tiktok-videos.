# Sources: How a torn QR code still scans (episode 4, 24 Nov 2026)

| Claim in the video | Source(s) |
| --- | --- |
| A QR code can restore its data when it is dirty or damaged (error correction) | Denso Wave (official): https://www.qrcode.com/en/about/error_correction.html ("restore data if the code is dirty or damaged"); https://www.qrcode.com/en/about/ ("Dirt and Damage Resistant") |
| Up to ~30% can be damaged at the strongest level (H) | IEEE Spectrum: https://spectrum.ieee.org/how-a-board-game-and-skyscrapers-inspired-the-development-of-the-qr-code ("even if 30 percent of the code area is soiled or damaged"); Seagull Scientific: https://help.seagullscientific.com/10.1/en/Content/ErrorCorrection_QRCode.html (Level H ≈ 30% of codewords); Deloitte QR help: https://qr.deloitte.com/help/en/article/qr-code-error-correction |
| Levels L ≈ 7%, M ≈ 15%, Q ≈ 25%, H ≈ 30% | Seagull Scientific (above); Dynamsoft docs: https://www.dynamsoft.com/capture-vision/docs/core/enums/barcode-reader/qr-code-error-correction-level.html; Deloitte (above). Denso Wave confirms "Level M (15%)" and that Q corresponds to its 25% worked example |
| The backup is extra data computed with Reed–Solomon code | Denso Wave error-correction page ("implemented by adding a Reed-Solomon Code to the original data"); Wikipedia: https://en.wikipedia.org/wiki/Reed%E2%80%93Solomon_error_correction (QR Code uses Reed–Solomon) |
| The same maths is used on music CDs | Denso Wave error-correction page ("used for music CDs etc."); Wikipedia Reed–Solomon ("a key component of the compact disc", CIRC) |
| …and on space probes like Voyager | Wikipedia Reed–Solomon ("implemented in the Voyager program", used to encode pictures sent back); Denso Wave error-correction page (developed against noise for "artificial satellites and planetary probes") |
| The code's maker chooses the level; more correction makes the code bigger | Denso Wave error-correction page (levels chosen by operating environment; raising the level "increases the amount of data / QR Code size") |
| Torn code shown on screen really scans | Tested: the episode's level-H code ("EVERYDAY GENIUS", version 2) with the bottom-right chunk removed decodes with ZXing (zxing-cpp) and OpenCV's Aruco QR detector, checked on the rendered frames |
| Three corner squares are position-detection patterns, not data, letting the code be read from any angle (360°) | Denso Wave history: https://www.qrcode.com/en/history/ (orientation found "regardless of the angle of scanning… any angle out of 360°"); Denso Wave development story: https://www.denso-wave.com/en/technology/vol1.html ("position detection pattern, located at three corners") |
| Ratio 1:1:3:1:1, picked after surveying flyers, magazines and cardboard boxes for the ratio least used in print | Denso Wave history ("the least used ratio of black and white areas on printed matter. This ratio was 1:1:3:1:1"); Denso Wave development story (same survey of printed matter) |
| Denso released it in 1994 | Denso Wave history ("In 1994, DENSO WAVE (then a division of DENSO CORPORATION) announced the release"); IEEE Spectrum ("introduced in 1994 by … Denso") |
| …to track car parts in factories, where codes get oily and dirty | IEEE Spectrum ("developed the code to speed up its tracking of car parts"); Denso Wave development story (manufacturing sites "vulnerable to oil or other dirt") |
| Denso chose not to exercise its patent; anyone can use it free | Denso Wave history ("would retain the patent rights … it declared that it would not exercise them"); Denso Wave FAQ: https://www.qrcode.com/en/faq.html ("Is there a fee for using QR Code?" "No.") |

Dropped: logos in the middle of codes (Denso's FAQ warns against overlaying illustrations), the Go board-game inspiration
(only one source), and "10 times faster" (Denso and IEEE Spectrum disagree).
