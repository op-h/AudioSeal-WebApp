import os
import soundfile as sf
import numpy as np
from pydub import AudioSegment

def text_to_bits(text):
    """Converts a string to its binary representation."""
    return ''.join(format(ord(i), '08b') for i in text)

def bits_to_text(bits):
    """Converts a binary string back to text."""
    # Ensure the bit string has a length that is a multiple of 8
    if len(bits) % 8 != 0:
        bits = bits[:len(bits) - (len(bits) % 8)]
        
    try:
        # Convert binary chunks of 8 to characters
        return "".join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8))
    except (ValueError, TypeError):
        # Return empty string if conversion fails, preventing crashes
        return ""

def embed_lsb(input_file_path, watermark_text, output_file_path):
    """Embeds a text watermark into an audio file using the LSB method."""
    
    # --- Step 1: Convert input audio to a temporary WAV for processing ---
    audio = AudioSegment.from_file(input_file_path)
    # Use a temporary file path for the standardized WAV file
    temp_wav_path = os.path.splitext(input_file_path)[0] + "_temp.wav"
    audio.export(temp_wav_path, format="wav")

    # --- Step 2: Read the standardized WAV file ---
    audio_data, samplerate = sf.read(temp_wav_path, dtype='int16')
    working_data = audio_data.copy()
    
    # Ensure we are working with a single channel (mono) for consistency
    if working_data.ndim > 1:
        working_data = working_data[:, 0]

    # --- Step 3: Prepare the watermark data ---
    watermark_text += "[END]"  # Append an end-of-message marker
    watermark_bits = text_to_bits(watermark_text)
    
    if len(watermark_bits) > len(working_data):
        os.remove(temp_wav_path) # Clean up temp file
        raise ValueError("Audio file is too small to hold the watermark.")

    # --- Step 4: Embed the bits into the audio data ---
    for i, bit in enumerate(watermark_bits):
        if bit == '1':
            working_data[i] |= 1  # Set the LSB to 1
        else:
            working_data[i] &= ~1 # Set the LSB to 0 (clear it)
            
    # If original audio was stereo, rebuild it with the modified channel
    if audio_data.ndim > 1:
        audio_data[:, 0] = working_data
        final_data = audio_data
    else:
        final_data = working_data

    # --- Step 5: Save the watermarked audio and clean up ---
    sf.write(output_file_path, final_data, samplerate)
    os.remove(temp_wav_path) # Clean up temp file
    return True

def detect_lsb(input_file_path):
    """Detects a text watermark from an audio file."""

    # --- Step 1: Convert to WAV for consistent processing ---
    audio = AudioSegment.from_file(input_file_path)
    temp_wav_path = os.path.splitext(input_file_path)[0] + "_temp.wav"
    audio.export(temp_wav_path, format="wav")
    
    try:
        audio_data, _ = sf.read(temp_wav_path, dtype='int16')

        # --- FIX: Handle stereo audio by selecting only the first channel for detection ---
        if audio_data.ndim > 1:
            audio_data = audio_data[:, 0]

        extracted_bits = ""
        # Search for a reasonable length to avoid processing huge files entirely
        search_limit = min(len(audio_data), 50000) 

        for i in range(search_limit):
            extracted_bits += str(audio_data[i] & 1)
            
            # Check every 8 bits (every full character) for the [END] marker
            if (i + 1) % 8 == 0:
                current_text = bits_to_text(extracted_bits)
                if "[END]" in current_text:
                    os.remove(temp_wav_path) # Clean up temp file
                    return current_text.split("[END]")[0]
                        
        os.remove(temp_wav_path) # Clean up temp file
        return "[No Watermark Found]"
    except Exception as e:
        # Ensure cleanup happens even if an error occurs
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
        raise e

