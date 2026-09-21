# Java and Jakarta EE question bank

The public question source used by Tutorialz on Android and the web: **600 questions** across seven courses, published as catalog revision **3**.

| Course | Questions |
| --- | ---: |
| Enterprise basic | 100 |
| Enterprise medium | 100 |
| Enterprise advanced | 20 |
| Beginner Java | 64 |
| Java OOP | 66 |
| [Jakarta Competency Exam](JAKARTA_COMPETENCY_EXAM.md) | 50 |
| [Jakarta Dummy Exam](JAKARTA_DUMMY_EXAM.md) | 200 |

The former 3,200-question collection contained repeated variants. The current collection preserves curriculum coverage with distinct assessments. See [content notes](CONTENT.md), [coverage](coverage.json), [question conventions](QUESTION_CONVENTIONS.md), and [import attribution](imports/LICENSE-java-quiz.txt).

The mobile app downloads [catalog.json](https://raw.githubusercontent.com/adichannnnnhere64/jakarta-ee-question-bank/main/catalog.json) and verifies the SHA-256 of each changed course. Existing installs receive the update on their next online launch or through **Settings → Sync questions now**. Their attempt history and active question snapshots are retained.

## Updating questions

Edit and validate the collection in [Tutorialz's content/enterprise directory](https://github.com/adichannnnnhere64/tutorialz/tree/main/content/enterprise), then publish those changes to Tutorialz `main`. This repository mirrors that directory; make question edits in Tutorialz so they also reach the bundled offline bank.

The [Sync questions workflow](../../actions/workflows/sync.yml) checks Tutorialz `main` hourly and can also be run manually. It validates the source catalog and question bank, refuses collection changes or revision downgrades, and publishes changed files together in one commit. It copies existing JSON without regenerating questions. The upstream README is mirrored as `CONTENT.md`.

For local publication from a Tutorialz checkout:

```sh
cargo run -p tutorialz-core --locked -- content/enterprise/catalog.json
python3 scripts/question_bank.py
python3 /path/to/jakarta-ee-question-bank/scripts/sync.py content/enterprise
git -C /path/to/jakarta-ee-question-bank diff --stat
git -C /path/to/jakarta-ee-question-bank add .
git -C /path/to/jakarta-ee-question-bank commit -m "Sync questions from Tutorialz"
git -C /path/to/jakarta-ee-question-bank push origin main
```
