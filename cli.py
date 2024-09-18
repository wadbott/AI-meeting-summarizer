import os
import sys
import time
import threading
import signal
import subprocess
from datetime import datetime
from openai import OpenAI
import tiktoken
import torch
import whisper
from dotenv import load_dotenv

whisper_model = "small"
command_prompt = "Crie tópicos claros e concisos sem rótulos resumindo as informações principais"
stop_ticker = False

def display_ticker():
    start_time = time.time()
    while not stop_ticker:
        elapsed_time = time.time() - start_time
        minutes, seconds = divmod(int(elapsed_time), 60)
        sys.stdout.write(f'\rRecording: {minutes:02d}:{seconds:02d}')
        sys.stdout.flush()
        time.sleep(1)
        
def record_meeting(output_filename):
    global stop_ticker

    def signal_handler(sig, frame):
        global stop_ticker
        stop_ticker = True
        print("\nRecording stopped.")
        process.terminate()
        sys.exit(0)

    # Handle Ctrl + C to stop recording
    signal.signal(signal.SIGINT, signal_handler)

    # Command to capture audio from both devices (Microphone and Virtual Cable)
    command = [
        'ffmpeg',
        '-f', 'dshow',  # DirectShow capture for Windows
        '-i', 'audio=CABLE Output (VB-Audio Virtual Cable)',  # System audio from Virtual Cable
        '-f', 'dshow',  # Capture the microphone input
        '-i', 'audio=Microphone (FIFINE K670 Microphone)',  # Microphone input
        '-filter_complex', '[0:a][1:a]amix=inputs=2:duration=longest[aout]',  # Mix both audio inputs
        '-map', '[aout]',  # Map the mixed audio to the output
        '-c:a', 'libmp3lame',  # Use MP3 codec
        '-q:a', '2',  # Set audio quality (0-9, lower is better)
        '-y',  # Overwrite output file if it exists
        output_filename
    ]

    # Start ffmpeg subprocess
    process = subprocess.Popen(command, stderr=subprocess.PIPE)

    # Start ticker thread to display recording time
    ticker_thread = threading.Thread(target=display_ticker)
    ticker_thread.start()

    # Print any ffmpeg errors to the console
    print_ffmpeg_errors(process)

    # Wait for ticker thread to finish
    ticker_thread.join()


def print_ffmpeg_errors(process):
    """Read and print FFmpeg errors from stderr."""
    for line in iter(process.stderr.readline, b''):
        print(line.decode(), end='')

def transcribe_audio(filename):

    # load model
    devices = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = whisper.load_model(whisper_model, device=devices)

    # load audio and pad/trim it to fit 30 seconds
    audio = whisper.load_audio(filename)

    print("Beginning Transcribing Process...")

    result = model.transcribe(audio)

    return result['text']

def summarize_transcript(transcript):

    def generate_summary(prompt):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em resumir transcrições de reuniões. Seu objetivo é criar um resumo conciso e bem estruturado, destacando os principais pontos discutidos, decisões tomadas e ações a serem realizadas. Organize o resumo em tópicos claros e concisos, mantendo a essência da reunião em um formato fácil de ler e compreender."},
                {"role": "user", "content": f"{command_prompt}: {prompt}"}
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()

    chunks = []
    prompt = "Por favor, resuma o seguinte texto:\n\n"
    text = prompt + transcript
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    while tokens:
        chunk_tokens = tokens[:15000]
        chunk_text = tokenizer.decode(chunk_tokens)
        chunks.append(chunk_text)
        tokens = tokens[15000:]

    summary = "\n".join([generate_summary(chunk) for chunk in chunks])

    return summary

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} [record|summarize] output.mp3")
        sys.exit(1)

    load_dotenv()
    api_key = os.getenv('OPEN_API_KEY')
    if api_key is None:
        print("Environment variable OPEN_API_KEY not found. Exiting...")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    action = sys.argv[1]
    output_filename = sys.argv[2]

    if action == "record":
        record_meeting(output_filename)
    elif action == "summarize":
        transcript = transcribe_audio(output_filename)
        summary = summarize_transcript(transcript)
        
        # Create 'output' folder if it doesn't exist
        os.makedirs('output', exist_ok=True)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save transcript
        transcript_filename = f"output/transcript_{timestamp}.txt"
        with open(transcript_filename, 'w', encoding='utf-8') as f:
            f.write(transcript)
        
        # Save summary
        summary_filename = f"output/summary_{timestamp}.txt"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"Transcript saved to: {transcript_filename}")
        print(f"Summary saved to: {summary_filename}")
        
        print(f"TRANSCRIPT:{transcript}\n")
        print(f"SUMMARY_START:\n{summary}\nSUMMARY_END\n")
    else:
        print(f"Invalid action. Usage: python {sys.argv[0]} [record|summarize] output.mp3")
        sys.exit(1)
