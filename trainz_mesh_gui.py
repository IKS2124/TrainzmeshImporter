"""
Trainz Mesh Importer GUI
=========================
A small front-end for N3V Games' command-line "TrainzMeshImporter.exe" tool.

It does NOT re-implement the XML -> .im conversion itself (that logic lives
inside TrainzMeshImporter.exe, which already does it correctly). This GUI
just gives you:

    File > Open XML...        - pick the .xml file written by the
                                 Blender 2.79 IM exporter
    File > Export as .im...   - choose where to save, then runs
                                 TrainzMeshImporter.exe for you
    File > Exit

It looks for TrainzMeshImporter.exe in the same folder as this program.
If it can't find it, it will ask you to browse to it once, and remember
the location (saved to trainz_gui_config.json next to the program) for
next time.

Building this into a Windows .exe
----------------------------------
On a Windows machine with Python 3 installed:

    pip install pyinstaller
    pyinstaller --onefile --windowed --name TrainzMeshGUI trainz_mesh_gui.py

Then copy the real TrainzMeshImporter.exe into the same folder as the
resulting dist\\TrainzMeshGUI.exe (or use the "Locate..." menu item to
point at it wherever it lives).
"""

import json
import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

CONFIG_FILENAME = "trainz_gui_config.json"
IMPORTER_NAME = "TrainzMeshImporter.exe"


def app_dir():
    """Folder the running program (script or frozen exe) lives in."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def config_path():
    return os.path.join(app_dir(), CONFIG_FILENAME)


def load_config():
    path = config_path()
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_config(cfg):
    try:
        with open(config_path(), "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass


class TrainzMeshGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Trainz Mesh Importer GUI")
        self.geometry("700x460")
        self.minsize(560, 360)

        self.config_data = load_config()
        self.input_xml = tk.StringVar(value="")
        self.importer_path = tk.StringVar(
            value=self.config_data.get("importer_path", self._default_importer_path())
        )
        self.export_kin = tk.BooleanVar(value=False)

        self._build_menu()
        self._build_body()
        self._log("Ready. Use File > Open XML... to begin.")

    # ---------- setup helpers ----------

    def _default_importer_path(self):
        candidate = os.path.join(app_dir(), IMPORTER_NAME)
        return candidate if os.path.isfile(candidate) else ""

    def _build_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open XML...", command=self.open_xml, accelerator="Ctrl+O")
        file_menu.add_command(label="Export as .im...", command=self.export_im, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Locate TrainzMeshImporter.exe...", command=self.locate_importer)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_exit, accelerator="Ctrl+Q")
        menubar.add_cascade(label="File", menu=file_menu)

        self.config(menu=menubar)

        self.bind_all("<Control-o>", lambda e: self.open_xml())
        self.bind_all("<Control-e>", lambda e: self.export_im())
        self.bind_all("<Control-q>", lambda e: self.on_exit())

    def _build_body(self):
        pad = {"padx": 10, "pady": 6}

        top = ttk.Frame(self)
        top.pack(fill="x", **pad)

        ttk.Label(top, text="Input XML:").grid(row=0, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.input_xml, state="readonly").grid(
            row=0, column=1, sticky="ew", padx=6
        )
        ttk.Button(top, text="Open...", command=self.open_xml).grid(row=0, column=2)
        top.columnconfigure(1, weight=1)

        ttk.Label(top, text="Importer exe:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(top, textvariable=self.importer_path, state="readonly").grid(
            row=1, column=1, sticky="ew", padx=6, pady=(6, 0)
        )
        ttk.Button(top, text="Locate...", command=self.locate_importer).grid(
            row=1, column=2, pady=(6, 0)
        )

        opts = ttk.Frame(self)
        opts.pack(fill="x", **pad)
        ttk.Checkbutton(
            opts, text="Also export animation (.kin) if present in XML", variable=self.export_kin
        ).pack(side="left")

        btns = ttk.Frame(self)
        btns.pack(fill="x", **pad)
        ttk.Button(btns, text="Export as .im...", command=self.export_im).pack(side="left")
        ttk.Button(btns, text="Exit", command=self.on_exit).pack(side="right")

        ttk.Label(self, text="Log:").pack(anchor="w", padx=10)
        log_frame = ttk.Frame(self)
        log_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.log_box = tk.Text(log_frame, height=14, wrap="word", state="disabled")
        scroll = ttk.Scrollbar(log_frame, command=self.log_box.yview)
        self.log_box.configure(yscrollcommand=scroll.set)
        self.log_box.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    # ---------- logging ----------

    def _log(self, text):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text.rstrip() + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # ---------- actions ----------

    def open_xml(self):
        path = filedialog.askopenfilename(
            title="Open mesh XML (from Blender 2.79 IM exporter)",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
        )
        if path:
            self.input_xml.set(path)
            self._log(f"Opened: {path}")

    def locate_importer(self):
        path = filedialog.askopenfilename(
            title="Locate TrainzMeshImporter.exe",
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
        )
        if path:
            self.importer_path.set(path)
            self.config_data["importer_path"] = path
            save_config(self.config_data)
            self._log(f"TrainzMeshImporter.exe set to: {path}")

    def export_im(self):
        if not self.input_xml.get():
            messagebox.showwarning("No input file", "Please open an XML file first.")
            return

        if not self.importer_path.get() or not os.path.isfile(self.importer_path.get()):
            messagebox.showwarning(
                "Importer not found",
                "TrainzMeshImporter.exe was not found.\nPlease use 'Locate...' to select it.",
            )
            self.locate_importer()
            if not self.importer_path.get() or not os.path.isfile(self.importer_path.get()):
                return

        default_name = os.path.splitext(os.path.basename(self.input_xml.get()))[0]
        save_path = filedialog.asksaveasfilename(
            title="Export as .im",
            defaultextension=".im",
            initialfile=default_name,
            filetypes=[("Trainz mesh", "*.im"), ("All files", "*.*")],
        )
        if not save_path:
            return

        out_base = os.path.splitext(save_path)[0]  # importer ignores the extension you give it

        cmd = [
            self.importer_path.get(),
            "-inFile", self.input_xml.get(),
            "-outFile", out_base,
            "-outputIM", "true",
            "-outputKIN", "true" if self.export_kin.get() else "false",
            "-warnings", "true",
            "-info", "true",
        ]

        self._log("Running: " + " ".join(f'"{c}"' if " " in c else c for c in cmd))
        threading.Thread(target=self._run_importer, args=(cmd, out_base), daemon=True).start()

    def _run_importer(self, cmd, out_base):
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            if result.stdout:
                self._log(result.stdout)
            if result.stderr:
                self._log(result.stderr)

            im_file = out_base + ".im"
            if result.returncode == 0 and os.path.isfile(im_file):
                self._log(f"Success: wrote {im_file}")
                self.after(0, lambda: messagebox.showinfo("Export complete", f"Wrote:\n{im_file}"))
            else:
                self._log(f"Exporter exited with code {result.returncode}.")
                self.after(
                    0,
                    lambda: messagebox.showerror(
                        "Export failed",
                        "TrainzMeshImporter reported an error.\nSee the log for details.",
                    ),
                )
        except Exception as exc:
            self._log(f"Error running importer: {exc}")
            self.after(0, lambda: messagebox.showerror("Error", str(exc)))

    def on_exit(self):
        self.destroy()


if __name__ == "__main__":
    app = TrainzMeshGUI()
    app.mainloop()
