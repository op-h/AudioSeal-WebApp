<div align="center">

# 🔉 AudioSeal - Digital Audio Watermarking

*A cohesive steganography application blending Digital Signal Processing and Information Theory, styled with a Hacker Aesthetic.*

Done by **OPH - K**

[View the Live Demo Here](https://audioseal-app.onrender.com) *(Note: May not reflect the most recent local updates)*

</div>

---

## 📖 Executive Summary
AudioSeal is a web-based, full-stack application designed to seamlessly hide secret text messages within audio files. The application functions as both an encrypter (embedding a payload) and a decrypter (extracting and revealing the payload). 

This project explores complex concepts from the **Information Theory and Coding** subject, specifically focusing on data redundancy and fault-correction within noisy channels. This technical stack features a Flask Python backend to handle heavy Digital Signal Processing (DSP) and a sleek, fully-customized UI built in raw HTML/CSS/JS.

---

## ✨ Features & Project Scope

* **TryHackMe Hacker Aesthetic:** A modern, dark-mode glassmorphism interface featuring deep shades (`#111827`) and vivid red accents (`#ed1b24`), mimicking the popular cybersecurity platform feeling.
* **Information Theory Integration:** A classic **Hamming (7,4)** Error Correction Block Code algorithm handles binary payloads to ensure zero data corruption during the audio file encoding process.
* **Digital Signal Processing (DSP):** Uses Python logic alongside libraries like `pydub` and `soundfile` to manipulate and read exact audio frequencies up to the binary level.
* **Least Significant Bit (LSB) Steganography:** Replaces indistinguishable bits on an audio wave track with secret data without affecting human perception of the song or file.

---

## 🧬 Technical Implementation & Algorithms

### 1. The LSB (Least Significant Bit) Method
To hide text inside audio, the file is digitized and broken down into binary samples. Under standard 16-bit audio, the final, least significant bit of a number causes the lowest structural change if manipulated. The `embed_lsb` function forcefully clears out the last bit of millions of audio samples and inserts our text payload's bit instead. To humans, the audio sounds perfectly normal, but to the computer, there is a whole textual stream inside the background noise.

### 2. Hamming (7,4) Error Correcting Code
During audio processing, conversion, or transmission, it's possible for slight degradation to occur—a "noisy channel." To counteract this, the project utilizes the **Hamming (7,4)** block code from Information Theory.

#### How it works:
1. **Encoding:** We break an 8-bit text character into two **4-bit** message blocks: `d1, d2, d3, d4`.
2. **Adding Redundancy:** We calculate 3 parity bits (`p1, p2, p3`) using XOR logic based on specific data combinations:
   * `p1 = d1 ⊕ d2 ⊕ d4`
   * `p2 = d1 ⊕ d3 ⊕ d4`
   * `p3 = d2 ⊕ d3 ⊕ d4`
3. **Transmission:** The 4 original bits are packed with the 3 parity bits to become a **7-bit** block, which is then fed into the LSB algorithm.
4. **Decoding:** Upon extract, the app grabs 7 bits. It mathematically validates the parity bits to form a `Syndrome`. If the syndrome is equal to `0`, the data perfectly aligned. If the syndrome is > 0, we can use the exact decimal result of the syndrome to mathematically index *exactly which bit was corrupted* and permanently flip it back.

---

## 🛠️ Tech Stack & Dependencies

* **Backend Environment:** Python 3.8+
* **System Framework:** Flask web-server with secure Werkzeug routing logic.
* **Frontend Languages:** Vanilla ES6 Javascript, HTML5, raw custom styling variables in CSS3.
* **Audio DSP Tooling:** `pydub` (for file translation/ffmpeg connection), `soundfile`, `numpy` array manipulation.

---

## 🚀 Installation & Local Deployment

### Prerequisites
1. You must have Python installed.
2. You must have `FFmpeg` installed and added to your system's global `PATH` to allow `pydub` to convert `.mp3` formats.

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/op-h/AudioSeal-WebApp.git
   cd AudioSeal-WebApp
   ```

2. **Initialize Environment & Install Packages:**
   ```bash
   python -m venv venv
   # Activate: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Boot Application:**
   ```bash
   python app.py
   ```
4. **Access UI:** Open `http://localhost:5000` via any browser.
