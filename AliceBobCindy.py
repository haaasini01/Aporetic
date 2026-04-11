import os
import re
import time
from google import genai
from google.genai import types
import wolframalpha
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
math_engine = wolframalpha.Client(os.environ.get("WOLFRAM_APP_ID"))

class SocraticGPT:
    def __init__(self, role, n_round=10, model="gemini-2.5-flash"):
        self.role = role
        self.model = model
        self.n_round = n_round
        self.history = []
    def set_question(self, question):
        if self.role == "Socrates":
            self.history.append({
                "role": "system",
                "content": f"You are Socrates, a private tutor helping a student learn to solve challenging problems. The student will ask a question. Your job is not to give the answer directly. Instead, guide the student with hints, questions, and step-by-step tasks that lead them to discover the answer on their own.\n\nDo not provide a direct solution. Instead: ask the student to think through the problem, suggest the next smaller task, encourage them when they are on the right track, and redirect them if they try to get the answer too quickly. If the student asks if their approach is right, evaluate it and help them refine it. If they ask you directly for the answer, refuse and steer them back to reasoning.\n\nIf the student seems to arrive at the correct idea, use encouraging feedback like \"good\", \"yay\", or \"that's a good direction\".\n\nYou have access to WolframAlpha for verification of calculations and facts. Use this information to guide the student accurately, but maintain the Socratic method—do not reveal direct answers.\n\nThe problem statement is: {question}."
            })
            self.history.append({
                "role": "assistant",
                "content": "Let's work through this together step by step. What part of the problem do you understand so far?"
            })
            
    def get_response(self, temperature=None):
        # Consult WolframAlpha for the latest user message
        wolfram_context = ""
        if len(self.history) > 0 and self.history[-1]["role"] == "user":
            user_msg = self.history[-1]["content"]
            wolfram_result = self._query_wolfram_alpha(user_msg)
            if wolfram_result:
                wolfram_context = f"\n\n[Quick fact check via WolframAlpha: {wolfram_result}]"
        
        try:
            contents = []
            for i, msg in enumerate(self.history):
                role = "model" if msg["role"] == "assistant" else "user"
                # Add WolframAlpha context to the last user message
                content = msg["content"]
                if i == len(self.history) - 1 and msg["role"] == "user" and wolfram_context:
                    content += wolfram_context
                
                if contents and contents[-1].role == role:
                    contents[-1].parts[0].text += "\n\n" + content
                else:
                    contents.append(types.Content(role=role, parts=[types.Part.from_text(text=content)]))
            
            config = types.GenerateContentConfig()
            if temperature:
                config.temperature = temperature
                
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    res = client.models.generate_content(
                        model=self.model,
                        contents=contents,
                        config=config
                    )
                    msg = res.text
                    break
                except Exception as api_err:
                    err_msg = str(api_err).lower()
                    if attempt < max_retries - 1 and ("429" in err_msg or "quota" in err_msg or "limit" in err_msg or "retry" in err_msg):
                        time.sleep(60)
                    else:
                        raise api_err

        except Exception as e:
            err_str = str(e).lower()
            if "token limit" in err_str or "context length" in err_str or "maximum context" in err_str:
                msg = "The context length exceeds my limit... "
            else:
                msg = f"I encounter an error when using my backend model.\n\n Error: {str(e)}"
        
        self.history.append({
                "role": "assistant",
                "content": msg
            })
        return msg
    
    def _query_wolfram_alpha(self, text):
        """Query WolframAlpha for factual/mathematical information from user input."""
        try:
            res = math_engine.query(text)
            result = next(res.results).text
            return result
        except Exception:
            return None
            
    def update_history(self, message):
        self.history.append({
            "role": "user",
            "content": message
        })
        
    def add_reference(self, question, answer):
        self.history.append({
            "role": "system",
            "content": f"The WolframAlpha answer to \"{question}\" is \"{answer}\""
        })

    def add_python_feedback(self, msg):
        self.history.append({
            "role": "system",
            "content": f"Excuting the Python script. It returns \"{msg}\""
        })
        
    def add_feedback(self, question, answer):
        self.history.append({
            "role": "system",
            "content": f"Hasini's feedback to \"{question}\" is \"{answer}\""
        })

def ask_WolframAlpha(text):
    pattern = r"@Check with WolframAlpha:\s*(.*)"
    matches = re.findall(pattern, text)
    results = []
    
    if len(matches) == 0:
        return None
    
    for match in matches:
        res = math_engine.query(match)
        print(f"[... Using WolframAlpha to solve: {match}]\n")
        time.sleep(5)
        try:
            results.append({"question": match, 
                            "answer": next(res.results).text})
        except:
            results.append({"question": match, 
                            "answer": "No response from WolframAlpha..."})
    return results


def write_Python(text):
    matches, matches2 = [], []
    pattern = r"@write_code[\s\S]*?```(?:\w+\n)?([\s\S]*?)```"
    matches = re.findall(pattern, text)
    pattern2 = r"```[\s\S]*?@write_code\s*(?:\w+\n)?([\s\S]*?)```"
    matches2 = re.findall(pattern2, text)

    if len(matches2) > 0:
        matches = matches2
    else:
        matches = matches + matches2

    pattern3 = r"(@write_code\s*(.*))"
    check_write = re.findall(pattern3, text)
    
    if len(check_write) == 0:
        return None

    print("<Writing Python scripts>\n")
    for match in matches:
        print("[... Writing Python scripts:]\n")
        print(match)

    return matches


def execute_Python(text):
    pattern = r"@execute[\s\S]*?```(?:\w+\n)?([\s\S]*?)```"
    matches = re.findall(pattern, text)

    pattern2 = r"(@execute\s*(.*))"
    check_exe = re.findall(pattern2, text)
    
    if len(check_exe) == 0:
        return None

    print("<Excuting Python scripts>\n")
    for match in matches:
        print("[... Excuting Python scripts:]\n")
        print(match)

    return matches


def ask_Hasini(text):
    pattern = r"@Check with Hasini:\s*(.*)"
    matches = re.findall(pattern, text)
    results = []
    
    if len(matches) == 0:
        return None
    
    for match in matches:
        res = math_engine.query(match)
        print(f"[... Asking Hasini's opinon on: {match}]\n")
        time.sleep(5)
        try:
            results.append({"question": match, 
                            "answer": input("Hasini's feedback")})
        except:
            results.append({"question": match, 
                            "answer": "No response from Hasini..."})
    return results


def need_to_ask_Hasini(text):
    pattern = r"@Check with Hasini:\s*(.*)"
    matches = re.findall(pattern, text)
    
    if len(matches) == 0:
        return False
    
    return matches