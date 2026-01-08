#!/usr/bin/env python3
"""
PDF Forensic Sanitizer - Professional Edition
Remove forensic traces from PDF files with full control
Created by: Itay Naftali
"""

import sys
import os
import re
import zlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading


class PDFSanitizer:
    def __init__(self):
        self.stats = {}

    def sanitize_pdf(self, input_path, output_path=None, options=None, progress_callback=None):
        """Sanitize PDF based on selected options"""

        if output_path is None:
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_sanitized{ext}"

        if options is None:
            options = {
                'remove_author': True, 'remove_creator': True, 'remove_producer': True,
                'remove_title': True, 'remove_subject': True, 'remove_timestamps': True,
                'remove_timezone': True, 'remove_lang_tags': True, 'remove_doc_id': True,
                'remove_xmp': True
            }

        self.stats = {
            'author': False, 'creator': False, 'producer': False,
            'title': False, 'subject': False, 'timestamps': False,
            'timezone': False, 'lang_tags': 0, 'doc_id': False, 'xmp': False
        }

        with open(input_path, 'rb') as f:
            data = f.read()

        if progress_callback:
            progress_callback(5, "Reading PDF...")

        # === COMPRESSED STREAMS (Language Tags) ===
        if options.get('remove_lang_tags'):
            if progress_callback:
                progress_callback(10, "Processing compressed streams...")

            def replace_in_stream(match):
                stream_data = match.group(1)
                try:
                    decompressed = zlib.decompress(stream_data)
                    if b'/Lang(he)' in decompressed:
                        count = decompressed.count(b'/Lang(he)')
                        self.stats['lang_tags'] += count
                        decompressed = decompressed.replace(b'/Lang(he)', b'/Lang(en)')
                        recompressed = zlib.compress(decompressed, 9)
                        return b'stream\r\n' + recompressed + b'\r\nendstream'
                except:
                    pass
                return match.group(0)

            stream_pattern = rb'stream\r?\n(.+?)\r?\nendstream'
            data = re.sub(stream_pattern, replace_in_stream, data, flags=re.DOTALL)

        # === TIMEZONE ===
        if options.get('remove_timezone'):
            if progress_callback:
                progress_callback(20, "Removing timezone info...")
            date_pattern = rb"(D:\d{14})([+-]\d{2}'\d{2}')"
            if re.search(date_pattern, data):
                self.stats['timezone'] = True
            data = re.sub(date_pattern, rb"\1Z", data)

        # === AUTHOR ===
        if options.get('remove_author'):
            if progress_callback:
                progress_callback(25, "Removing author...")
            if re.search(rb'/Author\([^)]+\)', data) or re.search(rb'/Author<[^>]+>', data):
                self.stats['author'] = True
            data = re.sub(rb'/Author\([^)]*\)', b'/Author()', data)
            data = re.sub(rb'/Author<[^>]*>', b'/Author<>', data)

        # === CREATOR ===
        if options.get('remove_creator'):
            if progress_callback:
                progress_callback(30, "Removing creator...")
            if re.search(rb'/Creator\([^)]+\)', data) or re.search(rb'/Creator<[^>]+>', data):
                self.stats['creator'] = True
            data = re.sub(rb'/Creator\([^)]*\)', b'/Creator()', data)
            data = re.sub(rb'/Creator<[^>]*>', b'/Creator<>', data)

        # === PRODUCER ===
        if options.get('remove_producer'):
            if progress_callback:
                progress_callback(35, "Removing producer...")
            if re.search(rb'/Producer\([^)]+\)', data) or re.search(rb'/Producer<[^>]+>', data):
                self.stats['producer'] = True
            data = re.sub(rb'/Producer\([^)]*\)', b'/Producer()', data)
            data = re.sub(rb'/Producer<[^>]*>', b'/Producer<>', data)

        # === TITLE ===
        if options.get('remove_title'):
            if progress_callback:
                progress_callback(40, "Removing title...")
            if re.search(rb'/Title\([^)]+\)', data) or re.search(rb'/Title<[^>]+>', data):
                self.stats['title'] = True
            data = re.sub(rb'/Title\([^)]*\)', b'/Title()', data)
            data = re.sub(rb'/Title<[^>]*>', b'/Title<>', data)

        # === SUBJECT ===
        if options.get('remove_subject'):
            if progress_callback:
                progress_callback(45, "Removing subject...")
            if re.search(rb'/Subject\([^)]+\)', data) or re.search(rb'/Subject<[^>]+>', data):
                self.stats['subject'] = True
            data = re.sub(rb'/Subject\([^)]*\)', b'/Subject()', data)
            data = re.sub(rb'/Subject<[^>]*>', b'/Subject<>', data)

        # === LANGUAGE TAGS (uncompressed) ===
        if options.get('remove_lang_tags'):
            if progress_callback:
                progress_callback(50, "Removing language tags...")
            data = re.sub(rb'/Lang\(he\)', b'/Lang(en)', data)

        # === DOCUMENT ID ===
        if options.get('remove_doc_id'):
            if progress_callback:
                progress_callback(55, "Removing document ID...")
            if re.search(rb'/ID\s*\[\s*<[A-Fa-f0-9]+>', data):
                self.stats['doc_id'] = True
            data = re.sub(
                rb'/ID\s*\[\s*<[A-Fa-f0-9]+>\s*<[A-Fa-f0-9]+>\s*\]',
                b'/ID[<00000000000000000000000000000000><00000000000000000000000000000000>]',
                data
            )

        # === TIMESTAMPS ===
        if options.get('remove_timestamps'):
            if progress_callback:
                progress_callback(60, "Removing timestamps...")
            if re.search(rb'/CreationDate\([^)]+\)', data):
                self.stats['timestamps'] = True
            data = re.sub(rb'/CreationDate\([^)]*\)', b'/CreationDate(D:19700101000000Z)', data)
            data = re.sub(rb'/ModDate\([^)]*\)', b'/ModDate(D:19700101000000Z)', data)

        # === XMP METADATA ===
        if options.get('remove_xmp'):
            if progress_callback:
                progress_callback(70, "Removing XMP metadata...")
            self.stats['xmp'] = True

            data = re.sub(rb'<xmp:CreatorTool>[^<]*</xmp:CreatorTool>',
                          b'<xmp:CreatorTool></xmp:CreatorTool>', data)
            data = re.sub(rb'<dc:creator>.*?</dc:creator>',
                          b'<dc:creator><rdf:Seq><rdf:li></rdf:li></rdf:Seq></dc:creator>',
                          data, flags=re.DOTALL)
            data = re.sub(rb'<dc:title>.*?</dc:title>',
                          b'<dc:title><rdf:Alt><rdf:li xml:lang="x-default"></rdf:li></rdf:Alt></dc:title>',
                          data, flags=re.DOTALL)
            data = re.sub(rb'<dc:description>.*?</dc:description>',
                          b'<dc:description><rdf:Alt><rdf:li xml:lang="x-default"></rdf:li></rdf:Alt></dc:description>',
                          data, flags=re.DOTALL)
            data = re.sub(rb'<pdf:Producer>[^<]*</pdf:Producer>',
                          b'<pdf:Producer></pdf:Producer>', data)
            data = re.sub(rb'<xmpMM:DocumentID>[^<]*</xmpMM:DocumentID>',
                          b'<xmpMM:DocumentID>uuid:00000000-0000-0000-0000-000000000000</xmpMM:DocumentID>', data)
            data = re.sub(rb'<xmpMM:InstanceID>[^<]*</xmpMM:InstanceID>',
                          b'<xmpMM:InstanceID>uuid:00000000-0000-0000-0000-000000000000</xmpMM:InstanceID>', data)
            data = re.sub(rb'<xmp:CreateDate>[^<]*</xmp:CreateDate>',
                          b'<xmp:CreateDate>1970-01-01T00:00:00Z</xmp:CreateDate>', data)
            data = re.sub(rb'<xmp:ModifyDate>[^<]*</xmp:ModifyDate>',
                          b'<xmp:ModifyDate>1970-01-01T00:00:00Z</xmp:ModifyDate>', data)

        # === WRITE OUTPUT ===
        if progress_callback:
            progress_callback(90, "Writing file...")

        with open(output_path, 'wb') as f:
            f.write(data)

        if progress_callback:
            progress_callback(100, "Complete!")

        return output_path, self.stats


class ModernGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PDF Forensic Sanitizer")
        self.root.geometry("650x750")
        self.root.minsize(600, 700)
        self.root.resizable(True, True)
        self.root.configure(bg='#0d1117')

        self.sanitizer = PDFSanitizer()
        self.selected_file = None
        self.options_vars = {}

        self.setup_ui()

    def setup_ui(self):
        # Colors
        self.bg_dark = '#0d1117'
        self.bg_card = '#161b22'
        self.bg_input = '#21262d'
        self.accent = '#238636'
        self.accent_red = '#da3633'
        self.text_primary = '#f0f6fc'
        self.text_secondary = '#8b949e'
        self.border = '#30363d'

        # Main container with scrollable canvas
        main = tk.Frame(self.root, bg=self.bg_dark, padx=25, pady=15)
        main.pack(fill=tk.BOTH, expand=True)

        # === HEADER ===
        header = tk.Frame(main, bg=self.bg_dark)
        header.pack(fill=tk.X, pady=(0, 15))

        title = tk.Label(header, text="PDF Forensic Sanitizer",
                        font=('Segoe UI', 22, 'bold'),
                        bg=self.bg_dark, fg=self.text_primary)
        title.pack()

        subtitle = tk.Label(header, text="Remove metadata and forensic traces from PDF files",
                           font=('Segoe UI', 10),
                           bg=self.bg_dark, fg=self.text_secondary)
        subtitle.pack(pady=(3, 0))

        credits = tk.Label(header, text="Created by Itay Naftali",
                          font=('Segoe UI', 9, 'bold'),
                          bg=self.bg_dark, fg='#58a6ff')
        credits.pack(pady=(5, 0))

        # === FILE SELECTION CARD ===
        file_card = tk.Frame(main, bg=self.bg_card, padx=15, pady=12)
        file_card.pack(fill=tk.X, pady=(0, 12))

        file_header = tk.Label(file_card, text="SELECT FILE",
                              font=('Segoe UI', 10, 'bold'),
                              bg=self.bg_card, fg=self.accent)
        file_header.pack(anchor='w')

        file_row = tk.Frame(file_card, bg=self.bg_card)
        file_row.pack(fill=tk.X, pady=(10, 0))

        self.file_entry = tk.Entry(file_row, font=('Segoe UI', 11),
                                   bg=self.bg_input, fg=self.text_primary,
                                   insertbackground=self.text_primary,
                                   relief='flat', bd=0)
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, ipadx=10)
        self.file_entry.insert(0, "No file selected...")
        self.file_entry.config(state='readonly')

        browse_btn = tk.Button(file_row, text="Browse",
                              font=('Segoe UI', 10, 'bold'),
                              bg=self.accent, fg='white',
                              activebackground='#2ea043',
                              relief='flat', padx=20, pady=8,
                              cursor='hand2',
                              command=self.browse_file)
        browse_btn.pack(side=tk.RIGHT, padx=(15, 0))

        # === OPTIONS CARD ===
        options_card = tk.Frame(main, bg=self.bg_card, padx=15, pady=12)
        options_card.pack(fill=tk.X, pady=(0, 12))

        options_header = tk.Label(options_card, text="SANITIZATION OPTIONS",
                                 font=('Segoe UI', 10, 'bold'),
                                 bg=self.bg_card, fg=self.accent)
        options_header.pack(anchor='w')

        options_desc = tk.Label(options_card,
                               text="Select which forensic data to remove",
                               font=('Segoe UI', 9),
                               bg=self.bg_card, fg=self.text_secondary)
        options_desc.pack(anchor='w', pady=(2, 10))

        # Options grid
        opts_frame = tk.Frame(options_card, bg=self.bg_card)
        opts_frame.pack(fill=tk.BOTH, expand=True)

        # Left column
        left_col = tk.Frame(opts_frame, bg=self.bg_card)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right column
        right_col = tk.Frame(opts_frame, bg=self.bg_card)
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Options definitions
        left_opts = [
            ('remove_author', 'Author', 'Remove document author name'),
            ('remove_creator', 'Creator', 'Remove creating application'),
            ('remove_producer', 'Producer', 'Remove PDF producer software'),
            ('remove_title', 'Title', 'Remove document title'),
            ('remove_subject', 'Subject', 'Remove document subject'),
        ]

        right_opts = [
            ('remove_timestamps', 'Timestamps', 'Reset creation/modification dates'),
            ('remove_timezone', 'Timezone', 'Remove timezone info (+02:00)'),
            ('remove_lang_tags', 'Language Tags', 'Remove Hebrew /Lang(he) tags'),
            ('remove_doc_id', 'Document ID', 'Zero the UUID identifier'),
            ('remove_xmp', 'XMP Metadata', 'Clear embedded XMP data'),
        ]

        for col, opts in [(left_col, left_opts), (right_col, right_opts)]:
            for key, label, desc in opts:
                self.create_option(col, key, label, desc)

        # Select All / None buttons
        btn_row = tk.Frame(options_card, bg=self.bg_card)
        btn_row.pack(fill=tk.X, pady=(10, 0))

        select_all = tk.Button(btn_row, text="Select All",
                              font=('Segoe UI', 9),
                              bg=self.bg_input, fg=self.text_primary,
                              activebackground=self.border,
                              relief='flat', padx=15, pady=5,
                              cursor='hand2',
                              command=self.select_all)
        select_all.pack(side=tk.LEFT)

        select_none = tk.Button(btn_row, text="Select None",
                               font=('Segoe UI', 9),
                               bg=self.bg_input, fg=self.text_primary,
                               activebackground=self.border,
                               relief='flat', padx=15, pady=5,
                               cursor='hand2',
                               command=self.select_none)
        select_none.pack(side=tk.LEFT, padx=(10, 0))

        # === PROGRESS SECTION ===
        progress_frame = tk.Frame(main, bg=self.bg_dark)
        progress_frame.pack(fill=tk.X, pady=(0, 10))

        self.progress_var = tk.DoubleVar()

        # Custom progress bar style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.Horizontal.TProgressbar",
                       background=self.accent,
                       troughcolor=self.bg_input,
                       borderwidth=0,
                       lightcolor=self.accent,
                       darkcolor=self.accent)

        self.progress_bar = ttk.Progressbar(progress_frame,
                                            variable=self.progress_var,
                                            maximum=100,
                                            style="Custom.Horizontal.TProgressbar",
                                            mode='determinate')
        self.progress_bar.pack(fill=tk.X)

        self.status_label = tk.Label(progress_frame, text="Ready",
                                    font=('Segoe UI', 9),
                                    bg=self.bg_dark, fg=self.text_secondary)
        self.status_label.pack(pady=(8, 0))

        # === SANITIZE BUTTON ===
        self.sanitize_btn = tk.Button(main, text="SANITIZE PDF",
                                     font=('Segoe UI', 12, 'bold'),
                                     bg=self.accent, fg='white',
                                     activebackground='#2ea043',
                                     relief='flat', pady=12,
                                     cursor='hand2',
                                     command=self.start_sanitization)
        self.sanitize_btn.pack(fill=tk.X, pady=(0, 12))

        # === RESULTS ===
        results_card = tk.Frame(main, bg=self.bg_card, padx=12, pady=10)
        results_card.pack(fill=tk.X, pady=(0, 10))

        results_header = tk.Label(results_card, text="RESULTS",
                                 font=('Segoe UI', 10, 'bold'),
                                 bg=self.bg_card, fg=self.accent)
        results_header.pack(anchor='w')

        self.results_text = tk.Text(results_card, height=6,
                                   font=('Consolas', 9),
                                   bg=self.bg_input, fg=self.text_primary,
                                   relief='flat', padx=8, pady=8,
                                   insertbackground=self.text_primary)
        self.results_text.pack(fill=tk.X, pady=(8, 0))
        self.results_text.insert('1.0', 'Select a PDF file and click SANITIZE PDF...')
        self.results_text.config(state=tk.DISABLED)

        # Select all by default
        self.select_all()

    def create_option(self, parent, key, label, description):
        """Create a styled checkbox option"""
        frame = tk.Frame(parent, bg=self.bg_card)
        frame.pack(fill=tk.X, pady=3)

        var = tk.BooleanVar(value=True)
        self.options_vars[key] = var

        cb = tk.Checkbutton(frame, text=label, variable=var,
                           font=('Segoe UI', 9),
                           bg=self.bg_card, fg=self.text_primary,
                           selectcolor=self.bg_input,
                           activebackground=self.bg_card,
                           activeforeground=self.text_primary,
                           cursor='hand2')
        cb.pack(anchor='w')

        desc = tk.Label(frame, text=description,
                       font=('Segoe UI', 8),
                       bg=self.bg_card, fg=self.text_secondary)
        desc.pack(anchor='w', padx=(20, 0))

    def select_all(self):
        for var in self.options_vars.values():
            var.set(True)

    def select_none(self):
        for var in self.options_vars.values():
            var.set(False)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select PDF to Sanitize",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            self.selected_file = file_path
            self.file_entry.config(state='normal')
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
            self.file_entry.config(state='readonly')
            self.status_label.config(text=f"File loaded: {os.path.basename(file_path)}", fg=self.text_secondary)

    def update_progress(self, value, status):
        self.progress_var.set(value)
        self.status_label.config(text=status)
        self.root.update_idletasks()

    def start_sanitization(self):
        if not self.selected_file:
            messagebox.showwarning("No File", "Please select a PDF file first.")
            return

        options = {key: var.get() for key, var in self.options_vars.items()}

        if not any(options.values()):
            messagebox.showwarning("No Options", "Please select at least one option.")
            return

        def run():
            try:
                self.sanitize_btn.config(state=tk.DISABLED, bg='#30363d')
                output_path, stats = self.sanitizer.sanitize_pdf(
                    self.selected_file,
                    options=options,
                    progress_callback=self.update_progress
                )

                # Show results
                self.results_text.config(state=tk.NORMAL)
                self.results_text.delete('1.0', tk.END)

                self.results_text.insert(tk.END, "SANITIZATION COMPLETE!\n")
                self.results_text.insert(tk.END, "=" * 45 + "\n\n")
                self.results_text.insert(tk.END, f"Output: {os.path.basename(output_path)}\n\n")

                changes = []
                if stats['author']: changes.append("Author removed")
                if stats['creator']: changes.append("Creator removed")
                if stats['producer']: changes.append("Producer removed")
                if stats['title']: changes.append("Title removed")
                if stats['subject']: changes.append("Subject removed")
                if stats['timestamps']: changes.append("Timestamps reset")
                if stats['timezone']: changes.append("Timezone removed")
                if stats['lang_tags']: changes.append(f"Language tags: {stats['lang_tags']} fixed")
                if stats['doc_id']: changes.append("Document ID zeroed")
                if stats['xmp']: changes.append("XMP metadata cleared")

                if changes:
                    self.results_text.insert(tk.END, "Changes:\n")
                    for c in changes:
                        self.results_text.insert(tk.END, f"  [OK] {c}\n")
                else:
                    self.results_text.insert(tk.END, "No changes needed.\n")

                self.results_text.config(state=tk.DISABLED)
                self.status_label.config(text="Complete!", fg='#3fb950')

                messagebox.showinfo("Success", f"Sanitized PDF saved to:\n{output_path}")

            except Exception as e:
                self.status_label.config(text="Error!", fg='#f85149')
                messagebox.showerror("Error", str(e))
            finally:
                self.sanitize_btn.config(state=tk.NORMAL, bg='#238636')

        threading.Thread(target=run, daemon=True).start()

    def run(self):
        self.root.mainloop()


def cli_mode(input_file):
    """Command line mode"""
    print("=" * 50)
    print("PDF Forensic Sanitizer")
    print("Created by Itay Naftali")
    print("=" * 50)
    print(f"\nProcessing: {input_file}")

    sanitizer = PDFSanitizer()

    def progress(val, msg):
        print(f"  [{int(val):3d}%] {msg}")

    try:
        output_path, stats = sanitizer.sanitize_pdf(input_file, progress_callback=progress)
        print(f"\n[OK] Success! Output: {output_path}")
    except Exception as e:
        print(f"\n[ERROR] {e}")

    print("\nPress Enter to exit...")
    input()


def main():
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        if os.path.exists(input_file) and input_file.lower().endswith('.pdf'):
            cli_mode(input_file)
            sys.exit(0)

    try:
        app = ModernGUI()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
