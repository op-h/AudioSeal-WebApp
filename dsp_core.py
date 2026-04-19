import os
import soundfile as sf
import numpy as np
from pydub import AudioSegment

def hamming_encode(data_bits):
    """Encodes a 4-bit string into a 7-bit Hamming code string."""
    d1, d2, d3, d4 = int(data_bits[0]), int(data_bits[1]), int(data_bits[2]), int(data_bits[3])
    p1 = d1 ^ d2 ^ d4
    p2 = d1 ^ d3 ^ d4
    p3 = d2 ^ d3 ^ d4
    return f"{p1}{p2}{d1}{p3}{d2}{d3}{d4}"

def hamming_decode(encoded_bits):
    """Decodes a 7-bit Hamming code string back to 4 bits, correcting 1-bit errors."""
    if len(encoded_bits) < 7:
        return "0000"
    b1, b2, b3, b4, b5, b6, b7 = [int(x) for x in encoded_bits]
    p1_calc = b3 ^ b5 ^ b7
    p2_calc = b3 ^ b6 ^ b7
    p3_calc = b5 ^ b6 ^ b7
    
    s1 = b1 ^ p1_calc
    s2 = b2 ^ p2_calc
    s3 = b4 ^ p3_calc
    
    syndrome = s1 * 1 + s2 * 2 + s3 * 4
    
    corrected = [b1, b2, b3, b4, b5, b6, b7]
    if syndrome != 0:
        error_index = syndrome - 1
        if 0 <= error_index < 7:
            corrected[error_index] ^= 1
            
    return f"{corrected[2]}{corrected[4]}{corrected[5]}{corrected[6]}"

def text_to_bits(text):
    """Converts a string to its binary representation with Hamming(7,4) redundancy."""
    base_bits = ''.join(format(ord(i), '08b') for i in text)
    encoded = []
    for i in range(0, len(base_bits), 4):
        encoded.append(hamming_encode(base_bits[i:i+4]))
    return ''.join(encoded)

def bits_to_text(bits):
    """Decodes a binary string with Hamming(7,4) and converts back to text."""
    if len(bits) % 7 != 0:
        bits = bits[:len(bits) - (len(bits) % 7)]
        
    decoded_bits = ""
    for i in range(0, len(bits), 7):
        decoded_bits += hamming_decode(bits[i:i+7])
        
    if len(decoded_bits) % 8 != 0:
        decoded_bits = decoded_bits[:len(decoded_bits) - (len(decoded_bits) % 8)]
        
    try:
        return "".join(chr(int(decoded_bits[i:i+8], 2)) for i in range(0, len(decoded_bits), 8))
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
        # The length of the end marker "[END]" is 5 characters * 14 bits/char = 70 bits
        end_marker_len = 70 

        for sample in audio_data:
            extracted_bits.append(str(sample & 1))
            
            # Process every 14 bits (one character with Hamming parity bits)
            if len(extracted_bits) == 14:
                char_bits = "".join(extracted_bits)
                decoded_nibbles = hamming_decode(char_bits[:7]) + hamming_decode(char_bits[7:])
                try:
                    char = chr(int(decoded_nibbles, 2))
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
