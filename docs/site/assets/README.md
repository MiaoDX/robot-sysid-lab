# Presentation Assets

`l0-cover-hand.woff2` is a Long Cang subset for the Chinese L0 opening title.
Source: `google/fonts`, `ofl/longcang/LongCang-Regular.ttf`.
License: `LICENSE-LONG-CANG.txt` (SIL Open Font License 1.1).

Regenerate the subset when the opening title changes:

```sh
pyftsubset LongCang-Regular.ttf --text='让模型从偏差走向验证' \
  --flavor=woff2 --output-file=l0-cover-hand.woff2 --layout-features='*'
```

The Chinese title uses the local subset. English titles use the course display
font. Both versions use system fonts for body text, equations, and tables.
