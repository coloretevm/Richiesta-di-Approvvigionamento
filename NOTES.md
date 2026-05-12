# Notes

## Version 1.2 - 2026-05-12

- Request numbering is now annual.
- If the year stored in `richiesta_counter.json` is different from the current year, the next request starts again from `0001`.
- The counter still advances only after the PDF is generated successfully.

## Version 1.1 - 2026-05-12

- Added automatic numbering for each `Richiesta di Approvvigionamento`.
- The generated PDF filename now includes the request number, for example:
  `Richiesta di approvvigionamento N. 0001 - 2026-05-12.pdf`.
- The request number is printed inside the PDF header as `N. 0001`.
- The app shows the next request number in the main toolbar.
- The counter is stored locally in `richiesta_counter.json` next to the program.
- The counter advances only after the PDF is generated successfully.

## Included Build

- Windows executable: `dist/Richiesta_di_approvvigionamento.exe`
- Python source: `app.py`
