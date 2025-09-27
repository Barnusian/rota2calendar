## rota2calendar
Webapp used to parse the spreadsheet data in rota PDFs and return calendar event files.

A rota file and employee name (not case-sensitive) are provided. The employee's shifts are found in their named row. Sunday's date in the top left (cell reference:...) is used to extrapolate the dates of the rest of the week. The shifts are exported as .ics files. Files are processed live and nothing is stored or kept long-term.

#### Further Dev Goals:

- Fix on iOS. It's got something to do with how I'm referencing the date, I think there's a more robust/less hacky way to do it.

- Update landing page

- Update description