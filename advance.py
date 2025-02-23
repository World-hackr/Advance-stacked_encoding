import os
import sys
import shutil
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import find_peaks
import csv

class EnvelopePlot:
    def __init__(self, wav_file, ax):
        """
        Loads the .wav file (converting to mono and normalizing) and uses the number of samples 
        in the file as the x-axis resolution. Initializes arrays for drawing a custom envelope.
        A text annotation inside the subplot shows the file’s name.
        The attribute self.offset is used to reposition the envelope vertically.
        """
        self.wav_file = wav_file
        self.ax = ax
        self.sample_rate, data = wavfile.read(wav_file)
        if data.ndim > 1:
            data = np.mean(data, axis=1)
        data = data.astype(float)
        data = data / np.max(np.abs(data))
        self.num_points = len(data)  # x-axis resolution from file
        self.audio_data = data
        self.max_amp = np.max(np.abs(data))
        # Arrays for custom envelope drawing.
        self.drawing_pos = np.zeros(self.num_points)
        self.drawing_neg = np.zeros(self.num_points)
        # Vertical offset for repositioning; initially zero.
        self.offset = 0  
        # Create line objects for positive (blue) and negative (red) envelope drawings.
        self.line_pos, = ax.plot([], [], color='blue', lw=2, label='Positive Envelope')
        self.line_neg, = ax.plot([], [], color='red', lw=2, label='Negative Envelope')
        self.is_drawing = False
        self.prev_idx = None
        # We'll try to use blitting for faster updates on this axes.
        self.background = None  

        # Set axis limits based on the file’s data.
        ax.set_xlim(0, self.num_points)
        margin = 0.1 * self.max_amp
        ax.set_ylim(-self.max_amp - margin, self.max_amp + margin)
        # Place the file name inside the plot.
        self.label = ax.text(10, self.max_amp - margin, os.path.basename(wav_file),
                             fontsize=10, color='black', verticalalignment='top')
        ax.legend(loc='upper right')

    # --- Drawing Handlers ---
    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        self.is_drawing = True
        self.prev_idx = int(event.xdata)
        # Reset background so that we update from fresh
        self.background = None
        self.update_drawing(event)

    def on_motion(self, event):
        if self.is_drawing and event.inaxes == self.ax:
            self.update_drawing(event)

    def on_release(self, event):
        self.is_drawing = False
        self.prev_idx = None

    def update_drawing(self, event):
        idx = int(event.xdata)
        if idx < 0 or idx >= self.num_points:
            return
        # If event.ydata is nonnegative, update the positive envelope;
        # if negative, update the negative envelope.
        if event.ydata >= 0:
            val = event.ydata
            if self.prev_idx is not None and idx > self.prev_idx:
                self.drawing_pos[self.prev_idx:idx+1] = np.linspace(
                    self.drawing_pos[self.prev_idx], val, idx - self.prev_idx + 1)
            else:
                self.drawing_pos[idx] = val
            self.line_pos.set_data(np.arange(self.num_points), self.drawing_pos + self.offset)
        else:
            val = event.ydata
            if self.prev_idx is not None and idx > self.prev_idx:
                self.drawing_neg[self.prev_idx:idx+1] = np.linspace(
                    self.drawing_neg[self.prev_idx], val, idx - self.prev_idx + 1)
            else:
                self.drawing_neg[idx] = val
            self.line_neg.set_data(np.arange(self.num_points), self.drawing_neg + self.offset)
        self.prev_idx = idx

        # Try to update only the active axes via blitting.
        try:
            if self.background is None:
                self.background = self.ax.figure.canvas.copy_from_bbox(self.ax.bbox)
            else:
                self.ax.figure.canvas.restore_region(self.background)
            self.ax.draw_artist(self.line_pos)
            self.ax.draw_artist(self.line_neg)
            self.ax.figure.canvas.blit(self.ax.bbox)
        except Exception as e:
            # If blitting fails, do a full redraw.
            self.ax.figure.canvas.draw_idle()

    def reposition_update(self):
        """Update envelope lines using the current offset."""
        x = np.arange(self.num_points)
        self.line_pos.set_data(x, self.drawing_pos + self.offset)
        self.line_neg.set_data(x, self.drawing_neg + self.offset)
        self.ax.figure.canvas.draw_idle()

