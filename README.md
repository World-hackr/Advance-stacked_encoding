# Advance-stacked_encoding
# Multi-Division Waveform Stacking & Envelope Tool

This Python script enables you to load multiple **.wav** files, display each one in a separate subplot, draw custom envelopes over them, and reposition those envelopes. Finally, it generates modified versions of each waveform based on the envelopes you drew.

## Key Features

1. **Multiple .wav Inputs**  
   - Prompts for the number of divisions (subplots) and loads that many audio files.
   - Each .wav is converted to mono (if needed) and normalized to `[-1, 1]`.

2. **Interactive Envelope Drawing**  
   - Each subplot corresponds to one audio file.
   - Click and drag to draw separate envelopes for positive and negative amplitudes.
   - Press **Enter** to finalize your drawing for all subplots.

3. **Reposition Phase**  
   - After drawing, you can drag each drawn envelope vertically in its subplot.
   - Allows you to offset the entire envelope up or down.
   - Press **Enter** again to finalize repositioning.

4. **Output**  
   - **PNG**: Saves the final drawing (`final_drawing.png`) in a newly created folder named after the first .wav file.
   - **CSV & WAV**: For each .wav file, writes:
     - A **CSV** with peak data (index, original peak, drawn peak, scaling factor).
     - A **modified WAV** file with peaks scaled to match your drawn envelope.

## Dependencies

- Python 3.x  
- [NumPy](https://numpy.org/)  
- [Matplotlib](https://matplotlib.org/)  
- [SciPy](https://www.scipy.org/)

Install via pip:
```bash
pip install numpy matplotlib scipy
