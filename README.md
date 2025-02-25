# Audio Envelope Processing Tool

## Overview
This tool provides an interactive interface to process audio (`.wav`) files by allowing users to draw custom envelopes over the waveform. It supports color customization, real-time audio preview, and produces multiple output files including visualizations, envelope data, and modified audio. The tool also features automatic stereo to mono conversion and allows repeated processing of different file sets without restarting the program.

## Features
- **Multiple File Processing:**  
  - Process one or more `.wav` files simultaneously by creating multiple divisions (subplots).
  - After processing a set of files, the user is prompted to process another set without needing to restart the program.

- **Stereo to Mono Conversion:**  
  - If an input audio file is stereo, the tool automatically converts it to mono by averaging the channels.

- **Interactive Envelope Drawing:**  
  - **Mouse-based Drawing:** Click and drag on the waveform to create envelope curves.
  - **Dual Envelopes:** Draw separate positive and negative envelopes.
  - **Live Update:** The envelope drawing is updated in real time as you move the mouse.

- **Keyboard Shortcuts:**  
  - **`p` (Preview):** Preview the modified audio based on the drawn envelope.
  - **`r` (Reset):** Reset the current envelope drawing.
  - **`u` (Undo):** Undo the last drawing stroke.

- **Color Customization:**  
  - **Drawing Canvas Color Picker:** Customize the background and envelope colors before starting the drawing.
  - **Final Drawing Customization:** Change colors after drawing is complete to adjust the final visual output.
  - **Additional Phases:** Customize colors for the "natural_lang" and "wave_comparison" visualizations.
  
- **Output Generation:**  
  - **Images:** Saves multiple PNG files:
    - `final_drawing.png` – The initial drawing with your customizations.
    - `natural_lang.png` – A visualization with the faint original wave removed and a highlighted modified wave.
    - `wave_comparison.png` – A side-by-side comparison of the original and modified waveforms.
  - **CSV Files:** Exports envelope data (index, positive envelope, negative envelope) for each audio file.
  - **Modified Audio Files:** Saves the modified audio (with applied envelopes) as new `.wav` files.

## Requirements
- Python 3.x
- Required packages:
  - `numpy`
  - `matplotlib`
  - `scipy`
  - `sounddevice`
- A system capable of audio playback (for the preview feature).

## Installation
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
