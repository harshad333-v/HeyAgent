# Dual provider modes

## Gemini API

The Gemini API adapter sends chat requests to Google's documented API using GEMINI_API_KEY. Configure GEMINI_CHAT_MODEL to override the default model.

## Gemini Web manual handoff

The desktop app can open https://gemini.google.com/app in the user's default browser and copy the prompt to the clipboard after the user submits it in Arya. The user then pastes the prompt into the website and reads the response there.

This is a manual browser handoff, not an automated provider. Arya does not import browser authentication data, automate private website endpoints, or retrieve the website response.

## OpenAI API

The OpenAI adapter uses OPENAI_API_KEY and optionally OPENAI_CHAT_MODEL.

## Security and limitations

- API credentials stay in the backend process environment and are not exposed to renderer JavaScript.
- Google sign-in remains in the user's browser.
- Gemini Web replies are not automatically returned to Arya.
- Do not build automated website access using undocumented endpoints. Any future automated integration requires a supported and authorized interface.
