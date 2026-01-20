import pdfplumber
import sys

def extract_text(pdf_path):
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    pdf_path = r"D:\Antigravity\Jackypotato\xhs_articles\教学文档---1211_史上最详细教程：如何申请_Gemini_3_会员，使用_Antigravity（小白也能一步成功）.pdf"
    content = extract_text(pdf_path)
    # Output to stdout with UTF-8 encoding
    sys.stdout.reconfigure(encoding='utf-8')
    print(content)
