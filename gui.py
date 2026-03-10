import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from decryptor import decrypt_image
from email_receiver import download_encrypted_files
from email_sender import send_email
from encryptor import encrypt_image
from env_config import load_email_settings, save_email_settings
from key_manager import generate_key, hash_key
from utils import is_valid_image, setup_logging


class SecureImageTransferGUI:
    """
    Tkinter-based GUI for the Secure Image Transfer System.
    """

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Secure Image Transfer System")
        self.root.geometry("980x640")
        self.root.minsize(900, 580)

        setup_logging()

        # State
        self.selected_image_path: str | None = None
        self.encrypted_file_path: str | None = None

        self._configure_style()
        self._build_layout()
        self._load_email_settings_from_env()

    # ----------------- Styling -----------------
    def _configure_style(self) -> None:
        self.style = ttk.Style()
        # Use a modern theme if available
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")

        # Dark mode palette
        bg = "#0f172a"
        surface = "#111827"
        accent = "#3b82f6"
        accent_hover = "#2563eb"
        text = "#e5e7eb"
        muted = "#9ca3af"

        self.root.configure(bg=bg)

        self.style.configure(
            "App.TFrame",
            background=bg,
        )
        self.style.configure(
            "Card.TFrame",
            background=surface,
            relief="flat",
            borderwidth=0,
        )
        self.style.configure(
            "TLabel",
            background=bg,
            foreground=text,
        )
        self.style.configure(
            "Card.TLabel",
            background=surface,
            foreground=text,
        )
        self.style.configure(
            "Muted.TLabel",
            background=surface,
            foreground=muted,
        )
        self.style.configure(
            "TEntry",
            fieldbackground="#020617",
            foreground=text,
            bordercolor="#020617",
        )
        self.style.map(
            "Accent.TButton",
            background=[("!disabled", accent), ("pressed", accent_hover), ("active", accent_hover)],
            foreground=[("!disabled", "white")],
        )
        self.style.configure(
            "Accent.TButton",
            padding=8,
            borderwidth=0,
            focusthickness=0,
        )
        self.style.configure(
            "TProgressbar",
            troughcolor="#020617",
            bordercolor="#020617",
            background=accent,
        )

    # ----------------- Layout -----------------
    def _build_layout(self) -> None:
        main = ttk.Frame(self.root, style="App.TFrame", padding=20)
        main.pack(fill="both", expand=True)

        header = ttk.Frame(main, style="App.TFrame")
        header.pack(fill="x", pady=(0, 20))

        title = ttk.Label(
            header,
            text="Secure Image Transfer System",
            font=("Segoe UI", 20, "bold"),
        )
        title.pack(anchor="w")

        subtitle = ttk.Label(
            header,
            text="Encrypt images with AES-256 and send them securely via email.",
            style="Muted.TLabel",
            font=("Segoe UI", 10),
        )
        subtitle.pack(anchor="w", pady=(4, 0))

        content = ttk.Frame(main, style="App.TFrame")
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)

        # Left: File + Key
        left = ttk.Frame(content, style="App.TFrame")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self._build_file_card(left)
        self._build_key_card(left)

        # Right: Email + Actions
        right = ttk.Frame(content, style="App.TFrame")
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self._build_email_card(right)
        self._build_actions_card(right)

        # Bottom: Status
        status_frame = ttk.Frame(main, style="App.TFrame")
        status_frame.pack(fill="x", pady=(16, 0))

        self.progress = ttk.Progressbar(status_frame, mode="determinate")
        self.progress.pack(fill="x")

        self.status_label = ttk.Label(
            status_frame,
            text="Ready.",
            style="Muted.TLabel",
            font=("Segoe UI", 9),
        )
        self.status_label.pack(anchor="w", pady=(4, 0))

    def _build_file_card(self, parent: ttk.Frame) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=16)
        card.pack(fill="x", pady=(0, 12))

        title = ttk.Label(card, text="Image File", style="Card.TLabel", font=("Segoe UI", 12, "bold"))
        title.grid(row=0, column=0, sticky="w")

        self.image_label = ttk.Label(
            card,
            text="No image selected.",
            style="Muted.TLabel",
            font=("Segoe UI", 9),
        )
        self.image_label.grid(row=1, column=0, sticky="w", pady=(4, 8))

        select_btn = ttk.Button(
            card,
            text="Select Image...",
            style="Accent.TButton",
            command=self.on_select_image,
        )
        select_btn.grid(row=2, column=0, sticky="w")

    def _build_key_card(self, parent: ttk.Frame) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=16)
        card.pack(fill="x", pady=(0, 12))

        title = ttk.Label(card, text="Secret Key", style="Card.TLabel", font=("Segoe UI", 12, "bold"))
        title.grid(row=0, column=0, columnspan=3, sticky="w")

        key_label = ttk.Label(card, text="Passphrase / Key:", style="Card.TLabel")
        key_label.grid(row=1, column=0, sticky="w", pady=(10, 4))

        self.key_var = tk.StringVar()
        key_entry = ttk.Entry(card, textvariable=self.key_var, width=40, show="•")
        key_entry.grid(row=2, column=0, columnspan=2, sticky="we")

        toggle_btn = ttk.Button(
            card,
            text="Show",
            command=lambda e=key_entry: self._toggle_password_visibility(e),
        )
        toggle_btn.grid(row=2, column=2, padx=(8, 0))

        gen_btn = ttk.Button(
            card,
            text="Generate Strong Key",
            style="Accent.TButton",
            command=self.on_generate_key,
        )
        gen_btn.grid(row=3, column=0, sticky="w", pady=(10, 0))

        copy_btn = ttk.Button(
            card,
            text="Copy Key",
            command=self.on_copy_key,
        )
        copy_btn.grid(row=3, column=1, sticky="w", padx=(8, 0), pady=(10, 0))

        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=0)
        card.columnconfigure(2, weight=0)

    def _build_email_card(self, parent: ttk.Frame) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=16)
        card.pack(fill="x", pady=(0, 12))

        title = ttk.Label(card, text="Email Settings", style="Card.TLabel", font=("Segoe UI", 12, "bold"))
        title.grid(row=0, column=0, columnspan=2, sticky="w")

        helper = ttk.Label(
            card,
            text="Tip: Save once, then the app auto-fills these fields from .env next time.",
            style="Muted.TLabel",
            font=("Segoe UI", 9),
        )
        helper.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 8))

        sender_label = ttk.Label(card, text="Sender Email:", style="Card.TLabel")
        sender_label.grid(row=2, column=0, sticky="w", pady=(2, 2))
        self.sender_email_var = tk.StringVar()
        sender_entry = ttk.Entry(card, textvariable=self.sender_email_var, width=40)
        sender_entry.grid(row=2, column=1, sticky="we", pady=(2, 2))

        pwd_label = ttk.Label(card, text="Sender Password / App Password:", style="Card.TLabel")
        pwd_label.grid(row=3, column=0, sticky="w", pady=(4, 2))
        self.sender_pwd_var = tk.StringVar()
        self.sender_pwd_entry = ttk.Entry(card, textvariable=self.sender_pwd_var, show="•")
        self.sender_pwd_entry.grid(row=3, column=1, sticky="we", pady=(4, 2))

        toggle_pwd_btn = ttk.Button(
            card,
            text="Show",
            command=lambda e=self.sender_pwd_entry: self._toggle_password_visibility(e),
        )
        toggle_pwd_btn.grid(row=3, column=2, padx=(8, 0))

        recv_label = ttk.Label(card, text="Receiver Email:", style="Card.TLabel")
        recv_label.grid(row=4, column=0, sticky="w", pady=(4, 2))
        self.receiver_email_var = tk.StringVar()
        recv_entry = ttk.Entry(card, textvariable=self.receiver_email_var)
        recv_entry.grid(row=4, column=1, sticky="we", pady=(4, 2))

        save_settings_btn = ttk.Button(
            card,
            text="Save Email Settings (.env)",
            command=self.on_save_email_settings,
        )
        save_settings_btn.grid(row=5, column=0, columnspan=2, sticky="w", pady=(10, 0))

        card.columnconfigure(1, weight=1)

    def _build_actions_card(self, parent: ttk.Frame) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=16)
        card.pack(fill="both", expand=True)

        title = ttk.Label(card, text="Actions", style="Card.TLabel", font=("Segoe UI", 12, "bold"))
        title.grid(row=0, column=0, columnspan=2, sticky="w")

        guide = ttk.Label(
            card,
            text="Flow: 1) Select + Encrypt  2) Save Email Settings  3) Send / Download / Decrypt",
            style="Muted.TLabel",
            font=("Segoe UI", 9),
        )
        guide.grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 10))

        encrypt_btn = ttk.Button(
            card,
            text="Encrypt Selected Image",
            style="Accent.TButton",
            command=self.on_encrypt_image,
        )
        encrypt_btn.grid(row=2, column=0, sticky="we", pady=(2, 4), columnspan=2)

        send_btn = ttk.Button(
            card,
            text="Send Encrypted Image via Email",
            command=self.on_send_email,
        )
        send_btn.grid(row=3, column=0, sticky="we", pady=4, columnspan=2)

        download_btn = ttk.Button(
            card,
            text="Check Email & Download .enc Files",
            command=self.on_check_email,
        )
        download_btn.grid(row=4, column=0, sticky="we", pady=4, columnspan=2)

        decrypt_btn = ttk.Button(
            card,
            text="Decrypt Encrypted File",
            style="Accent.TButton",
            command=self.on_decrypt_image,
        )
        decrypt_btn.grid(row=5, column=0, sticky="we", pady=(12, 0), columnspan=2)

        card.rowconfigure(6, weight=1)
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)

    def _load_email_settings_from_env(self) -> None:
        settings = load_email_settings()
        self.sender_email_var.set(settings.get("SENDER_EMAIL", ""))
        self.sender_pwd_var.set(settings.get("SENDER_APP_PASSWORD", ""))
        self.receiver_email_var.set(settings.get("RECEIVER_EMAIL", ""))
        if any(settings.values()):
            self._set_status("Loaded email settings from .env", 0)

    # ----------------- Helpers -----------------
    def _toggle_password_visibility(self, entry: ttk.Entry) -> None:
        current = entry.cget("show")
        entry.configure(show="" if current else "•")

    def _set_status(self, text: str, progress: int | None = None) -> None:
        self.status_label.config(text=text)
        if progress is not None:
            self.progress["value"] = progress
        self.root.update_idletasks()

    # ----------------- Event Handlers -----------------
    def on_select_image(self) -> None:
        path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        if not is_valid_image(path):
            messagebox.showerror("Invalid Image", "The selected file is not a valid image.")
            return
        self.selected_image_path = path
        self.image_label.config(text=os.path.basename(path))
        self._set_status(f"Selected image: {os.path.basename(path)}", 0)

    def on_generate_key(self) -> None:
        key = generate_key()
        self.key_var.set(key)
        self._set_status("Generated a new strong key.", 0)

    def on_copy_key(self) -> None:
        key = self.key_var.get().strip()
        if not key:
            messagebox.showwarning("No Key", "There is no key to copy.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(key)
        self._set_status("Key copied to clipboard.", 0)

    def _get_aes_key(self) -> bytes | None:
        password = self.key_var.get().strip()
        if not password:
            messagebox.showerror("Missing Key", "Please provide a secret key or generate one first.")
            return None
        return hash_key(password)

    def on_save_email_settings(self) -> None:
        sender = self.sender_email_var.get().strip()
        pwd = self.sender_pwd_var.get().strip()
        receiver = self.receiver_email_var.get().strip()

        if not sender or not pwd:
            messagebox.showerror(
                "Missing Fields",
                "Please provide sender email and app password before saving.",
            )
            return

        try:
            save_email_settings(
                {
                    "SENDER_EMAIL": sender,
                    "SENDER_APP_PASSWORD": pwd,
                    "RECEIVER_EMAIL": receiver,
                }
            )
            self._set_status("Email settings saved to .env", 0)
            messagebox.showinfo(
                "Saved",
                "Email settings saved to .env. Receiver email is optional and can be changed per send.",
            )
        except Exception as exc:
            messagebox.showerror("Save Error", f"Could not save .env settings.\n\nDetails: {exc}")

    def on_encrypt_image(self) -> None:
        if not self.selected_image_path:
            messagebox.showerror("No Image", "Please select an image to encrypt.")
            return
        key = self._get_aes_key()
        if key is None:
            return

        def task() -> None:
            try:
                self._set_status("Encrypting image...", 20)
                enc_path = encrypt_image(self.selected_image_path, key)
                self.encrypted_file_path = enc_path
                self._set_status("Image encrypted successfully.", 100)
                messagebox.showinfo("Success", f"Encrypted file created:\n{enc_path}")
            except Exception as exc:
                self._set_status("Encryption failed.", 0)
                messagebox.showerror("Encryption Error", str(exc))
            finally:
                self.progress["value"] = 0

        threading.Thread(target=task, daemon=True).start()

    def on_send_email(self) -> None:
        if not self.encrypted_file_path:
            messagebox.showerror(
                "No Encrypted File",
                "Please encrypt an image first. The encrypted file will then be sent.",
            )
            return

        sender = self.sender_email_var.get().strip()
        pwd = self.sender_pwd_var.get().strip()
        receiver = self.receiver_email_var.get().strip()

        if not sender or not pwd or not receiver:
            messagebox.showerror("Missing Fields", "Please provide sender email, password, and receiver email.")
            return

        def task() -> None:
            try:
                self._set_status("Sending email with encrypted attachment...", 40)
                send_email(sender, pwd, receiver, self.encrypted_file_path)
                self._set_status("Encrypted image sent successfully.", 100)
                messagebox.showinfo("Email Sent", "Encrypted image email was sent successfully.")
            except Exception as exc:
                self._set_status("Failed to send email.", 0)
                messagebox.showerror("Email Error", str(exc))
            finally:
                self.progress["value"] = 0

        threading.Thread(target=task, daemon=True).start()

    def on_check_email(self) -> None:
        user = self.sender_email_var.get().strip()
        pwd = self.sender_pwd_var.get().strip()
        if not user or not pwd:
            messagebox.showerror(
                "Missing Credentials",
                "Please provide the email and password to check for encrypted attachments.",
            )
            return

        def task() -> None:
            try:
                self._set_status("Checking email for encrypted attachments...", 30)
                attachments = download_encrypted_files(
                    user,
                    pwd,
                    max_messages=100,
                    timeout_seconds=30,
                )
                if not attachments:
                    self._set_status("No encrypted attachments found.", 0)
                    messagebox.showinfo("No Files", "No .enc attachments were found in your inbox.")
                    return
                self._set_status("Downloaded encrypted attachments.", 100)
                msg = "\n".join(f"{name} -> {path}" for name, path in attachments)
                messagebox.showinfo("Downloaded Files", f"The following files were downloaded:\n\n{msg}")
            except Exception as exc:
                self._set_status("Failed to download attachments.", 0)
                messagebox.showerror("Email Error", str(exc))
            finally:
                self.progress["value"] = 0

        threading.Thread(target=task, daemon=True).start()

    def on_decrypt_image(self) -> None:
        key = self._get_aes_key()
        if key is None:
            return

        enc_path = filedialog.askopenfilename(
            title="Select Encrypted File (.enc)",
            filetypes=[("Encrypted files", "*.enc"), ("All files", "*.*")],
        )
        if not enc_path:
            return

        default_output = os.path.splitext(enc_path)[0]
        suggested_ext = os.path.splitext(default_output)[1].lower() or ".png"
        out_path = filedialog.asksaveasfilename(
            title="Save Decrypted Image As",
            initialfile=os.path.basename(default_output),
            defaultextension=suggested_ext,
            filetypes=[
                ("Original Image Type", f"*{suggested_ext}"),
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg *.jpeg"),
                ("All Files", "*.*"),
            ],
        )
        if not out_path:
            return

        def task() -> None:
            try:
                self._set_status("Decrypting image...", 50)
                saved_path = decrypt_image(enc_path, key, out_path)
                self._set_status("Image decrypted successfully.", 100)
                messagebox.showinfo("Success", f"Decrypted image saved to:\n{saved_path}")
            except ValueError as exc:
                # Likely padding / key mismatch
                self._set_status("Decryption failed.", 0)
                messagebox.showerror(
                    "Decryption Error",
                    f"Decryption failed. The key may be incorrect or the file is corrupted.\n\nDetails: {exc}",
                )
            except Exception as exc:
                self._set_status("Decryption failed.", 0)
                messagebox.showerror("Decryption Error", str(exc))
            finally:
                self.progress["value"] = 0

        threading.Thread(target=task, daemon=True).start()


def run_gui() -> None:
    root = tk.Tk()
    app = SecureImageTransferGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()

