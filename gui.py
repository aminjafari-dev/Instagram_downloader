import os
import threading
from queue import Queue, Empty
from typing import Any, Dict

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except Exception:
    tk = None  # type: ignore
    ttk = None  # type: ignore
    filedialog = None  # type: ignore
    messagebox = None  # type: ignore

from downloader import download_instagram_video


class DownloaderGUI:
    def __init__(self) -> None:
        if tk is None:
            raise RuntimeError("Tkinter is not available in this environment.")
        self.root = tk.Tk()
        self.root.title("Instagram Video Downloader")

        self.url_var = tk.StringVar()
        self.output_var = tk.StringVar(value=os.path.join(os.getcwd(), "downloads"))
        self.cookies_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Idle")
        self.progress_var = tk.DoubleVar(value=0.0)

        self.queue: Queue[Dict[str, Any]] = Queue()
        self.downloading = False

        self._build_ui()
        self._poll_queue()

    def _build_ui(self) -> None:
        pad = {"padx": 8, "pady": 6}

        frm = ttk.Frame(self.root)
        frm.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # URL
        ttk.Label(frm, text="Instagram URL:").grid(row=0, column=0, sticky="w", **pad)
        url_entry = ttk.Entry(frm, textvariable=self.url_var, width=60)
        url_entry.grid(row=0, column=1, columnspan=2, sticky="ew", **pad)

        # Output directory
        ttk.Label(frm, text="Output folder:").grid(row=1, column=0, sticky="w", **pad)
        out_entry = ttk.Entry(frm, textvariable=self.output_var, width=50)
        out_entry.grid(row=1, column=1, sticky="ew", **pad)
        ttk.Button(frm, text="Browse", command=self._browse_output).grid(row=1, column=2, sticky="ew", **pad)

        # Cookies file
        ttk.Label(frm, text="Cookies file (optional):").grid(row=2, column=0, sticky="w", **pad)
        cookies_entry = ttk.Entry(frm, textvariable=self.cookies_var, width=50)
        cookies_entry.grid(row=2, column=1, sticky="ew", **pad)
        ttk.Button(frm, text="Browse", command=self._browse_cookies).grid(row=2, column=2, sticky="ew", **pad)

        # Progress bar
        self.progress = ttk.Progressbar(frm, orient="horizontal", length=400, mode="determinate", maximum=100, variable=self.progress_var)
        self.progress.grid(row=3, column=0, columnspan=3, sticky="ew", **pad)

        # Status
        self.status_label = ttk.Label(frm, textvariable=self.status_var)
        self.status_label.grid(row=4, column=0, columnspan=3, sticky="w", **pad)

        # Download button
        self.download_btn = ttk.Button(frm, text="Download", command=self._on_download)
        self.download_btn.grid(row=5, column=0, columnspan=3, sticky="ew", **pad)

        for i in range(3):
            frm.columnconfigure(i, weight=1)

    def _browse_output(self) -> None:
        if filedialog is None:
            return
        directory = filedialog.askdirectory(initialdir=self.output_var.get() or os.getcwd())
        if directory:
            self.output_var.set(directory)

    def _browse_cookies(self) -> None:
        if filedialog is None:
            return
        file_path = filedialog.askopenfilename(title="Select cookies.txt", filetypes=[["Text files", "*.txt"], ["All files", "*.*"]])
        if file_path:
            self.cookies_var.set(file_path)

    def _on_download(self) -> None:
        if self.downloading:
            return
        url = self.url_var.get().strip()
        if not url:
            if messagebox:
                messagebox.showwarning("Missing URL", "Please enter an Instagram URL.")
            return
        output = self.output_var.get().strip() or os.path.join(os.getcwd(), "downloads")
        cookies = self.cookies_var.get().strip() or None

        self.downloading = True
        self.download_btn.configure(state=tk.DISABLED)
        self.status_var.set("Starting download...")
        self.progress_var.set(0.0)

        def gui_progress_hook(status: Dict[str, Any]) -> None:
            self.queue.put(status)

        def worker() -> None:
            code = download_instagram_video(url, output, cookies, gui_progress_hook)
            self.queue.put({"status": "__done__", "code": code})

        threading.Thread(target=worker, daemon=True).start()

    def _poll_queue(self) -> None:
        try:
            while True:
                status = self.queue.get_nowait()
                state = status.get("status")
                if state == "downloading":
                    total = status.get("total_bytes") or status.get("total_bytes_estimate")
                    downloaded = status.get("downloaded_bytes")
                    if total and downloaded:
                        pct = downloaded / total * 100.0
                        self.progress_var.set(max(0.0, min(100.0, pct)))
                        self.status_var.set(f"Downloading: {pct:5.1f}%")
                elif state == "finished":
                    self.progress_var.set(100.0)
                    self.status_var.set("Processing file...")
                elif state == "__done__":
                    code = status.get("code", 1)
                    if code == 0:
                        self.status_var.set("Done ✅")
                    else:
                        self.status_var.set("Failed ❌ (check console)")
                    self.download_btn.configure(state=tk.NORMAL)
                    self.downloading = False
        except Empty:
            pass
        if self.root.winfo_exists():
            self.root.after(100, self._poll_queue)

    def run(self) -> None:
        self.root.mainloop()


