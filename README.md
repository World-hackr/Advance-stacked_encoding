This repository contains a multi-division wave processing tool with the following features:

Custom Wave Generation (Presets/Manual)

Users can either pick a numeric preset (Sine, Square, Triangle, Sawtooth) or manually specify frequency, samples-per-wavelength, and periods.
Output filename is also user-defined.
Stacked Waveforms

The user can process multiple wavefiles in one go, creating a subplot for each.
Each subplot can be either an existing .wav file or a newly generated custom wave.
Interactive Drawing

Each wave can be given a custom “envelope” for positive and negative portions by click-and-drag on the subplot.
Keyboard shortcuts:
p: Preview the audio (applies to all subplots).
r: Reset envelope for the active subplot.
u: Undo the last stroke for the active subplot.
No Panning

The Matplotlib toolbar is disabled so there’s no accidental panning or zooming during drawing.
Color Pickers

final_drawing: Shows the user-drawn envelopes for each wave.
natural_lang: Displays a strictly sign-subdivided wave (no dashed segments) with negative color for < 0 and positive color for ≥ 0.
wave_comparison: Compares original vs. modified wave on each subplot, with the modified wave partially transparent so the original wave can peek through.
Consistent Aspect Ratio

The script forces set_aspect('auto') and uniform axis margins in reapply_colors(...), preventing wave compression even with multiple subplots. All images (final_drawing, natural_lang, wave_comparison) maintain a visually consistent axis scale.
CSV + Modified WAV Output

For each subplot, a .csv file is generated containing the positive and negative envelope data.
A modified .wav file (named future_<originalName>.wav) is created with the user’s drawn envelope applied.
Usage
Clone/Download this repository.
Install dependencies:
bash
Copy
Edit
pip install matplotlib numpy scipy sounddevice
Run the main script:
bash
Copy
Edit
python 🍘Natural_Language.py
Choose how many subplots (e.g. 3). For each subplot:
(1) Use an existing .wav file, or
(2) Generate a custom wave (with presets/manual)
Draw envelopes on each subplot:
Click and drag above zero for positive envelope, below zero for negative envelope.
Keyboard shortcuts:
p = Preview all subplots’ audio
r = Reset the active subplot’s envelope
u = Undo the last stroke on the active subplot
Color Pickers prompt for each output phase:
final_drawing → shows the user’s drawn envelope(s).
natural_lang → single continuous wave with negative vs. positive coloring.
wave_comparison → original wave vs. modified wave with partial transparency.
Outputs:
A new folder is created based on the first wave’s filename.
Inside that folder, you’ll find:
final_drawing.png
natural_lang.png
wave_comparison.png
envelope_*.csv (one per subplot)
*_future_<originalName>.wav (the modified audio per subplot)
