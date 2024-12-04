import re

def extract_python_code(response: str) -> str:
    """
    Extract Python code blocks from a ChatGPT response.

    Args:
        response (str): The full response from ChatGPT.

    Returns:
        str: Extracted Python code or an empty string if no code is found.
    """
    # Regular expression to find code blocks enclosed in triple backticks
    code_blocks = re.findall(r"```python(.*?)```", response, re.DOTALL)
    
    # Combine all found code blocks
    extracted_code = "\n\n".join(code_blocks).strip()
    
    return extracted_code or "No Python code found in the response."