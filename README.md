<div align="center">

🔉 AudioSeal - Digital Audio Watermarking

A web application to hide secret messages inside audio files using steganography.

Designed by OPH

View the Live Demo Here

audioseal-app.onrender.com

</div>

📖 About The Project

AudioSeal is a web-based tool that provides a user-friendly interface for digital steganography in audio files. It allows you to embed a secret text message into an audio file (like .wav, .mp3, or .flac) and then extract it later. This project demonstrates core concepts of Digital Signal Processing (DSP) wrapped in a modern, responsive web application with a sleek "glassmorphism" design.

The core of the application uses a Least Significant Bit (LSB) algorithm to subtly alter the audio data in a way that is imperceptible to the human ear but can be detected by the software.

✨ Key Features

Embed Watermark: Hide any text message within a supported audio file.

Detect Watermark: Extract the hidden message from a sealed audio file.

Drag & Drop Interface: Modern, easy-to-use file upload system.

Multi-Format Support: Works with .wav, .mp3, .flac, and other common audio formats thanks to pydub.

Secure & Private: All processing is done on the server, and files are not stored permanently.

Responsive Design: A beautiful UI that works on both desktop and mobile devices.

🛠️ Tech Stack

This project was built using a combination of backend signal processing and modern frontend technologies:

<p align="center">
<img src="https://www.google.com/search?q=https://img.shields.io/badge/Python-3776AB%3Fstyle%3Dfor-the-badge%26logo%3Dpython%26logoColor%3Dwhite" alt="Python">
<img src="https://www.google.com/search?q=https://img.shields.io/badge/Flask-000000%3Fstyle%3Dfor-the-badge%26logo%3Dflask%26logoColor%3Dwhite" alt="Flask">
<img src="https://www.google.com/search?q=https://img.shields.io/badge/HTML5-E34F26%3Fstyle%3Dfor-the-badge%26logo%3Dhtml5%26logoColor%3Dwhite" alt="HTML5">
<img src="https://www.google.com/search?q=https://img.shields.io/badge/CSS3-1572B6%3Fstyle%3Dfor-the-badge%26logo%3Dcss3%26logoColor%3Dwhite" alt="CSS3">
<img src="https://www.google.com/search?q=https://img.shields.io/badge/JavaScript-F7DF1E%3Fstyle%3Dfor-the-badge%26logo%3Djavascript%26logoColor%3Dblack" alt="JavaScript">
</p>

🚀 How To Run Locally

To get a local copy up and running, follow these simple steps.

Prerequisites

Python 3.8+

pip (Python package installer)

FFmpeg: This is a crucial dependency for handling different audio formats.

Download it from the official FFmpeg website.

Make sure to add its bin directory to your system's PATH.

Installation & Setup

Clone the repository:

git clone [https://github.com/your-username/AudioSeal-WebApp.git]([https://github.com/your-username/AudioSeal-WebApp.git](https://github.com/op-h/AudioSeal-WebApp))
cd AudioSeal-WebApp


Create and activate a virtual environment:

# Create the environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate


Install the required packages:

pip install -r requirements.txt


Run the Flask application:

python app.py
