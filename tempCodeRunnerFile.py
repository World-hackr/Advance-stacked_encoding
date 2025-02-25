import os
import sys
import shutil
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import csv
import sounddevice as sd

class EnvelopePlot:
    def __init__(self, wav_file, ax, bg_color, pos_color, neg_color):
        self.wav_file = wav_file
        self.ax = ax
        self.bg_color = bg_color
        self.pos_color = pos_color
        self.neg_color = neg_color
        
        # Configure plot colors
        self.ax.set_facecolor(self.bg_color)
        self.fig = self.ax.figure
        self.fig.patch.set_facecolor(self.bg_color)
        
        # Load and normalize audio
        self.sample_rate, data = wavfile.read(wav_file)
        if data.ndim > 1:
            data = np.mean(data, axis=1)
        self.audio_data = data.astype(float) / np.max(np.abs(data))
        self.num_points = len(self.audio_data)
        self.max_amp = np.max(np.abs(self.audio_data))

        # Plot original waveform (faded)
        self.ax.plot(self.audio_data, color=self.pos_color, alpha=0.15, lw=1)

        # Initialize envelopes
        self.drawing_pos = np.zeros(self.num_points)
        self.drawing_neg = np.zeros(self.num_points)
        
        # Create envelope lines for drawing
        self.line_pos, = self.ax.plot([], [], color=self.pos_color, lw=2, label='Positive')
        self.line_neg, = self.ax.plot([], [], color=self.neg_color, lw=2, label='Negative')

        # Configure axis limits
        margin = 0.1 * self.max_amp
        self.ax.set_xlim(0, self.num_points)
        self.ax.set_ylim(-self.max_amp - margin, self.max_amp + margin)
        self.ax.tick_params(axis='both', colors='gray')
        for spine in self.ax.spines.values():
            spine.set_color('gray')
        
        # Add filename text
        base_name = os.path.basename(wav_file)
        self.ax.text(10, self.max_amp - margin, base_name, 
                     fontsize=9, color='gray', alpha=0.8, verticalalignment='top')

        # Drawing state
        self.is_drawing = False
        self.prev_idx = None
        self.last_state_pos = None
        self.last_state_neg = None
        self.background = None
        self.offset = 0.0

    def on_mouse_press(self, event):
        if event.inaxes != self.ax:
            return
        self.is_drawing = True
        if event.xdata is not None:
            self.prev_idx = int(event.xdata)
        self.last_state_pos = self.drawing_pos.copy()
        self.last_state_neg = self.drawing_neg.copy()
        self.update_drawing(event)

    def on_mouse_move(self, event):
        if self.is_drawing and event.inaxes == self.ax:
            self.update_drawing(event)

    def on_mouse_release(self, event):
        self.is_drawing = False

    def update_drawing(self, event):
        if event.xdata is None or event.ydata is None:
            return
        idx = int(event.xdata)
        if idx < 0 or idx >= self.num_points:
            return
        amp = event.ydata
        envelope = self.drawing_pos if amp >= 0 else self.drawing_neg
        if self.prev_idx is not None and idx != self.prev_idx:
            start_idx = self.prev_idx
            end_idx = idx
            if start_idx > end_idx:
                start_idx, end_idx = end_idx, start_idx
                start_val = amp
                end_val = envelope[self.prev_idx]
            else:
                start_val = envelope[self.prev_idx]
                end_val = amp
            envelope[start_idx:end_idx+1] = np.linspace(start_val, end_val, end_idx - start_idx + 1)
        else:
            envelope[idx] = amp
        self.prev_idx = idx
        self.line_pos.set_data(np.arange(self.num_points), self.drawing_pos + self.offset)
        self.line_neg.set_data(np.arange(self.num_points), self.drawing_neg + self.offset)
        if self.background is None:
            self.background = self.ax.figure.canvas.copy_from_bbox(self.ax.bbox)
        else:
            self.ax.figure.canvas.restore_region(self.background)
        self.ax.draw_artist(self.line_pos)
        self.ax.draw_artist(self.line_neg)
        self.ax.figure.canvas.blit(self.ax.bbox)

    def undo_envelope(self):
        if self.last_state_pos is not None and self.last_state_neg is not None:
            self.drawing_pos = self.last_state_pos.copy()
            self.drawing_neg = self.last_state_neg.copy()
            self.redraw_lines()

    def reset_envelope(self):
        self.drawing_pos[:] = 0
        self.drawing_neg[:] = 0
        self.redraw_lines()

    def redraw_lines(self):
        self.line_pos.set_data(np.arange(self.num_points), self.drawing_pos + self.offset)
        self.line_neg.set_data(np.arange(self.num_points), self.drawing_neg + self.offset)
        self.ax.figure.canvas.draw_idle()

    def preview_envelope(self):
        adjusted = np.copy(self.audio_data)
        for i in range(len(adjusted)):
            if adjusted[i] > 0:
                adjusted[i] = self.drawing_pos[i] + self.offset
            elif adjusted[i] < 0:
                adjusted[i] = self.drawing_neg[i] + self.offset
        audio_int16 = (adjusted * 32767).astype(np.int16)
        sd.play(audio_int16, self.sample_rate)
        sd.wait()