def process_peaks_and_modify_audio(ep):
    """
    Detects peaks (both positive and negative) in the original audio.
    For each detected peak, computes the factor needed to change the original
    peak value to the drawn outline value (using drawing_pos for positive peaks
    and drawing_neg for negative ones). Then, the factors are linearly interpolated
    over the entire audio signal and applied to produce a modified audio.
    
    Returns:
      modified_audio: the new audio signal after applying the scaling
      peak_data: a list of tuples (peak_index, original_peak, drawn_peak, factor)
    """
    # Detect positive and negative peaks in the original audio.
    pos_idx, _ = find_peaks(ep.audio_data)
    neg_idx, _ = find_peaks(-ep.audio_data)
    peak_indices = np.sort(np.concatenate((pos_idx, neg_idx)))
    
    peak_data = []
    x_peaks = []
    factors = []
    for idx in peak_indices:
        orig_val = ep.audio_data[idx]
        if orig_val >= 0:
            drawn_val = ep.drawing_pos[idx] + ep.offset
        else:
            drawn_val = ep.drawing_neg[idx] + ep.offset
        # Avoid division by zero.
        factor = drawn_val / orig_val if orig_val != 0 else 1.0
        peak_data.append((idx, orig_val, drawn_val, factor))
        x_peaks.append(idx)
        factors.append(factor)
    N = ep.num_points
    all_indices = np.arange(N)
    # Interpolate the scaling factor for every sample.
    interpolated_factors = np.interp(all_indices, x_peaks, factors)
    # Apply the factor to the original audio.
    modified_audio = ep.audio_data * interpolated_factors
    modified_audio = np.clip(modified_audio, -1, 1)
    return modified_audio, peak_data

