import io
import numpy as np
import soundfile as sf
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

def text_to_bits(text):
    """Converts a text string into a bit string."""
    bits = bin(int.from_bytes(text.encode('utf-8', 'surrogatepass'), 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))

def bits_to_text(bits):
    """Converts a bit string back into a text string."""
    n = int(bits, 2)
    try:
        return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode('utf-8', 'surrogatepass') or '\0'
    except Exception:
        return "[Error: Could not decode bits]"

def embed_lsb(input_file_path, watermark_text, output_file_path):
    """
    Embeds a watermark into an audio file using LSB steganography.
    This version is more robust and provides better error handling.
    """
    try:
        # Step 1: Load and standardize audio using pydub
        audio_segment = AudioSegment.from_file(input_file_path)
        # Standardize to a known format: 16-bit PCM, single channel (mono) for consistency
        audio_segment = audio_segment.set_channels(1)
        audio_segment = audio_segment.set_sample_width(2) # 2 bytes = 16 bits
    except CouldntDecodeError:
        raise Exception("Could not decode audio file. It might be corrupt or an unsupported format.")
    except Exception as e:
        # This often catches FFmpeg issues if it's not installed or not in the system's PATH
        raise Exception(f"Error loading audio file. Ensure ffmpeg is correctly installed. Original error: {e}")

    # Step 2: Convert pydub segment to a processable format for soundfile
    wav_io = io.BytesIO()
    audio_segment.export(wav_io, format="wav")
    wav_io.seek(0)
    audio_data, samplerate = sf.read(wav_io, dtype='int16')

    # Step 3: Prepare watermark
    watermark_bits = text_to_bits(watermark_text + "[END]")
    if len(watermark_bits) > len(audio_data):
        raise ValueError("Audio file is too short to hold the secret message.")

    # Step 4: Embed bits into audio data using LSB
    for i, bit in enumerate(watermark_bits):
        if bit == '1':
            audio_data[i] = audio_data[i] | 1  # Set LSB to 1
        else:
            audio_data[i] = audio_data[i] & ~1 # Set LSB to 0

    # Step 5: Save the modified audio data back to a WAV file
    sf.write(output_file_path, audio_data, samplerate)
    return True


def detect_lsb(input_file_path):
    """
    Detects a watermark from an audio file.
    """
    try:
        # Step 1: Load audio, ensuring it's read as 16-bit integers
        audio_data, samplerate = sf.read(input_file_path, dtype='int16')
    except Exception as e:
        raise Exception(f"Could not read audio file for detection. Is it a valid WAV file? Error: {e}")
        
    # Step 2: Extract LSB from each sample
    extracted_bits = ""
    for sample in audio_data:
        extracted_bits += str(sample & 1)
        # Optimization: Check for the [END] marker periodically
        if "[END]" in bits_to_text(extracted_bits):
            break
        # Safety break to prevent running on huge files forever
        if len(extracted_bits) > 40000: # Approx 5000 characters
             return "[No Watermark Found]"
    
    decoded_text = bits_to_text(extracted_bits)
    
    if "[END]" in decoded_text:
        return decoded_text.split("[END]")[0]
    else:
        return "[No Watermark Found]"

