import matplotlib
matplotlib.rcParams['toolbar'] = 'None'

import os, sys, shutil, csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import sounddevice as sd
from scipy import signal
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.widgets import Slider

##############################################################################
# 1) CUSTOM WAVE GENERATION (Presets or Manual)
##############################################################################
def generate_custom_wave():
    print("\n=== Custom Frequency Waveform Generation ===")
    print("Choose a preset or go manual:")
    print("  1) Sine wave     (freq=440, spw=100, periods=10)")
    print("  2) Square wave   (freq=220, spw=80,  periods=20)")
    print("  3) Triangle wave (freq=100, spw=200, periods=5)")
    print("  4) Sawtooth wave (freq=50,  spw=120, periods=15)")
    print("  5) Manual entry")
    choice = input("Enter 1-5: ").strip()
    wave_type = "sine"
    freq, spw, periods = 440.0, 100, 10
    if choice == "1":
        print("\nPreset 1: Sine wave (freq=440, spw=100, periods=10)")
    elif choice == "2":
        wave_type, freq, spw, periods = "square", 220, 80, 20
        print("\nPreset 2: Square wave (freq=220, spw=80, periods=20)")
    elif choice == "3":
        wave_type, freq, spw, periods = "triangle", 100, 200, 5
        print("\nPreset 3: Triangle wave (freq=100, spw=200, periods=5)")
    elif choice == "4":
        wave_type, freq, spw, periods = "sawtooth", 50, 120, 15
        print("\nPreset 4: Sawtooth wave (freq=50, spw=120, periods=15)")
    elif choice == "5":
        print("\nManual Entry:")
        print("Wave Type (enter 1-4):\n  1) sine\n  2) square\n  3) triangle\n  4) sawtooth")
        wt_choice = input("Wave type (1-4): ").strip()
        if wt_choice == "2":
            wave_type = "square"
        elif wt_choice == "3":
            wave_type = "triangle"
        elif wt_choice == "4":
            wave_type = "sawtooth"
        else:
            wave_type = "sine"
        try:
            freq = float(input("Enter frequency in Hz (e.g. 440): "))
            spw = int(input("Enter samples per wavelength (e.g. 100): "))
            periods = int(input("Enter number of periods (e.g. 10): "))
        except ValueError:
            print("Invalid input. Using defaults: sine, 440 Hz, 100 spw, 10 periods.")
    else:
        print("\nInvalid choice, using default sine wave.")
    total_samples = spw * periods
    sample_rate = int(freq * spw)
    duration = periods / freq
    t = np.linspace(0, duration, total_samples, endpoint=False)
    if wave_type == "square":
        wave = np.sign(np.sin(2*np.pi*freq*t))
    elif wave_type == "triangle":
        wave = signal.sawtooth(2*np.pi*freq*t, 0.5)
    elif wave_type == "sawtooth":
        wave = signal.sawtooth(2*np.pi*freq*t)
    else:
        wave = np.sin(2*np.pi*freq*t)
    wave = wave / np.max(np.abs(wave))
    out_file = input("Enter filename for your custom wave (e.g. my_custom_wave.wav): ").strip()
    if not out_file:
        out_file = "my_custom_wave.wav"
    elif not out_file.lower().endswith(".wav"):
        out_file += ".wav"
    wavfile.write(out_file, sample_rate, (wave * 32767).astype(np.int16))
    print(f"\nGenerated {wave_type} wave, freq={freq} Hz, sample_rate={sample_rate} Hz, samples={total_samples}, duration={duration*1000:.2f} ms.")
    print(f"Custom wave saved to {out_file}")
    return out_file

##############################################################################
# 2) COLOR PICKER FUNCTIONS
##############################################################################
def show_color_options(options, title):
    print(f"\n{title}")
    print(f"{'No.':<5} {'Name':<20} {'Hex Code':<10}  Sample")
    for idx, (name, hex_code) in enumerate(options.items(), 1):
        try:
            r = int(hex_code[1:3], 16)
            g = int(hex_code[3:5], 16)
            b = int(hex_code[5:7], 16)
        except:
            r, g, b = (255,255,255)
        ansi_color = f"\033[38;2;{r};{g};{b}m"
        ansi_reset = "\033[0m"
        print(f"{idx:<5} {name:<20} {hex_code:<10}  {ansi_color}██{ansi_reset}")
    return list(options.values())

