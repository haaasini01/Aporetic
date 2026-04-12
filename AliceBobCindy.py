import os
import re
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import wolframalpha
from dotenv import load_dotenv

load_dotenv()

math_engine = wolframalpha.Client(os.environ.get("WOLFRAM_APP_ID"))

class SocraticGPT:
    def __init__(self, role, n_round=10, model="gemini-2.0-flash"):
        self.role = role
        self.model = model
        self.n_round = n_round
        self.history = []
        google_api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not google_api_key:
            raise ValueError(
                "Missing Google API key. Set GOOGLE_API_KEY or GEMINI_API_KEY in your environment."
            )
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=google_api_key,
            temperature=0.7,
            convert_system_message_to_human=True  # FIX: Gemini does not support SystemMessage natively
        )
        
    def set_question(self, question):
        if self.role == "Socrates":
            system_msg = (
                f"You are Socrates, a private tutor helping a student learn to solve challenging problems. "
                f"The student will ask a question. Your job is not to give the answer directly. "
                f"Instead, guide them with hints and questions.\n\n"
                f"IMPORTANT: Since this is the start of the session, your very first response must be: "
                f"'Let's work through this together step by step. What part of the problem do you understand so far?'\n\n"
                f"The problem statement is: {question}."
            )
            self.history.append(SystemMessage(content=system_msg))
    
    def get_response(self, temperature=None):
        wolfram_context = ""
        if len(self.history) > 0 and isinstance(self.history[-1], HumanMessage):
            user_msg = self.history[-1].content
            wolfram_result = self._query_wolfram_alpha(user_msg)
            if wolfram_result:
                wolfram_context = f"\n\n[Quick fact check via WolframAlpha: {wolfram_result}]"
        
        try:
            messages_to_send = self.history.copy()
            if wolfram_context and len(messages_to_send) > 0 and isinstance(messages_to_send[-1], HumanMessage):
                messages_to_send[-1] = HumanMessage(content=messages_to_send[-1].content + wolfram_context)
            
            res = self.llm.invoke(messages_to_send)
            msg = res.content
            
        except Exception as e:
            print(f"!!! Backend Error: {e}") 
            
            err_str = str(e).lower()
            if "token limit" in err_str or "context length" in err_str:
                msg = "The context length exceeds my limit... "
            else:
                msg = f"I encounter an error when using my backend model.\n\nError details: {str(e)}"
        
        self.history.append(AIMessage(content=msg))
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
        self.history.append(HumanMessage(content=message))
        
    def add_reference(self, question, answer):
        # FIX: Use HumanMessage + AIMessage pair instead of SystemMessage
        self.history.append(HumanMessage(content=f"What is the answer to: \"{question}\"?"))
        self.history.append(AIMessage(content=f"According to WolframAlpha, the answer is: \"{answer}\""))

    def add_python_feedback(self, msg):
        # FIX: Use HumanMessage instead of SystemMessage
        self.history.append(HumanMessage(content=f"I executed the Python script and it returned: \"{msg}\""))
        
    def add_feedback(self, question, answer):
        # FIX: Use HumanMessage instead of SystemMessage
        self.history.append(HumanMessage(content=f"Hasini's feedback to \"{question}\" is \"{answer}\""))

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
    
    if len(matches) == 0:
        return None
    
    return matches


def need_to_ask_Hasini(text):
    pattern = r"@Check with Hasini:\s*(.*)"
    matches = re.findall(pattern, text)
    
    if len(matches) == 0:
        return False
    
    return matches