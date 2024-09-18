# Meeting Summarizer for Windows 11 

This project was originally based on [MeetingSummarizer](https://github.com/rajpdus/MeetingSummarizer), but has since evolved into an independent project with new features and goals. This project is tailored for Windows 11 users and provides a CLI utility to record audio from multiple sources and generate summaries of the recorded content. It leverages FFmpeg for audio recording, Whisper for transcription, and OpenAI's GPT model for summarization, offering a streamlined solution for capturing and distilling meeting information on Windows 11 platforms.

## Prerequisites 

- Python: Download and install the latest version of Python from the [official website](https://www.python.org/downloads/) or use your package manager.
- FFmpeg: Install FFmpeg using a package manager. For Windows, you can use [Chocolatey](https://chocolatey.org/):

``` python
choco install ffmpeg-full
```

- OpenAI API Key: Sign up for an account on the [OpenAI platform](https://platform.openai.com/) and obtain your API key.

- Create .env file with the following:

``` python
OPENAI_API_KEY=<your-openai-api-key>
```

- Run the following command in the terminal, to list your microphones and audio devices:

``` python
ffmpeg -list_devices true -f dshow -i dummy 
```

- Get the microphone and audio devices names and replace in cli.py file

## Whisper ASR 

Whisper is an Automatic Speech Recognition (ASR) system developed by OpenAI. It converts spoken language into written text and is trained on a large amount of multilingual and multitask supervised data collected from the web.

repo: [whisper](https://github.com/openai/whisper)

## CLI Utility 

The command-line interface (CLI) utility allows you to record meetings and transcribe and summarize the recordings using the following commands:

1. Record a meeting:

``` python
python cli.py record output.mp3
```

2. Stop recording:

``` python
ctrl + c
```

3. Transcribe and summarize a recorded meeting:

``` python
python cli.py summarize output.mp3
```

Replace `output.mp3` with your desired output file name.

## Requirements 

Install the required Python packages using the following command:

``` python
pip install -r requirements.txt
```

## Important notes 

- Change input and output devices to Virtual Audio Device in Windows sounds settings
- If you using 'Teams' or similar, you need to foward your speakers to the Virtual Audio Device as well.

## License 

This project is licensed under the [Apache License](LICENSE).
