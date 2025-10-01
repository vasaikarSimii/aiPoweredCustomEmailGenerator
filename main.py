import json
import re
from openai import OpenAI

# Load API key
with open("config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)
api_key = cfg.get("openai_api_key")
if not api_key:
    raise ValueError("Missing openai_api_key in config.json")

client = OpenAI(api_key=api_key)

def format_email(contact_name: str, company_name: str, custom_paragraph: str) -> str:
    lines = [
        f"Subject: Experienced AI & Healthcare Engineer Excited to Contribute to {company_name}",
        "",
        f"Dear {contact_name},",
        "",
        "Hope this email finds you well. ",
        "",
        custom_paragraph,
        "",
        f"As an AI & healthcare engineer, I bring 6+ years of experience building scalable, high-impact healthcare solutions. I am eager to contribute to Valeo Health’s next phase of innovation and regional growth, aligning my expertise in AI, healthcare technology, and product development with your vision."
        "",
        "",

        f"Having recently relocated from the U.S. due to H1B immigration changes, I am available for immediate joining. I would greatly value a brief conversation with you or your technical leadership team to explore how I can help accelerate Valeo Health’s mission and deliver measurable impact."
         "",
         "",

        f"My resume is attached; I’d greatly appreciate a connection with your recruitment or technical leadership team to explore how I can add value to {company_name}'s success.",
        "",
    
        "Best regards,",
        "Simii Vasaikar",
        "+918828013130",
        "LinkedIn: https://www.linkedin.com/in/seeminvasaikar/"
    ]
    return "\n".join(lines)

import re

def clean_paragraph(text: str) -> str:
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    # Remove domain references like [wamda.com], (example.com), etc.
    text = re.sub(r'\[?\(?\b\w+\.(com|world|org|net|co|io|ae)\b\)?\]?', '', text, flags=re.I)
    # Remove unwanted special characters: () _ -
    text = re.sub(r'[()\-_]', '', text)
    # Remove extra greetings like "I understand", "Let me know", etc.
    text = re.sub(r'^(I understand\.|Let me know if.*!?)\s*', '', text, flags=re.I)
    # Remove extra spaces and blank lines
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = text.strip()
    return text


def fetch_company_news(company_name: str) -> str:
    prompt = (
    f"Research the most recent news, innovation, or project at {company_name} "
    "related to AI, technology, or healthcare tech, and mention that the company stood out as a leader during my research of the next-gen technology leaders in the UAE. "
    "Write a concise 2-3 sentence paragraph suitable for a cold email introduction, position me as an asset for them, and show my willingness to build with them. "
    "Do NOT include any greetings, conclusions, headers, footers, follow-up sentences, websites, or special characters like (), _, -, or em dashes (—). "
    "Do NOT include website URLs or references. Only output the relevant content for the email paragraph. "
    "Replace em dashes with commas or periods for natural readability. "
    "Output only the paragraph without any assistant commentary or explanations and form clean sentences."
)

    try:
        resp = client.responses.create(
            model="gpt-4o",  # or “gpt-4o-mini” depending on your access
            input=prompt,
            tools=[{"type": "web_search"}]
        )
        custom_para = None
        for out in resp.output:
            if hasattr(out, "content"):
                for block in out.content:
                    if hasattr(block, "text"):
                        custom_para = block.text.strip()
                        break
            if custom_para is None and isinstance(out, dict) and "content" in out:
                for blk in out["content"]:
                    txt = blk.get("text")
                    if txt:
                        custom_para = txt.strip()
                        break
            if custom_para:
                break
        if not custom_para:
            raise Exception("No text in web_search output")
        return clean_paragraph(custom_para)
    except Exception as e:
        print("Web search failed; falling back to generic intro:", e)
        return f"I’m impressed by {company_name}’s ongoing work and excited to reach out."

def generate_custom_email(contact_name: str, company_name: str) -> str:
    custom_para = fetch_company_news(company_name)
    return format_email(contact_name, company_name, custom_para)

def main():
    email = generate_custom_email("Sundeep", "ValeoHealth")
    print("\n" + email + "\n")

if __name__ == "__main__":
    main()
