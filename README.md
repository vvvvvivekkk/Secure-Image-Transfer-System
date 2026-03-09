## Secure Image Transfer System using AES Encryption and Email

A desktop application written in Python that encrypts image files with AES‑256 before sending them via email, and decrypts received encrypted images locally. The GUI is built with `tkinter` and is designed to be clean, dark-themed, and user friendly.

---

### Features

- **AES‑256 image encryption** (CBC mode with PKCS7 padding)
- **Lossless image handling** by encrypting raw file bytes
- **Email sending** of encrypted `.enc` files via SMTP over SSL
- **Email receiving** of encrypted `.enc` attachments via IMAP
- **Key management** using SHA‑256 (password → 256‑bit key)
- **Modern dark-mode GUI** using `tkinter` and `ttk`
- **Status bar and progress indication**
- **Key generation and copy-to-clipboard**

---

### Project Structure

```text
secure-image-transfer/
├── main.py                # Application entry point
├── gui.py                 # Tkinter GUI
├── encryptor.py           # AES encryption logic
├── decryptor.py           # AES decryption wrapper
├── email_sender.py        # SMTP email sending
├── email_receiver.py      # IMAP email receiving
├── key_manager.py         # Key generation and SHA‑256 hashing
├── utils.py               # Logging, image validation helpers
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

---

### Installation

1. **Clone or copy the project**

   Place the project folder (e.g. `secure-image-transfer`) on your machine.

2. **Create and activate a virtual environment (recommended)**

   ```bash
   cd secure-image-transfer
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create your `.env` file**

  A sample file is included as `.env.example`.

  ```bash
  copy .env.example .env   # Windows
  # cp .env.example .env   # macOS/Linux
  ```

  Then set your actual values in `.env`:

  ```env
  SENDER_EMAIL=your_email@gmail.com
  SENDER_APP_PASSWORD=your_16_char_app_password
  RECEIVER_EMAIL=receiver@example.com   # optional
  ```

---

### Email Provider Notes

The app uses:

- `smtp.gmail.com:465` (SMTP over SSL) for sending
- `imap.gmail.com` for receiving

For Gmail you typically must:

- Enable **2‑step verification** on your Google account.
- Create an **App Password** and use that in the app instead of your normal password.

For other providers, you may need to adapt server settings in `email_sender.send_email` and `email_receiver.download_encrypted_files` (SMTP/IMAP hostnames and ports).

---

### Running the Application

1. Ensure your virtual environment is activated and dependencies installed.
2. From the project root, run:

   ```bash
   python main.py
   ```

3. The **Secure Image Transfer System** window will open.

---

### Using the Application

#### 1. Select Image

- Click **"Select Image..."**.
- Choose any supported image (`.png`, `.jpg`, `.jpeg`, `.bmp`, `.gif`, `.tiff`).
- The app validates the file using Pillow. Invalid files are rejected.

#### 2. Set or Generate Secret Key

- In **"Secret Key"**:
  - Enter a passphrase manually, or
  - Click **"Generate Strong Key"** to create a random 256‑bit key (base64 encoded).
- You can click **"Copy Key"** to place the current key into your clipboard.
- Internally, whatever you type is converted to a 256‑bit AES key using SHA‑256.

#### 3. Encrypt the Image

- Click **"Encrypt Selected Image"**.
- The app:
  - Reads the image file bytes.
  - Derives an AES‑256 key from your passphrase.
  - Generates a random IV.
  - Encrypts using AES‑CBC and writes `IV + ciphertext` to a `.enc` file next to the original image.
- On success you will see a confirmation dialog and the path to the encrypted file.

> The original image remains untouched; only the `.enc` file is sent/stored.

#### 4. Configure Email

- In **"Email Settings"**:
  - `Sender Email`: your email address (e.g. Gmail).
  - `Sender Password / App Password`: your email password or app password.
  - `Receiver Email`: the destination email address.
- You can toggle password visibility via the **"Show"** button.
- Click **"Save Email Settings (.env)"** to store these values for next launch.
- On startup, the app automatically loads saved email settings from `.env`.
- `Receiver Email` is optional in `.env` and can be changed any time before sending.

#### 5. Send Encrypted Image via Email

- After encrypting an image, click **"Send Encrypted Image via Email"**.
- The app attaches the `.enc` file and sends it using SMTP over SSL.
- On failure (authentication, network, etc.) a descriptive error dialog is shown.

#### 6. Check Email & Download `.enc` Files

- Provide the **email** and **password / app password** under **"Email Settings"**.
- Click **"Check Email & Download .enc Files"**.
- The app:
  - Connects to IMAP (`imap.gmail.com` by default).
  - Scans the `INBOX` for emails with `.enc` attachments.
  - Downloads these attachments into a `downloads/` directory.
- A dialog lists the downloaded filenames and locations.

#### 7. Decrypt an Encrypted File

- Click **"Decrypt Encrypted File"**.
- Choose a `.enc` file (e.g. from `downloads/`).
- Choose a save location and image filename for the decrypted output.
- The app:
  - Uses your current secret key (same passphrase used at encryption time).
  - Decrypts the file, removes padding, and writes the original bytes.
- If the key is incorrect or the file is corrupted, you get a clear error message.

> Because encryption is done at the raw-byte level, decrypted images are bit‑for‑bit identical to the originals as long as the correct key is used and the file is not corrupted.

---

### Security Details

- **Algorithm**: AES‑256 in **CBC** mode.
- **Key size**: 256 bits.
- **Key derivation**: SHA‑256 hash of the provided password/passphrase.
- **IV**: 16‑byte random IV generated for **each encryption**, stored at the start of the `.enc` file.
- **Padding**: PKCS7 on plaintext before encryption.
- **Image integrity**: Encryption operates on the original file bytes so no recompression or quality loss occurs.

Keep your passphrase/key secure and share it with recipients via a separate communication channel (not in the same email as the encrypted file).

---

### Error Handling

The application gracefully handles:

- Missing or invalid image files.
- Incorrect decryption keys (via padding verification errors).
- Email authentication failures.
- Network or connection errors to SMTP/IMAP servers.
- Missing or malformed attachments when receiving.

User-friendly dialogs provide clear descriptions of what went wrong and how to fix it (e.g. "The key may be incorrect or the file is corrupted").

---

### Development Notes

- **Encryption / Decryption**
  - Core logic lives in `encryptor.py` and is reused by `decryptor.py`.
  - The same PKCS7 logic and IV layout is used both ways to guarantee compatibility.

- **GUI**
  - Implemented in `gui.py` with a dark, card-based layout using `ttk` styles.
  - Long-running tasks (encryption, sending, IMAP checks, decryption) run in background threads so the UI remains responsive.

- **Logging**
  - `utils.setup_logging()` configures logging to both a file (`secure_image_transfer.log`) and the console.
  - You can adjust the log level or extend logging as needed.

---

### Running Tests / Verifying Round-Trip

To verify that encryption and decryption are lossless:

1. Pick an image `example.png`.
2. In the app:
   - Select the image.
   - Set a key (e.g. `my-test-key`).
   - Encrypt it.
3. Using a Python shell, compare the original and decrypted files:

   ```python
   with open("example.png", "rb") as f1, open("example.png.dec", "rb") as f2:
       print(f1.read() == f2.read())  # should print True
   ```

If they match, the system preserves image bytes perfectly.

