import os
import sys
import shutil
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import csv
import sounddevice as sd

##############################################################################
# COLOR-PICKING FUNCTIONS
##############################################################################

def show_color_options(options, title):
    """
    Prints a table of color options with a small ANSI color swatch (if supported).
    """
    print(f"\n{title}")
    print(f"{'No.':<5} {'Name':<20} {'Hex Code':<10}  Sample")
    for idx, (name, hex_code) in enumerate(options.items(), 1):
        if hex_code.startswith('#') and len(hex_code) == 7:
            try:
                r = int(hex_code[1:3], 16)
                g = int(hex_code[3:5], 16)
                b = int(hex_code[5:7], 16)
            except ValueError:
                r, g, b = (255, 255, 255)
        else:
            r, g, b = (255, 255, 255)
        ansi_color = f"\033[38;2;{r};{g};{b}m"
        ansi_reset = "\033[0m"
        print(f"{idx:<5} {name:<20} {hex_code:<10}  {ansi_color}██{ansi_reset}")
    return list(options.values())

def choose_color(options, prompt):
    while True:
        try:
            choice = int(input(prompt))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            print(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("Invalid input. Please enter a number.")

def run_color_picker(default_bg, default_pos, default_neg):
    """
    Asks user if they want custom colors. If not, returns the defaults.
    If yes, shows color menus for background, positive, negative lines.
    """
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

    use_custom = input("Use custom colors? (y/n): ").lower() == 'y'
    if not use_custom:
        return default_bg, default_pos, default_neg

    # Show color menus
    bg_vals  = show_color_options(background_options, "Background Colors:")
    bg_pick  = choose_color(bg_vals,  "Select background color (enter number): ")

    pos_vals = show_color_options(positive_options,  "\nPositive Envelope Colors:")
    pos_pick = choose_color(pos_vals, "Select positive color (enter number): ")

    neg_vals = show_color_options(negative_options,  "\nNegative Envelope Colors:")
    neg_pick = choose_color(neg_vals, "Select negative color (enter number): ")

    return bg_pick, pos_pick, neg_pick

##############################################################################
# ENVELOPEPLOT + MAIN LOGIC
##############################################################################

class EnvelopePlot:
    def __init__(self, wav_file, ax, bg_color, pos_color, neg_color):
        self.wav_file = wav_file
        self.ax = ax

        # We'll store the "canvas" colors as defaults
        self.canvas_bg_color = bg_color
        self.canvas_pos_color = pos_color
        self.canvas_neg_color = neg_color

        # Actually set the background
        self.ax.set_facecolor(self.canvas_bg_color)
        self.fig = self.ax.figure
        self.fig.patch.set_facecolor(self.canvas_bg_color)

        # Load & normalize
        self.sample_rate, data = wavfile.read(wav_file)
        if data.ndim > 1:
            data = np.mean(data, axis=1)
        self.audio_data = data.astype(float) / np.max(np.abs(data))
        self.num_points = len(self.audio_data)
        self.max_amp = np.max(np.abs(self.audio_data))

        # Faint original wave
        self.faint_line, = self.ax.plot(
            self.audio_data,
            color=self.canvas_pos_color,
            alpha=0.15,
            lw=1
        )

        # Envelope arrays
        self.drawing_pos = np.zeros(self.num_points)
        self.drawing_neg = np.zeros(self.num_points)

        # Envelope lines
        self.line_pos, = self.ax.plot([], [],
                                      color=self.canvas_pos_color,
                                      lw=2, label='Positive')
        self.line_neg, = self.ax.plot([], [],
                                      color=self.canvas_neg_color,
                                      lw=2, label='Negative')

        # We'll add final wave lines or wave_comparison lines later
        self.final_line = None
        self.comparison_line_orig = None
        self.comparison_line_mod  = None

        # Configure axis
        margin = 0.1 * self.max_amp
        self.ax.set_xlim(0, self.num_points)
        self.ax.set_ylim(-self.max_amp - margin, self.max_amp + margin)
        self.ax.tick_params(axis='both', colors='gray')
        for spine in self.ax.spines.values():
            spine.set_color('gray')

        # Show filename
        base_name = os.path.basename(wav_file)
        self.ax.text(10, self.max_amp - margin,
                     base_name, fontsize=9, color='gray', alpha=0.8,
                     verticalalignment='top')

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
            envelope[start_idx:end_idx+1] = np.linspace(
                start_val, end_val,
                end_idx - start_idx + 1
            )
        else:
            envelope[idx] = amp
        self.prev_idx = idx

        self.line_pos.set_data(np.arange(self.num_points),
                               self.drawing_pos + self.offset)
        self.line_neg.set_data(np.arange(self.num_points),
                               self.drawing_neg + self.offset)

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
        self.line_pos.set_data(np.arange(self.num_points),
                               self.drawing_pos + self.offset)
        self.line_neg.set_data(np.arange(self.num_points),
                               self.drawing_neg + self.offset)
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

    def reapply_colors(self, bg_color, pos_color, neg_color,
                       faint_alpha=0.15, final_wave_color="#00FF00",
                       final_wave_alpha=0.4, orig_alpha=0.6, mod_alpha=0.8):
        """
        Re-color this subplot's background, faint_line, line_pos, line_neg,
        final_line, comparison lines, etc.
        """
        self.ax.set_facecolor(bg_color)
        self.fig.patch.set_facecolor(bg_color)

        if self.faint_line is not None:
            self.faint_line.set_color(pos_color)
            self.faint_line.set_alpha(faint_alpha)

        self.line_pos.set_color(pos_color)
        self.line_neg.set_color(neg_color)

        if self.final_line is not None:
            # "modified wave" line
            self.final_line.set_color(final_wave_color)
            self.final_line.set_alpha(final_wave_alpha)

        if self.comparison_line_orig is not None:
            # Original wave in negative color, alpha=0.6
            self.comparison_line_orig.set_color(neg_color)
            self.comparison_line_orig.set_alpha(orig_alpha)

        if self.comparison_line_mod is not None:
            # Modified wave in positive color, alpha=0.8
            self.comparison_line_mod.set_color(pos_color)
            self.comparison_line_mod.set_alpha(mod_alpha)

        self.ax.figure.canvas.draw_idle()

def get_modified_wave(ep):
    adjusted = np.copy(ep.audio_data)
    for i in range(len(adjusted)):
        if adjusted[i] > 0:
            adjusted[i] = ep.drawing_pos[i] + ep.offset
        elif adjusted[i] < 0:
            adjusted[i] = ep.drawing_neg[i] + ep.offset
    return adjusted

##############################################################################
# MAIN
##############################################################################

def process_multi_division():
    # 1) Insert .wav files first
    print("\n=== Insert your .wav files ===")
    try:
        num_div = int(input("Enter number of divisions (subplots): "))
    except ValueError:
        num_div = 1

    wav_files = []
    for i in range(num_div):
        wf = input(f"Enter path to .wav file for division {i+1}: ")
        if not os.path.exists(wf):
            print(f"File not found: {wf}")
            sys.exit(1)
        wav_files.append(wf)

    # Create new folder named after first file
    first_base = os.path.splitext(os.path.basename(wav_files[0]))[0]
    new_folder = os.path.join(os.getcwd(), first_base)
    os.makedirs(new_folder, exist_ok=True)
    print(f"Created folder: {new_folder}")

    # Copy .wav files to new folder
    for wf in wav_files:
        shutil.copy(wf, new_folder)
        print(f"Copied {wf} to {new_folder}")

    # 2) Right after inserting files, color picker for the "drawing canvas"
    print("\n=== Drawing Canvas Color Picker ===")
    # Default canvas colors
    default_bg  = "#000000"
    default_pos = "#00FF00"
    default_neg = "#00FF00"
    draw_bg, draw_pos, draw_neg = run_color_picker(default_bg, default_pos, default_neg)

    # 3) Create figure for interactive drawing with the chosen canvas colors
    fig, axes = plt.subplots(num_div, 1,
                             figsize=(16, 3 * num_div),
                             facecolor=draw_bg)
    fig.subplots_adjust(left=0.06, right=0.98, top=0.95, bottom=0.05, hspace=0)

    if num_div == 1:
        axes = [axes]

    # Disconnect default 'p' => panning
    if hasattr(fig.canvas.manager, 'key_press_handler_id'):
        fig.canvas.mpl_disconnect(fig.canvas.manager.key_press_handler_id)

    # 4) Create EnvelopePlots with the chosen canvas colors
    envelope_plots = []
    for i, wf in enumerate(wav_files):
        ep = EnvelopePlot(wf, axes[i],
                          bg_color=draw_bg,
                          pos_color=draw_pos,
                          neg_color=draw_neg)
        envelope_plots.append(ep)
        axes[i].set_aspect('auto')
        if i == 0:
            # top subplot => legend + instructions
            leg = axes[i].legend(loc='upper right')
            leg.get_frame().set_alpha(0.5)
            axes[i].text(
                0.65, 0.90,
                "p=preview\nr=reset\nu=undo",
                transform=axes[i].transAxes,
                fontsize=8,
                color='white',
                ha='left',
                va='top',
                bbox=dict(boxstyle="round", fc="black", ec="none", alpha=0.5)
            )

    # 5) Interactive drawing
    print("\nIn the drawing canvas:\n"
          " - Press 'p' to preview.\n"
          " - Press 'r' to reset.\n"
          " - Press 'u' to undo.\n")

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
        if not event.key:
            return
        k = event.key.lower()
        if k == 'p':
            print("Previewing all subplots...")
            for epp in envelope_plots:
                epp.preview_envelope()
        elif k in ['r','u']:
            for ep in envelope_plots:
                if event.inaxes == ep.ax:
                    if k == 'r':
                        ep.reset_envelope()
                        print("Envelope reset.")
                    elif k == 'u':
                        ep.undo_envelope()
                        print("Undo last stroke.")
                    break

    cid_press   = fig.canvas.mpl_connect('button_press_event', on_press)
    cid_move    = fig.canvas.mpl_connect('motion_notify_event', on_move)
    cid_release = fig.canvas.mpl_connect('button_release_event', on_release)
    cid_key     = fig.canvas.mpl_connect('key_press_event', on_key)

    plt.show(block=False)
    print("Drawing phase active. Press Enter when done.")
    input()

    fig.canvas.mpl_disconnect(cid_press)
    fig.canvas.mpl_disconnect(cid_move)
    fig.canvas.mpl_disconnect(cid_release)
    fig.canvas.mpl_disconnect(cid_key)

    # 6) final_drawing color pick
    print("\n=== final_drawing Color Picker ===")
    f_bg, f_pos, f_neg = run_color_picker(draw_bg, draw_pos, draw_neg)
    # Reapply to each subplot
    for ep in envelope_plots:
        ep.reapply_colors(f_bg, f_pos, f_neg)

    # Save final_drawing.png
    final_path = os.path.join(new_folder, "final_drawing.png")
    fig.savefig(final_path)
    print(f"final_drawing.png saved to {final_path}")

    # 7) Save CSV & WAV
    from scipy.io import wavfile
    for idx, ep in enumerate(envelope_plots, 1):
        csv_path = os.path.join(new_folder, f"envelope_{idx}.csv")
        with open(csv_path, "w", newline="") as f_:
            writer = csv.writer(f_)
            writer.writerow(["Index", "Positive", "Negative"])
            for i in range(ep.num_points):
                writer.writerow([i, ep.drawing_pos[i], ep.drawing_neg[i]])
        print(f"Envelope data saved to {csv_path}")

        mod_wave = get_modified_wave(ep)
        wav_path = os.path.join(new_folder, f"{idx}_future_{os.path.basename(ep.wav_file)}")
        wavfile.write(wav_path, ep.sample_rate, (mod_wave * 32767).astype(np.int16))
        print(f"Modified audio saved to {wav_path}")

    # 8) natural_lang => remove faint wave, add final wave
    for ep in envelope_plots:
        if ep.faint_line is not None:
            ep.faint_line.remove()
            ep.faint_line = None
        mod_wave = get_modified_wave(ep)
        ep.final_line, = ep.ax.plot(mod_wave, color='lime', alpha=0.4, lw=2, label='Modified Wave')

    print("\n=== natural_lang Color Picker ===")
    n_bg, n_pos, n_neg = run_color_picker(f_bg, f_pos, f_neg)
    for ep in envelope_plots:
        ep.reapply_colors(n_bg, n_pos, n_neg)
    axes[0].legend(loc='upper right').get_frame().set_alpha(0.5)

    nat_path = os.path.join(new_folder, "natural_lang.png")
    fig.savefig(nat_path)
    print(f"natural_lang.png saved to {nat_path}")

    # 9) wave_comparison => remove final_line, add original vs. modified wave
    for ep in envelope_plots:
        if ep.final_line is not None:
            ep.final_line.remove()
            ep.final_line = None

        # original wave => negative color, alpha=0.6
        ep.comparison_line_orig, = ep.ax.plot(
            ep.audio_data,
            color=n_neg,
            alpha=0.6,
            lw=2,
            label='Original Wave'
        )
        # modified wave => positive color, alpha=0.8
        mod_data = get_modified_wave(ep)
        ep.comparison_line_mod, = ep.ax.plot(
            mod_data,
            color=n_pos,
            alpha=0.8,
            lw=2,
            label='Modified Wave'
        )

    print("\n=== wave_comparison Color Picker ===")
    c_bg, c_pos, c_neg = run_color_picker(n_bg, n_pos, n_neg)
    for ep in envelope_plots:
        ep.reapply_colors(c_bg, c_pos, c_neg)
    axes[0].legend(loc='upper right').get_frame().set_alpha(0.5)

    cmp_path = os.path.join(new_folder, "wave_comparison.png")
    fig.savefig(cmp_path)
    print(f"wave_comparison.png saved to {cmp_path}")

    plt.close()

if __name__ == '__main__':
    while True:
        process_multi_division()
        cont = input("\nDo you want to process another set of files? (y/n): ").strip().lower()
        if cont != 'y':
            print("Exiting program.")
            break
