import subprocess

python_files = [r"src/agents/temperatures/temperatures.py", r"src/utils/discord_message.py"]

processes = []
for python_file in python_files:
    processes.append(subprocess.Popen(["python", python_file]))

for process in processes:
    process.wait()