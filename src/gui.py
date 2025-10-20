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

from .downloader import download_instagram_video, download_videos_from_excel
from .page_downloader import download_profile_videos, extract_username_from_url


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
        self.page_mode_var = tk.BooleanVar(value=False)
        self.max_videos_var = tk.IntVar(value=50)
        self.excel_mode_var = tk.BooleanVar(value=False)
        self.excel_file_var = tk.StringVar()
        self.url_column_var = tk.StringVar(value="url")

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

        # Page mode checkbox
        page_check = ttk.Checkbutton(frm, text="Download all videos from profile", variable=self.page_mode_var)
        page_check.grid(row=1, column=0, columnspan=3, sticky="w", **pad)

        # Excel mode checkbox
        excel_check = ttk.Checkbutton(frm, text="Download from Excel file", variable=self.excel_mode_var)
        excel_check.grid(row=2, column=0, columnspan=3, sticky="w", **pad)

        # Max videos (only visible when page mode is enabled)
        self.max_videos_label = ttk.Label(frm, text="Max videos:")
        self.max_videos_spinbox = ttk.Spinbox(frm, from_=1, to=200, width=10, textvariable=self.max_videos_var)

        # Excel file selection (only visible when excel mode is enabled)
        self.excel_file_label = ttk.Label(frm, text="Excel file:")
        self.excel_file_entry = ttk.Entry(frm, textvariable=self.excel_file_var, width=50)
        self.excel_file_button = ttk.Button(frm, text="Browse", command=self._browse_excel_file)
        
        # URL column name (only visible when excel mode is enabled)
        self.url_column_label = ttk.Label(frm, text="URL column name:")
        self.url_column_entry = ttk.Entry(frm, textvariable=self.url_column_var, width=20)
        
        # Output directory
        ttk.Label(frm, text="Output folder:").grid(row=5, column=0, sticky="w", **pad)
        out_entry = ttk.Entry(frm, textvariable=self.output_var, width=50)
        out_entry.grid(row=5, column=1, sticky="ew", **pad)
        ttk.Button(frm, text="Browse", command=self._browse_output).grid(row=5, column=2, sticky="ew", **pad)

        # Cookies file
        ttk.Label(frm, text="Cookies file (optional):").grid(row=6, column=0, sticky="w", **pad)
        cookies_entry = ttk.Entry(frm, textvariable=self.cookies_var, width=50)
        cookies_entry.grid(row=6, column=1, sticky="ew", **pad)
        ttk.Button(frm, text="Browse", command=self._browse_cookies).grid(row=6, column=2, sticky="ew", **pad)

        # Progress bar
        self.progress = ttk.Progressbar(frm, orient="horizontal", length=400, mode="determinate", maximum=100, variable=self.progress_var)
        self.progress.grid(row=7, column=0, columnspan=3, sticky="ew", **pad)

        # Status
        self.status_label = ttk.Label(frm, textvariable=self.status_var)
        self.status_label.grid(row=8, column=0, columnspan=3, sticky="w", **pad)

        # Download button
        self.download_btn = ttk.Button(frm, text="Download", command=self._on_download)
        self.download_btn.grid(row=9, column=0, columnspan=3, sticky="ew", **pad)

        for i in range(3):
            frm.columnconfigure(i, weight=1)

        # Bind checkboxes to show/hide controls
        page_check.configure(command=self._toggle_page_mode)
        excel_check.configure(command=self._toggle_excel_mode)
        self._toggle_page_mode()
        self._toggle_excel_mode()

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

    def _browse_excel_file(self) -> None:
        if filedialog is None:
            return
        file_path = filedialog.askopenfilename(
            title="Select Excel file", 
            filetypes=[["Excel files", "*.xlsx *.xls"], ["All files", "*.*"]]
        )
        if file_path:
            self.excel_file_var.set(file_path)

    def _toggle_page_mode(self) -> None:
        """Show/hide max videos control based on page mode checkbox."""
        if self.page_mode_var.get():
            self.max_videos_label.grid(row=3, column=0, sticky="w", padx=8, pady=6)
            self.max_videos_spinbox.grid(row=3, column=1, sticky="w", padx=8, pady=6)
        else:
            self.max_videos_label.grid_remove()
            self.max_videos_spinbox.grid_remove()

    def _toggle_excel_mode(self) -> None:
        """Show/hide Excel file controls based on excel mode checkbox."""
        if self.excel_mode_var.get():
            self.excel_file_label.grid(row=4, column=0, sticky="w", padx=8, pady=6)
            self.excel_file_entry.grid(row=4, column=1, sticky="ew", padx=8, pady=6)
            self.excel_file_button.grid(row=4, column=2, sticky="ew", padx=8, pady=6)
            self.url_column_label.grid(row=4, column=0, sticky="w", padx=200, pady=6)
            self.url_column_entry.grid(row=4, column=1, columnspan=2, sticky="w", padx=200, pady=6)
        else:
            self.excel_file_label.grid_remove()
            self.excel_file_entry.grid_remove()
            self.excel_file_button.grid_remove()
            self.url_column_label.grid_remove()
            self.url_column_entry.grid_remove()

    def _on_download(self) -> None:
        if self.downloading:
            return
        
        # Validate inputs based on mode
        if self.excel_mode_var.get():
            excel_file = self.excel_file_var.get().strip()
            if not excel_file:
                if messagebox:
                    messagebox.showwarning("Missing Excel File", "Please select an Excel file.")
                return
        else:
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

        def page_progress_callback(current: int, total: int, current_video: str) -> None:
            self.queue.put({
                "status": "page_progress",
                "current": current,
                "total": total,
                "current_video": current_video
            })

        def worker() -> None:
            if self.excel_mode_var.get():
                # Excel batch download mode
                excel_file = self.excel_file_var.get().strip()
                url_column = self.url_column_var.get().strip() or "url"
                
                try:
                    results = download_videos_from_excel(
                        excel_file, output, cookies, url_column, page_progress_callback
                    )
                    
                    # Send completion status
                    success_count = results['success']
                    failed_count = results['failed']
                    if failed_count == 0:
                        self.queue.put({"status": "__done__", "code": 0, "message": f"Downloaded {success_count} videos successfully"})
                    else:
                        self.queue.put({"status": "__done__", "code": 1, "message": f"Downloaded {success_count}/{success_count + failed_count} videos"})
                except Exception as e:
                    self.queue.put({"status": "__done__", "code": 1, "error": str(e)})
            elif self.page_mode_var.get():
                # Page download mode
                url = self.url_var.get().strip()
                username = extract_username_from_url(url)
                if not username:
                    self.queue.put({"status": "__done__", "code": 1, "error": "Invalid Instagram profile URL"})
                    return
                
                max_videos = self.max_videos_var.get()
                results = download_profile_videos(
                    url, output, cookies, max_videos, page_progress_callback
                )
                
                # Send completion status
                success_count = results['success']
                failed_count = results['failed']
                if failed_count == 0:
                    self.queue.put({"status": "__done__", "code": 0, "message": f"Downloaded {success_count} videos successfully"})
                else:
                    self.queue.put({"status": "__done__", "code": 1, "message": f"Downloaded {success_count}/{success_count + failed_count} videos"})
            else:
                # Single video download mode
                url = self.url_var.get().strip()
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
                elif state == "page_progress":
                    current = status.get("current", 0)
                    total = status.get("total", 1)
                    current_video = status.get("current_video", "")
                    pct = (current / total) * 100.0 if total > 0 else 0
                    self.progress_var.set(max(0.0, min(100.0, pct)))
                    self.status_var.set(f"[{current}/{total}] {current_video[:50]}...")
                elif state == "finished":
                    self.progress_var.set(100.0)
                    self.status_var.set("Processing file...")
                elif state == "__done__":
                    code = status.get("code", 1)
                    message = status.get("message", "")
                    if code == 0:
                        self.status_var.set(f"Done ✅ {message}")
                    else:
                        error = status.get("error", "")
                        self.status_var.set(f"Failed ❌ {error or message}")
                    self.download_btn.configure(state=tk.NORMAL)
                    self.downloading = False
        except Empty:
            pass
        if self.root.winfo_exists():
            self.root.after(100, self._poll_queue)

    def run(self) -> None:
        self.root.mainloop()