def save_csv_and_wav(envelope_plots, new_folder):
    """
    For each EnvelopePlot, process the peaks and modify the audio signal so that
    the peaks in the original file match the drawn envelope. Saves the peak data 
    (index, original peak, drawn peak, scaling factor) to a CSV file and writes 
    the modified audio as a new WAV file (both files have names prefixed with 'future_')
    into new_folder.
    """
    for ep in envelope_plots:
        modified_audio, peak_data = process_peaks_and_modify_audio(ep)
        
        # Create CSV filename: future_<original_basename>.csv in new_folder
        base_name = os.path.splitext(os.path.basename(ep.wav_file))[0]
        csv_filename = os.path.join(new_folder, f"future_{base_name}.csv")
        with open(csv_filename, "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["peak_index", "original_peak", "drawn_peak", "factor"])
            for data in peak_data:
                writer.writerow(data)
        print(f"Saved peak data as {csv_filename}")
        
        # Create WAV filename: future_<original_filename> in new_folder
        wav_filename = os.path.join(new_folder, f"future_{os.path.basename(ep.wav_file)}")
        wavfile.write(wav_filename, ep.sample_rate, (modified_audio * 32767).astype(np.int16))
        print(f"Saved modified audio as {wav_filename}")

def process_multi_division():
    try:
        num_div = int(input("Enter number of divisions (subplots): "))
    except ValueError:
        print("Invalid input; defaulting to 1 division.")
        num_div = 1

    wav_files = []
    for i in range(num_div):
        wav_file = input(f"Enter path to .wav file for division {i+1}: ")
        if not os.path.exists(wav_file):
            print("File not found. Exiting.")
            sys.exit(1)
        wav_files.append(wav_file)

    # Create new folder based on the first input file (remove extension)
    first_base = os.path.splitext(os.path.basename(wav_files[0]))[0]
    new_folder = os.path.join(os.getcwd(), first_base)
    os.makedirs(new_folder, exist_ok=True)
    print(f"Created folder: {new_folder}")

    # Copy all input WAV files into the new folder.
    for wav_file in wav_files:
        shutil.copy(wav_file, new_folder)
        print(f"Copied {wav_file} to {new_folder}")

    # Create a figure with one subplot per division, with no vertical gaps.
    fig, axes = plt.subplots(num_div, 1, figsize=(10, 3*num_div), sharex=False, sharey=False)
    if num_div == 1:
        axes = [axes]
    fig.subplots_adjust(hspace=0)

    envelope_plots = []
    for i, wav_file in enumerate(wav_files):
        ep = EnvelopePlot(wav_file, axes[i])
        envelope_plots.append(ep)

    # Global event handlers for drawing phase:
    def drawing_on_press(event):
        if event.inaxes is None:
            return
        for ep in envelope_plots:
            if event.inaxes == ep.ax:
                ep.on_click(event)
                break

    def drawing_on_motion(event):
        if event.inaxes is None:
            return
        for ep in envelope_plots:
            if event.inaxes == ep.ax:
                ep.on_motion(event)
                break

    def drawing_on_release(event):
        if event.inaxes is None:
            return
        for ep in envelope_plots:
            if event.inaxes == ep.ax:
                ep.on_release(event)
                break

    draw_press_id = fig.canvas.mpl_connect('button_press_event', drawing_on_press)
    draw_motion_id = fig.canvas.mpl_connect('motion_notify_event', drawing_on_motion)
    draw_release_id = fig.canvas.mpl_connect('button_release_event', drawing_on_release)

    plt.show(block=False)
    print("Drawing phase active. Draw your envelopes in each subplot.")
    print("When finished drawing, press Enter in the terminal (do NOT close the window).")
    input()  # Drawing phase complete

    # Immediately create output files from the current drawing.
    output_png = os.path.join(new_folder, "final_drawing.png")
    fig.savefig(output_png)
    print("Saved final drawing as", output_png)
    save_csv_and_wav(envelope_plots, new_folder)
    
    # Now continue with reposition phase (this phase affects only on-screen display).
    print("Reposition phase active.")
    print("Now, click anywhere in a subplot and drag vertically to move the entire envelope.")
    print("Press Enter in the terminal when done repositioning.")
    
    # Disconnect drawing phase event handlers.
    fig.canvas.mpl_disconnect(draw_press_id)
    fig.canvas.mpl_disconnect(draw_motion_id)
    fig.canvas.mpl_disconnect(draw_release_id)

    active_repos = {"ep": None, "start_y": None, "initial_offset": None}

    def repos_on_press(event):
        if event.inaxes is None:
            return
        for ep in envelope_plots:
            if event.inaxes == ep.ax:
                active_repos["ep"] = ep
                active_repos["start_y"] = event.ydata
                active_repos["initial_offset"] = ep.offset
                break

    def repos_on_motion(event):
        if active_repos["ep"] is None or event.inaxes is None:
            return
        dy = event.ydata - active_repos["start_y"]
        new_offset = active_repos["initial_offset"] + dy
        active_repos["ep"].offset = new_offset
        active_repos["ep"].reposition_update()
        active_repos["ep"].ax.figure.canvas.draw_idle()

    def repos_on_release(event):
        active_repos["ep"] = None
        active_repos["start_y"] = None
        active_repos["initial_offset"] = None

    repos_press_id = fig.canvas.mpl_connect('button_press_event', repos_on_press)
    repos_motion_id = fig.canvas.mpl_connect('motion_notify_event', repos_on_motion)
    repos_release_id = fig.canvas.mpl_connect('button_release_event', repos_on_release)

    input("When done repositioning, press Enter in the terminal.")
    fig.canvas.mpl_disconnect(repos_press_id)
    fig.canvas.mpl_disconnect(repos_motion_id)
    fig.canvas.mpl_disconnect(repos_release_id)

    plt.show(block=True)

if __name__ == '__main__':
    process_multi_division()
