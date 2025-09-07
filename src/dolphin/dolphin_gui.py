#!/usr/bin/env python3
"""
Dolphin-Mistral GUI Interface
Simple graphical interface for the uncensored model
"""

import tkinter as tk
from tkinter import scrolledtext, ttk
import subprocess
import threading
import queue
import sys


class DolphinGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Dolphin-Mistral Security Assistant")
        self.window.geometry("800x600")
        
        # Queue for thread communication
        self.response_queue = queue.Queue()
        
        # Setup UI
        self.setup_ui()
        
        # Check if Ollama is available
        self.check_ollama()
        
    def setup_ui(self):
        """Create the user interface"""
        # Header
        header = tk.Frame(self.window, bg="#2c3e50", height=60)
        header.pack(fill=tk.X)
        
        title = tk.Label(header, text="🐬 Dolphin-Mistral Security Assistant",
                        font=("Arial", 16, "bold"), fg="white", bg="#2c3e50")
        title.pack(pady=15)
        
        # Warning label
        warning = tk.Label(self.window, text="⚠️ Uncensored Model - Use Responsibly and Legally",
                          font=("Arial", 10), fg="red")
        warning.pack(pady=5)
        
        # Main content area
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Output area
        output_label = tk.Label(main_frame, text="Response:", font=("Arial", 10, "bold"))
        output_label.pack(anchor=tk.W)
        
        self.output_text = scrolledtext.ScrolledText(main_frame, height=20, wrap=tk.WORD,
                                                     font=("Consolas", 10))
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Input area
        input_frame = tk.Frame(self.window)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        input_label = tk.Label(input_frame, text="Your Question:", font=("Arial", 10, "bold"))
        input_label.pack(anchor=tk.W)
        
        self.input_text = tk.Text(input_frame, height=4, font=("Consolas", 10))
        self.input_text.pack(fill=tk.X, pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)
        
        self.send_button = tk.Button(button_frame, text="Send Query", command=self.send_query,
                                     bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                                     padx=20, pady=5)
        self.send_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = tk.Button(button_frame, text="Clear", command=self.clear_all,
                                bg="#95a5a6", fg="white", font=("Arial", 10),
                                padx=20, pady=5)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Example queries dropdown
        example_frame = tk.Frame(self.window)
        example_frame.pack(pady=5)
        
        tk.Label(example_frame, text="Examples:").pack(side=tk.LEFT, padx=5)
        
        self.examples = [
            "How does SQL injection work?",
            "Explain buffer overflow exploitation",
            "How to test for XSS vulnerabilities",
            "Explain reverse engineering techniques",
            "How to perform penetration testing",
            "What are common web vulnerabilities?",
            "How to analyze malware safely",
            "Explain privilege escalation methods"
        ]
        
        self.example_var = tk.StringVar()
        self.example_dropdown = ttk.Combobox(example_frame, textvariable=self.example_var,
                                            values=self.examples, width=50)
        self.example_dropdown.pack(side=tk.LEFT, padx=5)
        self.example_dropdown.bind("<<ComboboxSelected>>", self.load_example)
        
        # Status bar
        self.status_bar = tk.Label(self.window, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind Enter key to send
        self.input_text.bind("<Control-Return>", lambda e: self.send_query())
        
    def check_ollama(self):
        """Check if Ollama and Dolphin are available"""
        try:
            # Check Ollama
            result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                self.output_text.insert(tk.END, "❌ Ollama not found! Please install Ollama first.\n")
                self.send_button.config(state=tk.DISABLED)
                return
            
            # Check for Dolphin model
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if 'dolphin-mistral' not in result.stdout:
                self.output_text.insert(tk.END, "⚠️ Dolphin-Mistral not found!\n")
                self.output_text.insert(tk.END, "Installing... Run: ollama pull dolphin-mistral\n")
                self.send_button.config(state=tk.DISABLED)
                return
                
            self.output_text.insert(tk.END, "✅ Dolphin-Mistral is ready!\n")
            self.output_text.insert(tk.END, "-" * 60 + "\n")
            self.output_text.insert(tk.END, "Type your security questions below and click 'Send Query'\n")
            self.output_text.insert(tk.END, "Remember: This is an uncensored model - use responsibly!\n")
            self.output_text.insert(tk.END, "-" * 60 + "\n\n")
            
        except Exception as e:
            self.output_text.insert(tk.END, f"❌ Error: {e}\n")
            self.send_button.config(state=tk.DISABLED)
    
    def load_example(self, event=None):
        """Load example query into input"""
        example = self.example_var.get()
        self.input_text.delete(1.0, tk.END)
        self.input_text.insert(1.0, example)
    
    def send_query(self):
        """Send query to Dolphin model"""
        query = self.input_text.get(1.0, tk.END).strip()
        
        if not query:
            return
        
        # Update UI
        self.output_text.insert(tk.END, f"\n📤 Query: {query}\n")
        self.output_text.insert(tk.END, "-" * 60 + "\n")
        self.output_text.see(tk.END)
        
        self.send_button.config(state=tk.DISABLED, text="Processing...")
        self.status_bar.config(text="Processing query...")
        
        # Run in thread to avoid freezing UI
        thread = threading.Thread(target=self.run_query, args=(query,))
        thread.daemon = True
        thread.start()
        
        # Check for response
        self.window.after(100, self.check_response)
    
    def run_query(self, query):
        """Run the query in a separate thread"""
        try:
            result = subprocess.run(
                ['ollama', 'run', 'dolphin-mistral', query],
                capture_output=True,
                text=True,
                timeout=60
            )
            self.response_queue.put(('success', result.stdout))
        except subprocess.TimeoutExpired:
            self.response_queue.put(('error', 'Query timed out. Try a simpler question.'))
        except Exception as e:
            self.response_queue.put(('error', str(e)))
    
    def check_response(self):
        """Check for response from thread"""
        try:
            status, response = self.response_queue.get_nowait()
            
            if status == 'success':
                self.output_text.insert(tk.END, "🤖 Response:\n")
                self.output_text.insert(tk.END, response)
                self.output_text.insert(tk.END, "\n" + "=" * 60 + "\n")
            else:
                self.output_text.insert(tk.END, f"❌ Error: {response}\n")
            
            self.output_text.see(tk.END)
            self.send_button.config(state=tk.NORMAL, text="Send Query")
            self.status_bar.config(text="Ready")
            
        except queue.Empty:
            # Still processing, check again
            self.window.after(100, self.check_response)
    
    def clear_all(self):
        """Clear all text fields"""
        self.input_text.delete(1.0, tk.END)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "✅ Cleared. Ready for new query.\n\n")
    
    def run(self):
        """Start the GUI"""
        self.window.mainloop()


def main():
    """Main entry point"""
    gui = DolphinGUI()
    gui.run()


if __name__ == "__main__":
    main()