import openai
import tiktoken
import os
import time
from dotenv import load_dotenv
load_dotenv()

enc = tiktoken.get_encoding("cl100k_base")
openai.api_key = os.getenv('OPEN_AI_KEY')


def token_size(text):
    return len(list(enc.encode(text)))


class GPTSummarizer:

    def __init__(self, large_text, max_len=12000, relative_chunk_size=0.1):
        self.relative_chunk_size = relative_chunk_size
        self.large_text_token_size = token_size(large_text)
        self.chunk_size = max(min(int(self.large_text_token_size * self.relative_chunk_size), max_len), 1000)
        self.large_text = large_text
        self.max_len = max_len
        self.chunk_size_margin = int(0.1*self.chunk_size)
        self.max_chunk_size = self.chunk_size
        self.max_chunk_size_chars = self.max_chunk_size*3
        self.system_message = {
            "word_count_reduce": "You are a Summarizer Assistant. You are designed to help users condense large bodies of text into summaries. Please reduce word count, but the largest priority is to conserve important information and to retain context. Do not omit relevant information. You neither ask questions nor give comments. You only return a summary",
            "normal": "You are a Summarizer Assistant. You are designed to help users condense large bodies of text into concise summaries. You neither ask questions nor give comments. You only return a summary",
            "brief": "You are a Summarizer Assistant. You are designed to help users condense large bodies of text into concise and brief summaries. You neither ask questions nor give comments. You only return a brief summary.",
            "extensive": "You are a Summarizer Assistant. You are designed to help users condense large bodies of text into extensive summaries. You neither ask questions nor give comments. You only return an extensive summary."
        }
        self.chunk_summary_prompt = ""
        self.meta_summary_prompt = ""
        print("GPTSummarizer initialized.")
        print(f"Large text token size: {self.large_text_token_size}")
        print(f"Chunk size: {self.chunk_size}")

    def chat_completion(self, system_message, content):
        while True:
            try:
                response = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo-16k',
                    messages=[
                            {'role': 'system', 'content': system_message},
                            {'role': 'user', 'content': content},
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
        tokens = enc.encode(text)
        chunks = []
        for i in range(0, len(tokens), self.chunk_size):
            chunks.append(enc.decode(tokens[i:i+self.chunk_size+self.chunk_size_margin]))
        return chunks

    def generate_summary(self, text, mode='normal'):
        system_message = self.system_message[mode]
        response = self.chat_completion(system_message,
            f'Summarize in approximately {self.max_chunk_size} words: {text}')
        return response

    def generate_summary_of_summaries(self, summaries):
        prompt = ("In the following I will present multiple summaries, and each of these "
                  "summaries belong to one section of a larger text. The summaries are "
                  "ordered, i.e., the first summary belongs to the first section of the text, "
                  "the second summary belongs to the second section, and so on. Note however, "
                  "that the end of the i-th summary and the beginning of the (i+1)-th summary "
                  "might overlap. Now your task "
                  "is to create one single extensive summary from the following summaries. Please "
                  "make sure that the final summary coherent and that it feels like one summary "
                  "for the entire original text. The summaries for each section of the original "
                  "text are as follows: \n")
        for i, summary in enumerate(summaries):
            prompt += f"{i+1}. {summary} \n"
        prompt += f"""Now please give your final extensive summary with approximately {16000 - self.max_len} words: """
        response = self.chat_completion(self.system_message['extensive'], prompt)
        return response

    def summarize_large_text(self):
        # Split the text into chunks
        chunks = self.split_into_chunks(self.large_text)
        self.max_chunk_size = int(self.max_len / len(chunks))

        summarized_chunks = []
        for i, chunk in enumerate(chunks):
            print(f"Summarizing chunk {i}")
            summary = self.generate_summary(chunk, mode='word_count_reduce')
            if token_size(summary) > self.max_chunk_size:
                summary = self.generate_summary(summary, mode='word_count_reduce')
            if token_size(summary) > self.max_chunk_size:
                summary = self.generate_summary(summary, mode='brief')
            if token_size(summary) > self.max_chunk_size:
                print("Summary is still too long. Truncating summary to max chunk size.")
                summary = summary[:self.max_chunk_size_chars]
            summarized_chunks.append(summary)

        print("Generating final summary of summaries")
        final_summary = self.generate_summary_of_summaries(summarized_chunks)
        return final_summary


def main(path):
    with open(path, encoding="utf-8") as f:
        large_text = f.read()
    # large_text = "text"*3000
    summarizer = GPTSummarizer(large_text)
    summary = summarizer.summarize_large_text()
    # Write summary to file
    target = path.split("/")[-1].split(".")[0]
    with open(f"out/{target}_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)
    print(summary)


if __name__ == "__main__":
    # load openai key from environment
    # path = "datasets/shakespeare/romeo_and_juliet.txt"
    # path = "datasets/EU_AI_legislation.txt"
    path = "datasets/einkommensteuergesetz.html"
    # path = "datasets/faust.txt"
    main(path)
