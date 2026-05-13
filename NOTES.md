# Notes

## Version 1.5 - 2026-05-13

- Removed the GitHub token prompt from the app.
- The app now reads the token from an embedded `github_token.txt`, `RICHIESTA_GITHUB_TOKEN`, or `github_token.txt` next to the executable.
- The build script automatically embeds `github_token.txt` when that file exists during compilation.
- If no token is available, the app shows an error and does not ask the user to type anything.
- PDF filenames now use day-month-year dates, for example `13-05-2026`.

## Version 1.4 - 2026-05-12

- Published the GitHub-shared request counter build as v1.4.
- The visible request label now stays simple: `Richiesta: N. 0001`.
- The GitHub counter remains the single shared source for all PCs.
- The Windows executable is published as `dist/Richiesta di approvvigionamento v1.4.exe`.

## Version 1.3 - 2026-05-12

- Request numbering now uses GitHub as the single shared source of truth.
- On startup, the app reads `richiesta_counter.json` from the repository to show the next request number.
- Before generating a PDF, the app reserves the number by updating `richiesta_counter.json` on GitHub.
- This prevents two PCs from generating the same request number.
- A GitHub token with repository write access is required through `RICHIESTA_GITHUB_TOKEN` or `github_token.txt`.

## Version 1.2 - 2026-05-12

- Request numbering is now annual.
- If the year stored in `richiesta_counter.json` is different from the current year, the next request starts again from `0001`.
- The counter still advances only after the PDF is generated successfully.

## Version 1.1 - 2026-05-12

- Added automatic numbering for each `Richiesta di Approvvigionamento`.
- The generated PDF filename now includes the request number, for example:
  `Richiesta di approvvigionamento N. 0001 - 13-05-2026.pdf`.
- The request number is printed inside the PDF header as `N. 0001`.
- The app shows the next request number in the main toolbar.
- The counter is stored locally in `richiesta_counter.json` next to the program.
- The counter advances only after the PDF is generated successfully.

## Included Build

- Windows executable: `dist/Richiesta_di_approvvigionamento.exe`
- Python source: `app.py`
