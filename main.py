import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar, Label, Canvas
from PyPDF2 import PdfMerger
import os

class PDFMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Merger (Drag & Drop Edition)")
        self.pdf_files = []
        self.root.iconbitmap('pdf-file.ico')

        self.listbox = Listbox(root, selectmode=tk.SINGLE, width=50)
        self.listbox.pack(pady=(10, 0), fill=tk.X)

        scrollbar = Scrollbar(root, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Drop position indicator (red line between items)
        self.indicator = Canvas(root, width=300, height=4, bg=root.cget("bg"), highlightthickness=0)
        self.indicator.create_line(5, 2, 295, 2, fill="red", width=2)
        self.indicator.place_forget()

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add PDFs", command=self.add_pdfs).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Remove Selected", command=self.remove_selected).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Merge PDFs", command=self.merge_pdfs).grid(row=0, column=2, padx=5)

        # Drag-and-drop setup
        self.drag_data = {"index": None, "label": None}
        self.listbox.bind("<ButtonPress-1>", self.start_drag)
        self.listbox.bind("<B1-Motion>", self.do_drag)
        self.listbox.bind("<ButtonRelease-1>", self.stop_drag)

        # Empty space click to clear selection
        self.listbox.bind("<Button-1>", self.clear_selection, add='+')

    def add_pdfs(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        for f in files:
            if f not in self.pdf_files:
                self.pdf_files.append(f)
                self.listbox.insert(tk.END, os.path.basename(f))

    def remove_selected(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            self.listbox.delete(index)
            del self.pdf_files[index]

    def start_drag(self, event):
        index = self.listbox.nearest(event.y)
        bbox = self.listbox.bbox(index)

        if not bbox or event.y < bbox[1] or event.y > bbox[1] + bbox[3]:
            self.drag_data["index"] = None
            return

        self.drag_data["index"] = index
        item_text = self.listbox.get(index)
        self.drag_data["label"] = Label(self.root, text=item_text, relief="solid", bg="lightgray")
        self.drag_data["label"].place(x=event.x_root - self.root.winfo_rootx(),
                                      y=event.y_root - self.root.winfo_rooty())

    def do_drag(self, event):
        if self.drag_data["label"]:
            x = event.x_root - self.root.winfo_rootx()
            y = event.y_root - self.root.winfo_rooty()
            self.drag_data["label"].place(x=x, y=y)

            drop_index = self.listbox.nearest(event.y)
            bbox = self.listbox.bbox(drop_index)
            if bbox:
                row_height = bbox[3]
                midpoint = bbox[1] + row_height // 2
                if event.y > midpoint:
                    drop_index += 1
                if drop_index > len(self.pdf_files):
                    drop_index = len(self.pdf_files)

                self.drag_data["drop_index"] = drop_index

                y_pos = bbox[1] + row_height + self.listbox.winfo_y() if event.y > midpoint else bbox[1] + self.listbox.winfo_y()
                self.indicator.place(x=10, y=y_pos)
            else:
                self.indicator.place_forget()

    def stop_drag(self, event):
        if not self.drag_data["label"]:
            return

        drag_index = self.drag_data["index"]
        drop_index = self.drag_data.get("drop_index", drag_index)

        if drop_index > drag_index:
            drop_index -= 1

        if drop_index != drag_index:
            item = self.pdf_files.pop(drag_index)
            self.pdf_files.insert(drop_index, item)

        self.refresh_list()
        self.listbox.selection_set(drop_index)

        # Cleanup
        self.drag_data["label"].destroy()
        self.indicator.place_forget()
        self.drag_data = {"index": None, "label": None}

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for f in self.pdf_files:
            self.listbox.insert(tk.END, os.path.basename(f))

    def clear_selection(self, event):
        index = self.listbox.nearest(event.y)
        bbox = self.listbox.bbox(index)
        if not bbox or event.y < bbox[1] or event.y > bbox[1] + bbox[3]:
            self.listbox.selection_clear(0, tk.END)

    def merge_pdfs(self):
        if not self.pdf_files:
            messagebox.showwarning("No Files", "Add at least two PDFs to merge.")
            return

        output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if output_path:
            merger = PdfMerger()
            try:
                for pdf in self.pdf_files:
                    merger.append(pdf)
                merger.write(output_path)
                merger.close()
                messagebox.showinfo("Success", f"PDFs merged and saved to:\n{output_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to merge PDFs:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFMergerApp(root)
    root.mainloop()
