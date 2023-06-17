import requests
from bs4 import BeautifulSoup
# import pdfplumber
# from io import BytesIO
import tiktoken
from pdfminer.high_level import extract_text

enc = tiktoken.get_encoding("cl100k_base")


def token_size(text):
    return len(list(enc.encode(text)))


def get_content(url):
    try:
        # Sending a GET request
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Something went wrong", err)

    # Check if the URL points to a PDF
    if url.endswith('.pdf') or "pdf" in response.headers["Content-Type"]:
        # Write the PDF to a temporary file
        with open('temp.pdf', 'wb') as f:
            f.write(response.content)
        # Use PDFMiner to extract the text
        text = extract_text('temp.pdf')
        return text

    else:
        # Use BeautifulSoup to parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        # Remove unnecessary tags
        for script in soup(["script", "style"]):
            script.decompose()
        # Get the text
        text = soup.get_text()
        # Remove leading and trailing whitespace
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text


if __name__ == '__main__':
    url = 'https://example.com'
    url = 'https://raw.githubusercontent.com/lakaschus/CodeAlong_GPTFromScratch/master/source_datasets/1808-Faust-1.txt'
    url = 'https://www.gesetze-im-internet.de/estg/BJNR010050934.html'
    url = 'https://arxiv.org/pdf/2303.10130.pdf'
    content = get_content(url)
    print("Content: ", content)
    print("Token size: ", token_size(content))
