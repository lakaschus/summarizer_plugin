# ChatGPT plugin: Large Text Summarizer

Credit goes to https://github.com/daveshap/EU_AI_Act for the idea of summarizing text using ChatGPT.

## How-To

This Repo can be used as a plugin to ChatGPT. 
1. `pip install -r requirements.txt`
2. Just adapt the url in the `.well-known/ai-plugin.json` to your endpoint. 
3. Also specify your OpenAI API key in your environment. For instance, you can create a `.env` file with the following content: `OPEN_AI_KEY=<Your Key>`

## Background

This plugin basically summarizes any websites (Also PDFs) of any lengths by doing very simple web- and PDF-scraping and subsequent summarization using GPT3.5-16k.

If the length of the given text is longer than the context length, multiple chunks will be created where each chunk is smaller than the context length. Then, for each chunk of text a summary will be created. Finally, ChatGPT tries to create a coherent summary using the summaries of the separate chunks. 

Note that summarizing very large texts, like books, can be very expensive. 
Don't forget to set a limit on your OpenAI API key ;)
