import os
import soundfile as sf
import numpy as np
from pydub import AudioSegment

def text_to_bits(text):
    """Converts a string to its binary representation."""
    return ''.join(format(ord(i), '08b') for i in text)

def bits_to_text(bits):
    """Converts a binary string back to text."""
    if len(bits) % 8 != 0:
        bits = bits[:len(bits) - (len(bits) % 8)]
    try:
        return "".join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8))
    except (ValueError, TypeError):
        return ""

def embed_lsb(input_file_path, watermark_text, output_file_path):
    """Embeds a text watermark into an audio file using the LSB method."""
    temp_wav_path = os.path.splitext(input_file_path)[0] + "_temp.wav"
    try:
        # --- CHANGE: Added specific error handling for file loading ---
        try:
            audio = AudioSegment.from_file(input_file_path)
        except Exception as e:
            raise ValueError(f"Could not read audio file. It might be corrupt or an unsupported format. Error: {e}")
        # --- END CHANGE ---
        
        audio.export(temp_wav_path, format="wav")

        audio_data, samplerate = sf.read(temp_wav_path, dtype='int16')
        working_data = audio_data.copy()
    
        if working_data.ndim > 1:
            working_data = working_data[:, 0]

        watermark_text += "[END]"
        watermark_bits = text_to_bits(watermark_text)
    
        if len(watermark_bits) > len(working_data):
            raise ValueError("Audio file is too small to hold the watermark. Please use a larger file or shorter message.")

        for i, bit in enumerate(watermark_bits):
            if bit == '1':
                working_data[i] |= 1
            else:
                working_data[i] &= ~1
            
        if audio_data.ndim > 1:
            audio_data[:, 0] = working_data
            final_data = audio_data
        else:
            final_data = working_data

        sf.write(output_file_path, final_data, samplerate)
        return True
    finally:
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)

def detect_lsb(input_file_path):
    """Detects a text watermark from an audio file efficiently."""
    temp_wav_path = os.path.splitext(input_file_path)[0] + "_temp.wav"
    try:
        # --- CHANGE: Added specific error handling for file loading ---
        try:
            audio = AudioSegment.from_file(input_file_path)
        except Exception as e:
            raise ValueError(f"Could not read audio file. It might be corrupt or an unsupported format. Error: {e}")
        # --- END CHANGE ---

        audio.export(temp_wav_path, format="wav")
        audio_data, _ = sf.read(temp_wav_path, dtype='int16')

        if audio_data.ndim > 1:
            audio_data = audio_data[:, 0]

        extracted_bits = []
        decoded_text = ""
        # The length of the end marker "[END]" is 5 characters * 8 bits/char = 40 bits
        end_marker_len = 40 

        for sample in audio_data:
            extracted_bits.append(str(sample & 1))
            
            # Process every 8 bits (one character)
            if len(extracted_bits) == 8:
                byte_str = "".join(extracted_bits)
                try:
                    char = chr(int(byte_str, 2))
                    decoded_text += char
                except ValueError:
                    # Ignore bytes that aren't valid characters
                    pass
                extracted_bits = [] # Reset for the next byte

                # Efficiently check if the message has ended
                if decoded_text.endswith("[END]"):
                    return decoded_text[:-5] # Return text without the "[END]" marker
        
        # If loop finishes without finding the marker
        return "[No Watermark Found]"
    finally:
        # This block ensures the temp file is ALWAYS deleted
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
