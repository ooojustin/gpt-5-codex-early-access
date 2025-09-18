### codex-ea

demonstration of how to use `gpt-5-codex` programmatically, before it is available via the API, without paying for API credits.
the codex endpoint only works with `gpt-5-codex` and `gpt-5`.
you should not do this. this project is for educational purposes only.

1. copy `.env.example` to `.env`
2. set the `OPENAI_API_KEY` in `.env` to your access token from `~/.codex/auth.json`

after that, you can run `python -m codex_ea` to see it work.
