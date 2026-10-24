# Mandarin Word Bank

A revision app for the *iChinese 爱汉语* course, Units 1–10 (32 chapters).

- **Vocabulary:** 1,343 words with pinyin, meaning, an example sentence and audio.
- **Character breakdowns:** radical, components and stroke order for each character, plus a radical index.
- **Synonyms (近义词):** for 794 of the words.
- **Readings:** the textbook passages, with the textbook recordings and a hover card for every vocab word.
- **Comprehension questions:** 328 questions, each with an explanation.
- **Quizzes:** five question types, with a weak-words list.
- **Sentence patterns (句型):** 32 grammar patterns and a phrase bank of 137 ready-made sentences.

## Opening it

| How | What to do |
|---|---|
| **GitHub Pages** (easiest) | Repo **Settings → Pages → Deploy from branch → `main` / root**. The site appears at `https://<username>.github.io/<repo>/`. A Pages site is **public to anyone with the link**, even when the repo is private, and Pages on a private repo needs GitHub Pro (free for students). |
| **On your computer** | In this folder run `python3 -m http.server`, then open http://localhost:8000. Double-clicking `index.html` works too, but browsers block the word audio from a local file, so the device's own voice is used instead. |
| **Fully offline, one file** | Run `python3 build.py --offline` to make `Mandarin-Word-Bank-offline.html` (about 60 MB, all audio built in). It's in `.gitignore` because it's too big for GitHub. |

## Folder layout

```
index.html          the app (built — don't edit by hand)
audio/              word + example-sentence audio, one file per chapter (+ x.mp3 for phrases/patterns)
ptext/              textbook passage recordings, e.g. 3.2_1.mp3 = Unit 3 Lesson 2 Text 1
data/               everything the app shows, as JSON (made from source/)
source/
  template.html     the app's HTML/CSS/JS, with __PLACEHOLDERS__ for the data
  vocab/            vocabulary per chapter:  word|pinyin|meaning|example|translation[|spoken form]
                    (a leading * marks "Extra vocabulary")
  texts/            reading passages (format notes below)
  questions/        comprehension questions: TF / MC / SA lines per passage
  phrases/          phrase bank
  patterns.py       sentence-pattern definitions
tools/              the scripts used to make data/ and the audio (see notes)
build.py            rebuilds index.html from source/template.html + data/
```

## Changing things

- **Change the look or behaviour:** edit `source/template.html`, then run `python3 build.py`.
- **Fix a word, sentence or question:** edit the JSON in `data/`, then run `python3 build.py`. The text files in `source/` are the originals the JSON was made from. They're kept for reference, and the scripts in `tools/` show how they were converted.

**Passage text format** (`source/texts/`):

| Line starts with | Meaning |
|---|---|
| `@3.2` | chapter |
| `## 课文一\|TEXT 1\|d` | passage heading; type `d` = dialogue, `p` = prose, `l` = letter |
| `{王菲\|Wáng Fēi}` | name shown with pinyin above it |
| `#` | paragraph heading |
| `<` | unindented line |
| `>` | right-aligned line |
| `^` | centred line (diary heading) |
| `=` | intro paragraph |
| `~` | source link |

## Notes

- **Word audio** was made with an offline Mandarin speech engine (sherpa-onnx, the matcha-icefall-zh-baker model), plus a list of pronunciation fixes (`tools/prep.py` and the overrides described in `tools/`). The model isn't included because it's large. The scripts in `tools/` are the working versions, so their file paths may need adjusting before you run them again.
- **Passage audio** is the textbook's own recordings.
- **Example sentences for "extra" words, the English translations, the synonyms, the comprehension questions, the phrase bank and the pattern explanations** were written for this app and aren't from the textbook.
- **Character data** (decompositions, stroke order) comes from [Make Me a Hanzi](https://github.com/skishore/makemeahanzi) (LGPL / Arphic Public License).

## Copyright

The passages, vocabulary lists and recordings come from the *iChinese 爱汉语* textbook and are © their publisher. This repository is for personal study only. **Keep the repository private** and don't redistribute the textbook content.
