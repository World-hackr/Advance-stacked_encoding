# Envelope Waveform Editor

Envelope Waveform Editor is an interactive Python application that lets you generate, modify, and process audio waveforms visually. You can create custom audio waves, draw envelopes over them, adjust vertical spacing and centering, and finally generate modified audio files and images. This tool is designed to be both accessible to non-technical users and intriguing for technical enthusiasts.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [How It Works](#how-it-works)
  - [Custom Wave Generation](#custom-wave-generation)
  - [Drawing Canvas & Color Picker](#drawing-canvas--color-picker)
  - [Envelope Drawing and Editing](#envelope-drawing-and-editing)
  - [Vertical Spacing & Centering](#vertical-spacing--centering)
  - [Final Outputs](#final-outputs)
- [Installation & Requirements](#installation--requirements)
- [Usage Instructions](#usage-instructions)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Overview

The Envelope Waveform Editor allows you to:
- **Generate custom audio waves:** Choose between preset waveforms (sine, square, triangle, sawtooth) or enter your own parameters.
- **Interactively draw envelopes:** Use your mouse to draw over the waveform to specify positive and negative envelope adjustments.
- **Adjust display and audio properties:** Fine-tune vertical spacing, centering, and envelope shape using interactive sliders.
- **Export final files:** Save the modified audio as a WAV file (with DC offset correction) and export several PNG images showing different visualizations of your work (e.g., final drawing, natural language style, and wave comparison).

---

## Features

### For Non-Technical Users

- **Easy-to-use Interface:** Follow on-screen prompts to choose wave types, draw envelopes, and adjust the view without needing to know any coding.
- **Visual Feedback:** See your drawing exactly as it appears on the screen in the final image output.
- **Audio Preview:** Listen to a live preview of your modified audio to ensure it sounds as desired.
- **File Export:** Automatically save your work as WAV audio files and PNG images.

### For Tech Enthusiasts

- **Custom Wave Generation:** Specify frequency, samples per wavelength, and number of periods to create precise waveforms.
- **Envelope Editing:** The envelope is stored as separate positive and negative arrays, relative to a user-defined baseline. This data is saved in CSV format and later used to modify the waveform.
- **Interactive Sliders:** Adjust vertical spacing and centering using Matplotlib’s Slider widget.
- **DC Offset Correction:** When saving the final WAV file, the code subtracts the centering offset to eliminate unwanted DC bias.
- **Multiple Visualizations:** The application exports three types of images:
  - **Final Drawing:** The envelope exactly as drawn.
  - **Natural Language Visualization:** A strict, colored line representation of the envelope.
  - **Wave Comparison:** Overlay of the original and modified waveforms for direct comparison.
- **CSV as Data Source:** The envelope data is exported to CSV files, which are later reloaded to recalculate and generate the modified audio and visualizations.

---

## How It Works

### Custom Wave Generation

- **Presets & Manual Entry:** Choose from preset waveforms or manually enter frequency, samples per wavelength, and periods.
- **Audio File Creation:** The chosen parameters generate a normalized waveform, which is then saved as a WAV file.

### Drawing Canvas & Color Picker

- **Color Picker:** Choose background, positive, and negative colors for the drawing canvas through a simple text-based menu.
- **Drawing Interface:** The canvas displays the waveform, and you draw the envelope over it using the mouse.

### Envelope Drawing and Editing

- **Envelope Data:** The user’s mouse input is captured relative to a “centering” baseline (offset). Two arrays—one for positive envelope values and one for negative—are created.
- **CSV Export:** After drawing, the envelope data is saved into CSV files, serving as a “source of truth” for further processing.

### Vertical Spacing & Centering

- **Vertical Spacing:** Interactive sliders allow you to adjust the vertical spacing of the subplots, ensuring your drawings are clearly visible.
- **Centering Phase:** A centering slider shifts the waveform up or down. For visualization, the drawn envelope is shown with this offset, but for the final WAV file, the offset is subtracted to remove any DC bias.

### Final Outputs

- **Modified Audio Files:** The CSV envelope data is reloaded to recalculate the modified waveform. When creating the final WAV file, the centering offset is subtracted to avoid a DC offset.
- **PNG Images:**
  - **Final Drawing:** Saves the envelope as it was drawn.
  - **Natural Language Visualization:** Uses a strict, colored line to represent the envelope while keeping the drawn shift intact.
  - **Wave Comparison:** Overlays the original and modified waveforms for easy comparison, also maintaining the envelope’s shifted position.

---

## Installation & Requirements

- **Python 3.x**
- Required libraries:
  - `matplotlib`
  - `numpy`
  - `scipy`
  - `sounddevice`
  - `csv` (standard library)
  - `os`, `sys`, `shutil` (standard libraries)

To install the Python packages (if not already installed):

```bash
pip install matplotlib numpy scipy sounddevice
Usage Instructions
Run the Script:
Execute the script in your terminal:
bash
Copy
Edit
python your_script_name.py
Follow Prompts:
Choose whether to generate a custom waveform or use an existing WAV file.
Pick colors for the drawing canvas and envelope lines.
Adjust vertical spacing and centering using interactive sliders.
Use your mouse to draw the envelope on the displayed waveform.
Preview your modified audio by pressing p, reset or undo changes with r or u.
Export Files:
After completing the drawing phase, the application will export:
CSV files containing the envelope data.
A final drawing image (final_drawing.png).
Modified audio files (WAV).
Additional visualizations (natural_lang.png and wave_comparison.png).
Troubleshooting
No Audio Output: Ensure your sound device is configured correctly and the volume is up.
File Not Found Errors: Double-check the paths provided when prompted.
Graphical Issues: If the waveform looks squeezed or shifted, verify the centering slider and ensure the axis limits are set to [0, num_points].
License
This project is provided "as is" without warranty of any kind. You may use, modify, and distribute this tool according to your needs.

