# Trainz Mesh GUI

A simple Windows GUI (Open / Export as .im / Exit) that wraps the official
`TrainzMeshImporter.exe` command-line tool, so you don't have to use the
command line to convert Blender 2.79 IM-exporter `.xml` files into Trainz
`.im` mesh files.

## Contents

- `trainz_mesh_gui.py` — the GUI source (Python 3, Tkinter, no extra
  dependencies needed to just *run* it with `python trainz_mesh_gui.py`)
- `TrainzMeshImporter.exe` — the official N3V converter that does the
  actual XML → .im conversion. The GUI just calls this.
- `.github/workflows/build.yml` — a GitHub Actions workflow that builds
  a Windows `.exe` of the GUI automatically, no Windows PC required on
  your end.

## Getting a ready-made .exe (no PC needed)

1. Create a new **public or private** GitHub repository.
2. Upload all the files in this zip, keeping the folder structure
   (the `.github/workflows/build.yml` file must stay at that exact path).
3. Go to the repo's **Actions** tab.
   - If it's your first workflow, click "I understand my workflows, go
     ahead and enable them."
   - Click **Build Windows EXE** in the left sidebar, then **Run workflow**
     (or just push a commit — it runs automatically on push to `main`).
4. Wait ~1–2 minutes for the run to finish (green check mark).
5. Open the finished run, scroll to **Artifacts**, and download
   **TrainzMeshGUI-windows** — it's a zip containing:
   - `TrainzMeshGUI.exe` (the GUI, built fresh by GitHub's Windows runner)
   - `TrainzMeshImporter.exe` (the converter, copied in automatically)
6. Unzip both files into the same folder on your Windows 11 PC and
   double-click `TrainzMeshGUI.exe`.

## Building it yourself instead (if you do have a Windows PC)

```
pip install pyinstaller
pyinstaller --onefile --windowed --name TrainzMeshGUI trainz_mesh_gui.py
```
Then copy `TrainzMeshImporter.exe` into the same folder as the resulting
`dist\TrainzMeshGUI.exe`.

## Using the app

1. **File > Open XML...** — pick the `.xml` written by the Blender 2.79
   IM exporter.
2. Tick **"Also export animation (.kin)"** if you want the animation
   file too (off by default).
3. **File > Export as .im...** — choose a save location; the app runs
   `TrainzMeshImporter.exe` for you and shows its log in the window.
4. **File > Exit** when done.

If `TrainzMeshImporter.exe` isn't in the same folder as the GUI, use
**File > Locate TrainzMeshImporter.exe...** to point at it once — the
app remembers the location after that.