def choose_color(options, prompt):
    while True:
        c = input(prompt).strip()
        if not c.isdigit():
            print("Invalid input. Please enter a number.")
            continue
        choice = int(c)
        if 1 <= choice <= len(options):
            return options[choice-1]
        print(f"Please enter a number between 1 and {len(options)}")

def run_color_picker(default_bg, default_pos, default_neg):
    background_options = {
        "Black": "#000000", "Electric Blue": "#0000FF", "Neon Purple": "#BF00FF",
        "Bright Cyan": "#00FFFF", "Vibrant Magenta": "#FF00FF", "Neon Green": "#39FF14",
        "Hot Pink": "#FF69B4", "Neon Orange": "#FF4500", "Bright Yellow": "#FFFF00",
        "Electric Lime": "#CCFF00", "Vivid Red": "#FF0000", "Deep Sky Blue": "#00BFFF",
        "Vivid Violet": "#9F00FF", "Fluorescent Pink": "#FF1493", "Laser Lemon": "#FFFF66",
        "Screamin' Green": "#66FF66", "Ultra Red": "#FF2400", "Radical Red": "#FF355E",
        "Vivid Orange": "#FFA500", "Electric Indigo": "#6F00FF"
    }
    positive_options = {
        "Vibrant Green": "#00FF00", "Neon Green": "#39FF14", "Electric Lime": "#CCFF00",
        "Bright Yellow": "#FFFF00", "Vivid Cyan": "#00FFFF", "Electric Blue": "#0000FF",
        "Neon Purple": "#BF00FF", "Hot Pink": "#FF69B4", "Neon Orange": "#FF4500",
        "Vivid Red": "#FF0000", "Screamin' Green": "#66FF66", "Laser Lemon": "#FFFF66",
        "Fluorescent Magenta": "#FF00FF", "Hyper Blue": "#1F51FF", "Electric Teal": "#00FFEF",
        "Vivid Turquoise": "#00CED1", "Radical Red": "#FF355E", "Ultra Violet": "#7F00FF",
        "Neon Coral": "#FF6EC7", "Luminous Lime": "#BFFF00"
    }
    negative_options = {
        "Vibrant Green": "#00FF00", "Neon Orange": "#FF4500", "Hot Pink": "#FF69B4",
        "Vivid Cyan": "#00FFFF", "Electric Blue": "#0000FF", "Neon Purple": "#BF00FF",
        "Bright Yellow": "#FFFF00", "Electric Lime": "#CCFF00", "Vivid Red": "#FF0000",
        "Deep Pink": "#FF1493", "Screamin' Green": "#66FF66", "Laser Lemon": "#FFFF66",
        "Fluorescent Magenta": "#FF00FF", "Hyper Blue": "#1F51FF", "Electric Teal": "#00FFEF",
        "Vivid Turquoise": "#00CED1", "Radical Red": "#FF355E", "Ultra Violet": "#7F00FF",
        "Neon Coral": "#FF6EC7", "Luminous Lime": "#BFFF00"
    }
    use_custom = input("Use custom colors? (y/n): ").lower() == 'y'
    if not use_custom:
        return default_bg, default_pos, default_neg
    print("\nBackground Colors:")
    bg_vals = show_color_options(background_options, "Pick a background color:")
    bg_pick = choose_color(bg_vals, "Enter number for background: ")
    print("\nPositive Envelope Colors:")
    pos_vals = show_color_options(positive_options, "Pick a positive color:")
    pos_pick = choose_color(pos_vals, "Enter number for positive: ")
    print("\nNegative Envelope Colors:")
    neg_vals = show_color_options(negative_options, "Pick a negative color:")
    neg_pick = choose_color(neg_vals, "Enter number for negative: ")
    return bg_pick, pos_pick, neg_pick

