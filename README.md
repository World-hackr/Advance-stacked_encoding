Advanced Natural Language Wave Processing Tool
Table of Contents
Overview
Features
Installation and Setup
Usage
Wave Generation / Import
Color Customization
Vertical Spacing Adjustment
Interactive Envelope Drawing
Export & Visualization
How It Works
Layman Explanation
Technical Explanation
Sample Commit Message
Overview
This tool allows you to create or import sound files and interactively modify their waveforms. You can generate a custom waveform (or load an existing one), draw envelopes on the waveform, adjust the layout of multiple wave displays, and export the results in various formats including CSV, modified WAV files, and images. The project is designed to provide both a user-friendly interface for non-technical users and detailed control for technical users.

Features
Custom Wave Generation:
Generate waveforms using presets (sine, square, triangle, sawtooth) or via manual entry (specify frequency, samples per wavelength, and periods).

Existing Wave Import:
Load an existing WAV file for processing.

Multi-Division Stacked Wave Processing:
Stack multiple waveforms vertically for simultaneous editing.

Color Customization:
Customize background, positive envelope, and negative envelope colors through an interactive color picker.

Optional Vertical Spacing Adjustment:
Adjust the vertical spacing of the stacked subplots using inset sliders. This adjustment phase repositions subplots (without gaps) by modifying only the lower boundary of each subplot while keeping the top fixed.

Interactive Envelope Drawing:
Draw envelopes on each waveform interactively with your mouse (with undo and reset options) and preview the modified audio.

Export Options:
Export your work as CSV data, modified WAV files, and images including:

Final Drawing image.
Natural Language visualization image (a continuous wave using strict sign subdivision).
Wave Comparison image (overlaying the original and modified waveforms).
Installation and Setup
Prerequisites:

Python (version 3.x recommended)
Required Python packages: matplotlib, numpy, scipy, sounddevice
Installation:

Install the required packages using pip:
bash
Copy
Edit
pip install matplotlib numpy scipy sounddevice
Download the Code:

Clone or download the repository containing the source code.
Usage
Wave Generation / Import
When you run the tool, you will be prompted to either generate a custom wave (choose from presets or manually enter parameters) or import an existing WAV file.

Color Customization
You will then choose custom colors for the drawing canvas, as well as for the positive and negative envelopes, through an interactive color picker.

Vertical Spacing Adjustment
After color selection, the tool offers an optional vertical spacing adjustment phase:

If you choose "y", inset sliders will appear in each subplot.
Use these sliders to adjust each subplot’s lower boundary while the top remains fixed.
The subplots will automatically reallocate the remaining space, ensuring there are no gaps.
Press Enter to finish the adjustment phase; the sliders will then be removed.
Interactive Envelope Drawing
In the drawing phase, your waveform is displayed along with a faint reference of the original file. You can draw envelopes directly on the waveform:

p – Preview the modified audio.
r – Reset the envelope for the subplot under your mouse.
u – Undo the last stroke for the subplot under your mouse.
Export & Visualization
After the drawing phase:

The tool exports CSV files containing the envelope data.
Modified WAV files are generated.
Additional images are created:
Final Drawing: Shows the final envelope.
Natural Language Visualization: A continuous line visualization using strict sign subdivision.
Wave Comparison: An overlay of the original and modified waveforms with transparency.
How It Works
Layman Explanation
Imagine you have a sound wave picture like the ones seen in music editing software. This tool lets you create a new sound wave or load one that already exists. Then, you can “draw” over the wave with your mouse—like drawing on paper—to change its shape. You can also adjust how the waves are arranged on the screen (for example, how much space each one takes). Once you’re done, the tool saves your work as new sound files and images that show your changes. It’s a way to customize your own sound picture!

Technical Explanation
Wave Generation/Import:
The tool either generates a waveform based on preset or user-defined parameters or loads an existing WAV file and normalizes it.

Color Customization:
Users select colors for the canvas and envelope lines using an interactive color picker that prints ANSI swatches to the console.

Vertical Spacing Adjustment:
An optional phase allows users to reallocate the vertical space between subplots using inset sliders. Each slider controls the lower boundary of its subplot while keeping its top fixed. Subsequent subplots shift accordingly to maintain a continuous, gapless layout.

Interactive Envelope Drawing:
The EnvelopePlot class handles interactive envelope drawing. It captures mouse events (press, move, release) to draw and update envelope lines in real time with minimal redraw overhead (using a blit approach).

Export Routines:
After drawing, the tool exports envelope data to CSV files, generates modified WAV files (applying the drawn envelope), and produces images (final drawing, natural language visualization, and wave comparison) by reapplying user-defined color schemes.