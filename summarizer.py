import openai
import tiktoken
import os
import time
from dotenv import load_dotenv
load_dotenv()

enc = tiktoken.get_encoding("cl100k_base")

def token_size(text):
    return len(list(enc.encode(text)))

class GPTSummarizer:

    def __init__(self, max_len=12000, chunk_size=1024):
        self.max_len = max_len
        self.chunk_size = chunk_size
        self.max_chunk_size = chunk_size
        self.system_message = {
            "word_count_reduce": "You are a Summarizer Assistant. You are designed to help users condense large bodies of text into summaries. Please reduce word count, but the largest priority is to conserve important information and to retain context. Do not omit relevant information. You neither ask questions nor give comments. You only return a summary",
            "normal": "You are a Summarizer Assistant. You are designed to help users condense large bodies of text into concise summaries. You neither ask questions nor give comments. You only return a summary",
            "brief": "You are a Summarizer Assistant. You are designed to help users condense large bodies of text into concise and brief summaries. You neither ask questions nor give comments. You only return a brief summary.",
            "extensive": "You are a Summarizer Assistant. You are designed to help users condense large bodies of text into extensive summaries. You neither ask questions nor give comments. You only return an extensive summary."
        }
        self.chunk_summary_prompt = ""
        self.meta_summary_prompt = ""

    def chat_completion(system_message, text):
        while True:
            try:
                response = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                    messages=[
                            {'role': 'system', 'content': system_message},
                            {'role': 'user', 'content': f'Summarize: {text}'},
                        ],
                    )
                return response.choices[0].message.content
            except (openai.error.RateLimitError, openai.error.OpenAIError):
                print("OpenAI request failed. Waiting 1 second before trying again...")
                time.sleep(1)
            except Exception:
                print("Something went wrong. Waiting 1 second before trying again...")
                time.sleep(1)

    def split_into_chunks(self, text):
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ''
        for paragraph in paragraphs:
            if token_size((current_chunk + '\n\n' + paragraph)) <= self.max_len:
                current_chunk += '\n\n' + paragraph
            else:
                chunks.append(current_chunk)
                current_chunk = paragraph
        chunks.append(current_chunk)
        return chunks

    def generate_summary(self, text, mode='normal'):
        system_message = self.system_message[mode]
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo-16k',
            temperature=0,
            messages=[
                    {'role': 'system',
                     'content': system_message
                     },
                    {'role': 'user',
                     'content': f'Summarize in approximately {self.max_chunk_size} words: {text}'
                     },
                ],
            )
        return response.choices[0].message.content

    def generate_summary_of_summaries(self, summaries):
        prompt = ("In the following I will present multiple summaries, and each of these "
                  "summaries belong to one section of a larger text. The summaries are "
                  "ordered, i.e., the first summary belongs to the first section of the text, "
                  "the second summary belongs to the second section, and so on. Now your task "
                  "is to create one single extensive summary from the following summaries. Please "
                  "make sure that the final summary coherent and that it feels like one summary "
                  "for the entire original text. The summaries for each section of the original "
                  "text are as follows: \n")
        for i, summary in enumerate(summaries):
            prompt += f"{i+1}. {summary} \n"
        prompt += f"""Now please give your final extensive summary with approximately {16000 - self.max_len} words: """
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                    {'role': 'system', 'content': self.system_message['extensive']},
                    {'role': 'user', 'content': prompt},
                ],
            )
        return response.choices[0].message.content

    def summarize_large_text(self, text):
        # Split the text into chunks
        chunks = self.split_into_chunks(text)

        summarized_chunks = []
        self.max_chunk_size = int(self.max_len / len(chunks))
        for chunk in chunks:
            summary = self.generate_summary(chunk, mode='word_count_reduce')
            if token_size(summary) > self.max_chunk_size:
                summary = self.generate_summary(summary, mode='word_count_reduce')
            if token_size(summary) > self.max_chunk_size:
                summary = self.generate_summary(summary, mode='brief')
            summarized_chunks.append(summary)

        final_summary = self.generate_summary_of_summaries(summarized_chunks)
        return final_summary


# load openai key from environment
openai.api_key = os.getenv('OPEN_AI_KEY')

summarizer = GPTSummarizer()
# path = "datasets/shakespeare/romeo_and_juliet.txt"
path = "datasets/EU_AI_legislation.txt"
with open(path, encoding="utf-8") as f:
    large_text = f.read()
print(f"Text has total size of {token_size(large_text)} tokens.")
summary = summarizer.summarize_large_text(large_text)
print(summary)