##############################################################################
# 3) STRICT SIGN SUBDIVISION HELPERS
##############################################################################
def strict_sign_subdivision(x, y):
    new_x, new_y, color_val = [], [], []
    n = len(x)
    if n == 0:
        return np.array([]), np.array([]), np.array([])
    def sign_color(val):
        return 0 if val < 0 else 1
    for i in range(n-1):
        xi, yi = x[i], y[i]
        xip1, yip1 = x[i+1], y[i+1]
        new_x.append(xi)
        new_y.append(yi)
        color_val.append(sign_color(yi))
        if (yi < 0 and yip1 >= 0) or (yi >= 0 and yip1 < 0):
            dy = yip1 - yi
            t = (0 - yi)/dy if abs(dy) > 1e-12 else 0.5
            x_cross = xi + t*(xip1 - xi)
            crossing_color = 1 if (yi < 0 and yip1 >= 0) else 0
            new_x.append(x_cross)
            new_y.append(0.0)
            color_val.append(crossing_color)
    new_x.append(x[-1])
    new_y.append(y[-1])
    color_val.append(sign_color(y[-1]))
    return np.array(new_x), np.array(new_y), np.array(color_val)

def plot_strict_sign_colored_line(ax, xdata, ydata, neg_color, pos_color, linewidth=1.0, label="Modified Wave"):
    sx, sy, cvals = strict_sign_subdivision(xdata, ydata)
    points = np.array([sx, sy]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    cmap = ListedColormap([neg_color, pos_color])
    norm = BoundaryNorm([-0.5, 0.5, 1.5], cmap.N)
    lc = LineCollection(segments, cmap=cmap, norm=norm)
    lc.set_array(cvals[:-1])
    lc.set_linewidth(linewidth)  # Thinner line
    ax.add_collection(lc)
    dummy_line = ax.plot([], [], color='none', label=label)[0]
    return lc, dummy_line

##############################################################################
# 4) EnvelopePlot Class (Drawing System)
##############################################################################
class EnvelopePlot:
    def __init__(self, wav_file, ax, bg_color, pos_color, neg_color):
        self.wav_file = wav_file
        self.ax = ax
        self.canvas_bg_color = bg_color
        self.canvas_pos_color = pos_color
        self.canvas_neg_color = neg_color
        self.ax.set_facecolor(self.canvas_bg_color)
        self.fig = self.ax.figure
        self.fig.patch.set_facecolor(self.canvas_bg_color)
        self.sample_rate, data = wavfile.read(wav_file)
        if data.ndim > 1:
            data = np.mean(data, axis=1)
        self.audio_data = data.astype(float) / np.max(np.abs(data))
        self.num_points = len(self.audio_data)
        self.max_amp = np.max(np.abs(self.audio_data))
        
        # Faint line (original wave), thinner with slight alpha
        self.faint_line, = self.ax.plot(self.audio_data, color=self.canvas_pos_color, alpha=0.3, lw=0.8)
        
        self.drawing_pos = np.zeros(self.num_points)
        self.drawing_neg = np.zeros(self.num_points)
        # Thinner lines for envelope
        self.line_pos, = self.ax.plot([], [], color=self.canvas_pos_color, lw=1.0, label='Positive')
        self.line_neg, = self.ax.plot([], [], color=self.canvas_neg_color, lw=1.0, label='Negative')
        self.final_line = None
        self.comparison_line_orig = None
        self.comparison_line_mod = None
        
        # Set fixed range once at init
        margin = 0.1 * self.max_amp
        self.ax.set_xlim(0, self.num_points)
        self.ax.set_ylim(-self.max_amp - margin, self.max_amp + margin)
        self.ax.tick_params(axis='both', colors='gray')
        for spine in self.ax.spines.values():
            spine.set_color('gray')
        base_name = os.path.basename(wav_file)
        self.ax.text(10, self.max_amp - margin, base_name, fontsize=9, color='gray', alpha=0.8, verticalalignment='top')
        self.ax.set_aspect('auto')
        
        self.is_drawing = False
        self.prev_idx = None
        self.last_state_pos = None
        self.last_state_neg = None
        self.background = None
        
        # Store offset (centering shift) used during drawing; initially zero.
        self.offset = 0.0  
        self.center_pos = 1.0
        self.center_neg = 1.0
        self.center_line = None

    def on_mouse_press(self, event):
        if event.inaxes != self.ax:
            return
        self.is_drawing = True
        if event.xdata is not None:
            self.prev_idx = int(round(event.xdata))
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
        idx = int(round(event.xdata))
        if idx < 0 or idx >= self.num_points:
            return
        
        # Compute envelope relative to the current baseline (offset)
        rel_amp = event.ydata - self.offset
        envelope = self.drawing_pos if rel_amp >= 0 else self.drawing_neg
        
        # Interpolate between points if dragging
        if self.prev_idx is not None and idx != self.prev_idx:
            start_idx = self.prev_idx
            end_idx = idx
            if start_idx > end_idx:
                start_idx, end_idx = end_idx, start_idx
                start_val = rel_amp
                end_val = envelope[self.prev_idx]
            else:
                start_val = envelope[self.prev_idx]
                end_val = rel_amp
            envelope[start_idx:end_idx+1] = np.linspace(start_val, end_val, end_idx - start_idx + 1)
        else:
            envelope[idx] = rel_amp
        
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
        if self.faint_line is not None:
            self.faint_line.set_data(np.arange(self.num_points), self.audio_data + self.offset)
        self.ax.figure.canvas.draw_idle()

    def preview_envelope(self):
        adjusted = np.copy(self.audio_data)
        for i in range(len(adjusted)):
            if adjusted[i] >= 0:
                adjusted[i] = self.center_pos * self.drawing_pos[i] + self.offset
            else:
                adjusted[i] = self.center_neg * self.drawing_neg[i] + self.offset
        # For preview we subtract the offset (DC correction)
        adjusted = adjusted - self.offset
        audio_int16 = (adjusted * 32767).astype(np.int16)
        sd.play(audio_int16, self.sample_rate)
        sd.wait()

    def reapply_colors(self, bg_color, pos_color, neg_color, faint_alpha=0.3,
                       final_wave_color="#00FF00", final_wave_alpha=0.8, orig_alpha=0.6, mod_alpha=0.8):
        self.ax.set_facecolor(bg_color)
        self.fig.patch.set_facecolor(bg_color)
        if self.faint_line is not None:
            self.faint_line.set_color(pos_color)
            self.faint_line.set_alpha(faint_alpha)
            self.faint_line.set_linewidth(0.8)
        if self.line_pos is not None:
            self.line_pos.set_color(pos_color)
            self.line_pos.set_linewidth(1.0)
        if self.line_neg is not None:
            self.line_neg.set_color(neg_color)
            self.line_neg.set_linewidth(1.0)
        if self.final_line is not None:
            self.final_line.set_color(final_wave_color)
            self.final_line.set_alpha(final_wave_alpha)
            self.final_line.set_linewidth(1.0)
        if self.comparison_line_orig is not None:
            self.comparison_line_orig.set_color(neg_color)
            self.comparison_line_orig.set_alpha(orig_alpha)
            self.comparison_line_orig.set_linewidth(1.0)
        if self.comparison_line_mod is not None:
            self.comparison_line_mod.set_color(pos_color)
            self.comparison_line_mod.set_alpha(mod_alpha)
            self.comparison_line_mod.set_linewidth(1.0)
        self.ax.set_aspect('auto')
        self.ax.figure.canvas.draw_idle()

##############################################################################
# 5) NEW ENVELOPE WAVEFORM MODIFICATION USING CSV DATA
##############################################################################
def load_envelope_csv(csv_path):
    """Load envelope data from CSV.
       Returns two numpy arrays: positive_envelope, negative_envelope.
       The CSV file is expected to have a header row:
         Index, Positive, Negative
    """
    pos = []
    neg = []
    with open(csv_path, newline="") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            pos.append(float(row[1]))
            neg.append(float(row[2]))
    return np.array(pos), np.array(neg)

def get_modified_wave(ep, csv_path, subtract_offset=True):
    """
    Compute modified waveform using envelope data loaded from CSV.
    For each sample, if the original audio is positive, use the CSV 'Positive'
    value plus the baseline offset; if negative, use the CSV 'Negative' value.
    If subtract_offset is True (for WAV file output), the centering offset is removed.
    If False (for plotting Natural Language/Comparison), the waveform remains in its shifted position.
    """
    loaded_pos, loaded_neg = load_envelope_csv(csv_path)
    adjusted = np.copy(ep.audio_data)
    for i in range(len(adjusted)):
        if adjusted[i] >= 0:
            adjusted[i] = loaded_pos[i] + ep.offset
        else:
            adjusted[i] = loaded_neg[i] + ep.offset
    if subtract_offset:
        adjusted = adjusted - ep.offset
    return adjusted

##############################################################################
# 6) MULTI-FILE PROCESS WITH VERTICAL SPACING, CENTERING, AND DRAWING PHASES
##############################################################################
def process_multi_division():
    print("\n=== Multi-Division Wave Processing ===")
    try:
        num_div = int(input("Enter number of divisions (subplots): "))
    except ValueError:
        num_div = 1

    wav_files = []
    for i in range(num_div):
        print(f"\n--- Subplot {i+1} ---")
        mode = input("  (1) Use existing .wav\n  (2) Generate custom wave\nEnter 1 or 2: ").strip()
        if mode == '2':
            out_file = generate_custom_wave()
            wav_files.append(out_file)
        else:
            wf = input(f"Enter path to existing .wav file for subplot {i+1}: ")
            if not os.path.exists(wf):
                print(f"File not found: {wf}")
                sys.exit(1)
            wav_files.append(wf)

    first_base = os.path.splitext(os.path.basename(wav_files[0]))[0]
    new_folder = os.path.join(os.getcwd(), first_base)
    os.makedirs(new_folder, exist_ok=True)
    print(f"Created folder: {new_folder}")
    for wf in wav_files:
        shutil.copy(wf, new_folder)
        print(f"Copied {wf} to {new_folder}")

    print("\n=== Drawing Canvas Color Picker ===")
    default_bg, default_pos, default_neg = "#000000", "#00FF00", "#00FF00"
    draw_bg, draw_pos, draw_neg = run_color_picker(default_bg, default_pos, default_neg)

    fig, axes = plt.subplots(num_div, 1, figsize=(16,3*num_div), facecolor=draw_bg)
    fig.subplots_adjust(left=0.06, right=0.98, top=0.95, bottom=0.05, hspace=0)
    if num_div == 1:
        axes = [axes]

    # --- VERTICAL SPACING ADJUSTMENT PHASE ---
    adjust = input("Do you want to adjust vertical spacing? (y/n): ").strip().lower()
    if adjust == 'y':
        print("\n=== Readjustment Phase ===")
        fixed_top, fixed_bottom = 0.95, 0.05
        total_available = fixed_top - fixed_bottom
        heights = [total_available/num_div]*num_div
        positions = []
        current_top = fixed_top
        for h in heights:
            bottom = current_top - h
            positions.append([0.06, bottom, 0.92, h])
            current_top = bottom
        for i, ax in enumerate(axes):
            ax.set_position(positions[i])
        slider_height = 0.1
        slider_insets = []
        for i, ax in enumerate(axes):
            inset_ax = ax.inset_axes([0.05,0.45,0.9,slider_height], facecolor="lightgray")
            s = Slider(inset_ax, f"Height {i+1}", 0.05, total_available, valinit=heights[i],
                      valfmt="%.2f", color="blue")
            slider_insets.append(s)
        plt.pause(0.1)
        current_positions = positions.copy()
        weights = heights.copy()
        def slider_callback(val, i):
            nonlocal current_positions, weights, axes, fixed_bottom, total_available
            pos = current_positions[i]
            top = pos[1]+pos[3]
            new_height = val
            new_bottom = top - new_height
            current_positions[i] = [pos[0], new_bottom, pos[2], new_height]
            weights[i] = new_height
            if i+1 < num_div:
                available = new_bottom - fixed_bottom
                total_weight = sum(weights[j] for j in range(i+1,num_div))
                current_top = new_bottom
                for j in range(i+1,num_div):
                    new_h = (weights[j]/total_weight)*available if total_weight>0 else available/(num_div-i-1)
                    weights[j] = new_h
                    new_bottom_j = current_top - new_h
                    current_positions[j] = [current_positions[j][0], new_bottom_j, current_positions[j][2], new_h]
                    current_top = new_bottom_j
            for j, ax in enumerate(axes):
                ax.set_position(current_positions[j])
                new_inset_pos = [0.05,0.45,0.9,slider_height]
                slider_insets[j].ax.set_position(new_inset_pos)
            fig.canvas.draw_idle()
        for i, s in enumerate(slider_insets):
            s.on_changed(lambda val, i=i: slider_callback(val, i))
        print("Adjust vertical spacing as desired. Press Enter when done.")
        input()
        for s in slider_insets:
            s.ax.remove()
        fig.canvas.draw_idle()
    # --- END VERTICAL SPACING ADJUSTMENT ---

    # --- CREATE EnvelopePlot INSTANCES ---
    envelope_plots = []
    for i, wf in enumerate(wav_files):
        ep = EnvelopePlot(wf, axes[i], draw_bg, draw_pos, draw_neg)
        envelope_plots.append(ep)
        axes[i].set_aspect('auto')
        if i==0:
            leg = axes[i].legend(loc='upper right')
            leg.get_frame().set_alpha(0.5)
            axes[i].text(0.65,0.90,"p=preview\nr=reset\nu=undo",
                         transform=axes[i].transAxes,fontsize=8,color='white',
                         ha='left',va='top',
                         bbox=dict(boxstyle="round",fc="black",ec="none",alpha=0.5))
    
    # --- CENTERING PHASE ---
    print("\n=== Centering Phase ===")
    center_sliders = []
    for i, ep in enumerate(envelope_plots):
        ax = ep.ax
        inset_ax = ax.inset_axes([0.35,0.05,0.3,0.1], facecolor="lightgray")
        slider = Slider(inset_ax, "Center", -0.9, 0.9, valinit=ep.offset, valfmt="%.2f", color="orange")
        center_sliders.append(slider)
        def update_center(val, ep=ep):
            ep.offset = val
            ep.redraw_lines()
            ep.ax.figure.canvas.draw_idle()
        slider.on_changed(update_center)
    print("Adjust centering sliders as desired.")
    input("Press Enter to finalize centering phase...")
    for slider in center_sliders:
        slider.ax.remove()
    fig.canvas.draw_idle()
    
    # --- DRAWING PHASE ---
    print("\n=== Drawing Phase ===")
    print("Use your mouse to draw the envelope.\nPress 'p' to preview, 'r' to reset, 'u' to undo the last stroke.")
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
            print("Previewing ALL subplots...")
            for epp in envelope_plots:
                epp.preview_envelope()
        elif k in ['r','u']:
            for ep in envelope_plots:
                if event.inaxes == ep.ax:
                    if k == 'r':
                        ep.reset_envelope()
                        print("Envelope reset for this subplot.")
                    elif k == 'u':
                        ep.undo_envelope()
                        print("Undo last stroke for this subplot.")
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
    
    # --- FINAL DRAWING, SAVING, AND COMPARISON PHASES ---
    print("\n=== Final Drawing Color Picker ===")
    f_bg, f_pos, f_neg = run_color_picker(draw_bg, draw_pos, draw_neg)
    for ep in envelope_plots:
        ep.reapply_colors(f_bg, f_pos, f_neg)
    first_base = os.path.splitext(os.path.basename(wav_files[0]))[0]
    new_folder = os.path.join(os.getcwd(), first_base)
    
    # --- SAVE CSV FILES and store CSV paths ---
    csv_paths = []
    for idx, ep in enumerate(envelope_plots, 1):
        csv_path = os.path.join(new_folder, f"envelope_{idx}.csv")
        with open(csv_path, "w", newline="") as f_:
            writer = csv.writer(f_)
            writer.writerow(["Index", "Positive", "Negative"])
            for i in range(ep.num_points):
                writer.writerow([i, ep.drawing_pos[i], ep.drawing_neg[i]])
        print(f"Envelope data saved to {csv_path}")
        csv_paths.append(csv_path)
    
    # --- Create and save final drawing image (unchanged) ---
    final_path = os.path.join(new_folder, "final_drawing.png")
    fig.savefig(final_path)
    print("final_drawing.png saved to", final_path)
    
    # --- Create modified audio files using envelope data from CSV ---
    for idx, ep in enumerate(envelope_plots, 1):
        csv_path = csv_paths[idx-1]
        # For WAV file output, subtract offset (default behavior)
        mod_wave = get_modified_wave(ep, csv_path)
        wav_path = os.path.join(new_folder, f"{idx}_future_{os.path.basename(ep.wav_file)}")
        wavfile.write(wav_path, ep.sample_rate, (mod_wave * 32767).astype(np.int16))
        print(f"Modified audio saved to {wav_path}")
    
    # --- NATURAL LANGUAGE PHASE ---
    print("\n=== Natural Language Color Picker ===")
    n_bg, n_pos, n_neg = run_color_picker(f_bg, f_pos, f_neg)
    for idx, ep in enumerate(envelope_plots, 1):
        # Remove previous envelope lines
        if ep.faint_line is not None:
            ep.faint_line.remove()
            ep.faint_line = None
        if ep.line_pos is not None:
            ep.line_pos.remove()
            ep.line_pos = None
        if ep.line_neg is not None:
            ep.line_neg.remove()
            ep.line_neg = None
        if ep.final_line is not None:
            ep.final_line.remove()
            ep.final_line = None
        # Plot strict sign colored line (unique to natural_lang) with thinner lines
        mod_wave = get_modified_wave(ep, csv_paths[idx-1], subtract_offset=False)
        xvals = np.arange(len(mod_wave))
        plot_strict_sign_colored_line(ep.ax, xvals, mod_wave,
                                      neg_color=n_neg, pos_color=n_pos,
                                      linewidth=1.0,  # Thinner line
                                      label="Modified Wave")
        ep.ax.set_xlim(0, ep.num_points)
    for ep in envelope_plots:
        ep.reapply_colors(n_bg, n_pos, n_neg)
    axes[0].legend(loc='upper right').get_frame().set_alpha(0.5)
    nat_path = os.path.join(new_folder, "natural_lang.png")
    fig.savefig(nat_path)
    print("natural_lang.png saved to", nat_path)
    
    # --- WAVE COMPARISON PHASE ---
    for idx, ep in enumerate(envelope_plots, 1):
        if ep.final_line is not None:
            ep.final_line.remove()
            ep.final_line = None
        ep.comparison_line_orig, = ep.ax.plot(ep.audio_data, color=n_neg, alpha=0.6, lw=1.0, label='Original Wave')
        mod_data = get_modified_wave(ep, csv_paths[idx-1], subtract_offset=False)
        ep.comparison_line_mod, = ep.ax.plot(mod_data, color=n_pos, alpha=0.8, lw=1.0, label='Modified Wave')
        ep.ax.set_xlim(0, ep.num_points)
    print("\n=== Wave Comparison Color Picker ===")
    c_bg, c_pos, c_neg = run_color_picker(n_bg, n_pos, n_neg)
    for ep in envelope_plots:
        ep.reapply_colors(c_bg, c_pos, c_neg)
        if ep.comparison_line_mod is not None:
            ep.comparison_line_mod.set_alpha(0.4)
            ep.comparison_line_mod.set_linewidth(1.0)
        if ep.comparison_line_orig is not None:
            ep.comparison_line_orig.set_alpha(0.6)
            ep.comparison_line_orig.set_linewidth(1.0)
    axes[0].legend(loc='upper right').get_frame().set_alpha(0.5)
    cmp_path = os.path.join(new_folder, "wave_comparison.png")
    fig.savefig(cmp_path)
    print("wave_comparison.png saved to", cmp_path)
    plt.close()
    plt.ioff()

def main():
    while True:
        process_multi_division()
        cont = input("\nDo you want to process another set of files? (y/n): ").strip().lower()
        if cont != 'y':
            print("Exiting program.")
            break

if __name__ == '__main__':
    main()
