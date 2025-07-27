import subprocess

def call_ollama(prompt: str, model: str = "llama3") -> str:
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt.encode("utf-8"),
            capture_output=True,
            check=True
        )
        return result.stdout.decode("utf-8").strip()
    except subprocess.CalledProcessError as e:
        print(f"Ollama call failed:\n{e.stderr.decode('utf-8')}")
        raise