def get_modified_wave(envelope_plot):
    adjusted = np.copy(envelope_plot.audio_data)
    for i in range(len(adjusted)):
        if adjusted[i] > 0:
            adjusted[i] = envelope_plot.drawing_pos[i] + envelope_plot.offset
        elif adjusted[i] < 0:
            adjusted[i] = envelope_plot.drawing_neg[i] + envelope_plot.offset
    return adjusted

def show_color_options(options, title):
    print(f"\n{title}")
    print(f"{'No.':<5} {'Name':<20} {'Hex Code':<10}")
    for idx, (name, hex_code) in enumerate(options.items(), 1):
        print(f"{idx:<5} {name:<20} {hex_code:<10}")
    return list(options.values())

def choose_color(options, prompt):
    while True:
        try:
            choice = int(input(prompt))
            if 1 <= choice <= len(options):
                return options[choice-1]
            print(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("Invalid input. Please enter a number.")

def configure_colors():
    print("\n=== Color Configuration ===")
    use_custom = input("Use custom colors? (y/n): ").lower() == 'y'
    if not use_custom:
        return {'background': '#000000', 'positive': '#00FF00', 'negative': '#00FF00'}
    background_options = {
        "Black": "#000000",
        "Electric Blue": "#0000FF",
        "Neon Purple": "#BF00FF",
        "Bright Cyan": "#00FFFF",
        "Vibrant Magenta": "#FF00FF",
        "Neon Green": "#39FF14",
        "Hot Pink": "#FF69B4",
        "Neon Orange": "#FF4500",
        "Bright Yellow": "#FFFF00",
        "Electric Lime": "#CCFF00",
        "Vivid Red": "#FF0000",
        "Deep Sky Blue": "#00BFFF",
        "Vivid Violet": "#9F00FF",
        "Fluorescent Pink": "#FF1493",
        "Laser Lemon": "#FFFF66",
        "Screamin' Green": "#66FF66",
        "Ultra Red": "#FF2400",
        "Radical Red": "#FF355E",
        "Vivid Orange": "#FFA500",
        "Electric Indigo": "#6F00FF"
    }
    positive_options = {
        "Vibrant Green": "#00FF00",
        "Neon Green": "#39FF14",
        "Electric Lime": "#CCFF00",
        "Bright Yellow": "#FFFF00",
        "Vivid Cyan": "#00FFFF",
        "Electric Blue": "#0000FF",
        "Neon Purple": "#BF00FF",
        "Hot Pink": "#FF69B4",
        "Neon Orange": "#FF4500",
        "Vivid Red": "#FF0000",
        "Screamin' Green": "#66FF66",
        "Laser Lemon": "#FFFF66",
        "Fluorescent Magenta": "#FF00FF",
        "Hyper Blue": "#1F51FF",
        "Electric Teal": "#00FFEF",
        "Vivid Turquoise": "#00CED1",
        "Radical Red": "#FF355E",
        "Ultra Violet": "#7F00FF",
        "Neon Coral": "#FF6EC7",
        "Luminous Lime": "#BFFF00"
    }
    negative_options = {
        "Vibrant Green": "#00FF00",
        "Neon Orange": "#FF4500",
        "Hot Pink": "#FF69B4",
        "Vivid Cyan": "#00FFFF",
        "Electric Blue": "#0000FF",
        "Neon Purple": "#BF00FF",
        "Bright Yellow": "#FFFF00",
        "Electric Lime": "#CCFF00",
        "Vivid Red": "#FF0000",
        "Deep Pink": "#FF1493",
        "Screamin' Green": "#66FF66",
        "Laser Lemon": "#FFFF66",
        "Fluorescent Magenta": "#FF00FF",
        "Hyper Blue": "#1F51FF",
        "Electric Teal": "#00FFEF",
        "Vivid Turquoise": "#00CED1",
        "Radical Red": "#FF355E",
        "Ultra Violet": "#7F00FF",
        "Neon Coral": "#FF6EC7",
        "Luminous Lime": "#BFFF00"
    }
    bg_colors = show_color_options(background_options, "Background Colors:")
    bg_choice = choose_color(bg_colors, "Select background color (enter the number): ")
    pos_colors = show_color_options(positive_options, "\nPositive Envelope Colors:")
    pos_choice = choose_color(pos_colors, "Select positive color (enter the number): ")
    neg_colors = show_color_options(negative_options, "\nNegative Envelope Colors:")
    neg_choice = choose_color(neg_colors, "Select negative color (enter the number): ")
    return {'background': bg_choice, 'positive': pos_choice, 'negative': neg_choice}

def create_final_drawing_png(fig, folder):
    output_path = os.path.join(folder, "final_drawing.png")
    fig.savefig(output_path)
    print(f"Final drawing saved to {output_path}")

def save_csv_and_wav(envelope_plots, folder):
    for idx, ep in enumerate(envelope_plots, 1):
        # Save envelope CSV data
        csv_path = os.path.join(folder, f"envelope_{idx}.csv")
        with open(csv_path, "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["Index", "Positive", "Negative"])
            for i in range(ep.num_points):
                csvwriter.writerow([i, ep.drawing_pos[i], ep.drawing_neg[i]])
        print(f"Envelope data saved to {csv_path}")
        # Save modified wav file with "future" prefix
        adjusted = get_modified_wave(ep)
        original_name = os.path.basename(ep.wav_file)
        wav_path = os.path.join(folder, f"{idx}_future_{original_name}")
        wavfile.write(wav_path, ep.sample_rate, (adjusted * 32767).astype(np.int16))
        print(f"Modified audio saved to {wav_path}")

def create_comparison_png(envelope_plots, folder):
    num_plots = len(envelope_plots)
    # Create figure with same overall proportions as final_drawing.png using constrained_layout.
    fig, axes = plt.subplots(num_plots, 1, figsize=(10, 3 * num_plots), constrained_layout=True)
    if num_plots == 1:
        axes = [axes]
    for idx, ep in enumerate(envelope_plots):
        ax = axes[idx]
        ax.plot(ep.audio_data, label="Original", color="blue", alpha=0.5)
        modified = get_modified_wave(ep)
        ax.plot(modified, label="Modified", color="red", alpha=0.7)
        ax.set_xlim(0, ep.num_points)
        margin = 0.1 * ep.max_amp
        ax.set_ylim(-ep.max_amp - margin, ep.max_amp + margin)
        ax.set_facecolor(ep.bg_color)
        ax.set_title(f"Comparison Plot {idx+1}")
        ax.legend()
    output_path = os.path.join(folder, "comparison.png")
    fig.savefig(output_path)
    print(f"Comparison plot saved to {output_path}")
    plt.close(fig)

def create_stacked_modified_png(envelope_plots, folder):
    num_plots = len(envelope_plots)
    # Create figure with same overall proportions as final_drawing.png using constrained_layout.
    fig, axes = plt.subplots(num_plots, 1, figsize=(10, 3 * num_plots), constrained_layout=True)
    if num_plots == 1:
        axes = [axes]
    for idx, ep in enumerate(envelope_plots):
        ax = axes[idx]
        modified = get_modified_wave(ep)
        ax.plot(modified, color="lime", alpha=0.8)
        ax.set_title(f"Modified Waveform {idx+1}")
        ax.set_xlim(0, ep.num_points)
        margin = 0.1 * ep.max_amp
        ax.set_ylim(-ep.max_amp - margin, ep.max_amp + margin)
        ax.tick_params(axis='both', colors='gray')
        for spine in ax.spines.values():
            spine.set_color('gray')
        ax.set_facecolor(ep.bg_color)
    output_path = os.path.join(folder, "stacked_modified.png")
    fig.savefig(output_path)
    print(f"Stacked modified waveforms saved to {output_path}")
    plt.close(fig)

def process_multi_division():
    colors = configure_colors()
    try:
        num_div = int(input("\nEnter number of divisions (subplots): "))
    except ValueError:
        num_div = 1
    wav_files = []
    for i in range(num_div):
        path = input(f"Enter path to .wav file for division {i+1}: ")
        if not os.path.exists(path):
            print("File not found!")
            sys.exit(1)
        wav_files.append(path)
    first_base = os.path.splitext(os.path.basename(wav_files[0]))[0]
    new_folder = os.path.join(os.getcwd(), first_base)
    os.makedirs(new_folder, exist_ok=True)
    print(f"Created folder: {new_folder}")
    # Copy original .wav files to new folder
    for wf in wav_files:
        shutil.copy(wf, new_folder)
        print(f"Copied {wf} to {new_folder}")
        
    # Create the main drawing figure with stacked subplots (final_drawing.png)
    fig, axes = plt.subplots(num_div, 1, figsize=(10, 3 * num_div), facecolor=colors['background'])
    fig.subplots_adjust(hspace=0)
    if num_div == 1:
        axes = [axes]
    # Disconnect default key press handler to avoid panning
    if hasattr(fig.canvas.manager, 'key_press_handler_id'):
        fig.canvas.mpl_disconnect(fig.canvas.manager.key_press_handler_id)
    envelope_plots = []
    for i, wf in enumerate(wav_files):
        ep = EnvelopePlot(wf, axes[i],
                          bg_color=colors['background'],
                          pos_color=colors['positive'],
                          neg_color=colors['negative'])
        envelope_plots.append(ep)
        
    # Attach event handlers for interactive drawing
    def on_press(event):
        for ep in envelope_plots:
            if event.inaxes == ep.ax:
                ep.on_mouse_press(event)
                break
    def on_move(event):
        for ep in envelope_plots:
            if event.inaxes == ep.ax:
                ep.on_mouse_move(event)
                break
    def on_release(event):
        for ep in envelope_plots:
            if event.inaxes == ep.ax:
                ep.on_mouse_release(event)
                break
    def on_key(event):
        # 'p' previews without triggering panning; drawing remains active.
        if event.key.lower() == 'p':
            print("Previewing all subplots...")
            for epp in envelope_plots:
                epp.preview_envelope()
        else:
            for ep in envelope_plots:
                if event.inaxes == ep.ax:
                    if event.key.lower() == 'r':
                        ep.reset_envelope()
                    elif event.key.lower() == 'u':
                        ep.undo_envelope()
                    break

    cid_press = fig.canvas.mpl_connect('button_press_event', on_press)
    cid_move = fig.canvas.mpl_connect('motion_notify_event', on_move)
    cid_release = fig.canvas.mpl_connect('button_release_event', on_release)
    cid_key = fig.canvas.mpl_connect('key_press_event', on_key)
    
    plt.show(block=False)
    print("Drawing phase active. Press Enter when done.")
    input()
    fig.canvas.mpl_disconnect(cid_press)
    fig.canvas.mpl_disconnect(cid_move)
    fig.canvas.mpl_disconnect(cid_release)
    fig.canvas.mpl_disconnect(cid_key)
    
    # Save outputs
    create_final_drawing_png(fig, new_folder)
    save_csv_and_wav(envelope_plots, new_folder)
    create_comparison_png(envelope_plots, new_folder)
    create_stacked_modified_png(envelope_plots, new_folder)
    plt.close()

if __name__ == '__main__':
    process_multi_division()
