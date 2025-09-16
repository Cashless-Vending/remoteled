# Linear CSV Import: Getting Started

This guide walks you through preparing your environment, collecting the required Linear API token, and importing issue CSV files into Linear using the official CLI importer. Follow the steps in order and you can migrate issues from scratch without any prior setup.

## 1. Install Prerequisites
- Install [Node.js](https://nodejs.org/) 18 or newer so that `npm` is available on your machine.
- Verify the install:
  ```bash
  node --version
  npm --version
  ```

## 2. Install the Linear Importer CLI
Global installation makes the importer available from any directory:
```bash
npm i --location=global @linear/import
# or, equivalently
npm install -g @linear/import
```
After installation confirm that the binary is resolvable:
```bash
linear-import --help
```

## 3. Create a Linear Personal API Key
The importer authenticates with your workspace using a personal API key. Generate one from Linear’s web app:
1. Open Linear and click your avatar → `Settings`.
2. Navigate to **Security & access**.
3. Under **Personal API keys**, choose **New API key**, give it a descriptive label (e.g., `issuesKEY`), and copy the generated token. Store it in a password manager—you will paste it into the importer.

![Linear security and access screen](./linear-security-access.png)

> **Tip:** If the screenshot above is missing, capture your own by visiting the Security & access page. The API key must include the teams you plan to import into.

## 4. Prepare Your CSV File
Two starter CSVs live next to this guide:
- `linear_single_issue.csv` — a single issue to validate your mapping.
- `linear_all_issues.csv` — a full set covering project items PR-00…PR-11.

You can edit either file to match your workspace’s priorities, statuses, assignees, or labels. Keep the header row intact so the importer can map the columns correctly.

### Sample CSV Structure
```csv
Title,Description,Priority,Status,Assignee,Labels,Estimate,Created,Completed
"PR-01: Baseline Monorepo + CI","Set up monorepo layout; add Android CI to build assembleDebug; harden pi/install.sh path handling; confirm .gitignore excludes APKs/zips/builds/venv.

Acceptance:
- App builds on CI and uploads artifact
- Installer runs from any CWD
- Repo ignores binaries and build outputs","P1","Backlog","","phase:setup;phase:ci","3","2025-09-16",""
```

## 5. Run the Importer
1. Execute the CLI from the directory containing your CSV file:
   ```bash
   linear-import
   ```
2. When prompted (all answers can be changed on rerun):
   - Paste the personal API key you generated. Avoid passing the key via command-line arguments so it stays out of shell history.
   - Choose **Linear CSV** as the importer type.
   - Decide whether to create a new team (usually **No** if you already have the target team).
   - Select the destination team.
   - Choose whether to scope to a specific project and/or auto-assign the imported issues to yourself.
3. Map the CSV columns as follows:
   - `Title` → Title
   - `Description` → Description (Markdown is supported)
   - `Priority` → Priority (P0–P3)
   - `Status` → Status (map `Backlog` to your first workflow column, e.g., Backlog/Todo)
   - `Assignee` → Assignee (optional; must exactly match the member’s full name)
   - `Labels` → Labels (semicolon `;` separated)
   - `Estimate` → Estimate (story points)
   - `Created` / `Completed` → Dates (optional)
4. Review the preview, confirm the import, and wait for Linear to create the issues.

## 6. Post-Import Checks
- Open the destination team’s board or backlog to confirm the imported issues appear with the expected statuses and labels.
- If something looks wrong, adjust the CSV and rerun `linear-import`. The CLI avoids duplicates when issue titles remain identical.

You are now ready to iterate on your CSV and bring larger batches of work into Linear.
