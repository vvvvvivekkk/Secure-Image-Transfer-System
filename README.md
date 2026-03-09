🔐 Secure Image Transfer System
AES-256 Encryption + Email Transmission

A Python desktop application that securely encrypts image files using AES-256 encryption before sending them via email. The receiver can download the encrypted file and decrypt it locally using the correct secret key.

The application features a modern dark-mode GUI built with Tkinter and ensures lossless image recovery after decryption.

🚀 Features

🔒 AES-256 Image Encryption
Encrypts image files using AES-256 (CBC mode) with secure PKCS7 padding.

🖼️ Lossless Image Handling
Encrypts raw image bytes, ensuring no quality loss after decryption.

📧 Secure Email Sending
Send encrypted .enc files via SMTP over SSL.

📥 Email Receiving Support
Download encrypted .enc attachments using IMAP email access.

🔑 Secure Key Management
User passwords are converted to 256-bit encryption keys using SHA-256 hashing.

🌙 Modern Dark-Mode GUI
Clean and intuitive interface built with Tkinter + ttk styles.

📊 Status & Progress Indicators
Displays encryption status and email transfer messages.

📋 Key Generation + Clipboard Support
Generate secure keys and copy them instantly.

📂 Project Structure
secure-image-transfer/
│
├── main.py                # 🚀 Application entry point
├── gui.py                 # 🖥️ Tkinter graphical interface
├── encryptor.py           # 🔐 AES encryption logic
├── decryptor.py           # 🔓 AES decryption logic
├── email_sender.py        # 📤 SMTP email sending
├── email_receiver.py      # 📥 IMAP email receiving
├── key_manager.py         # 🔑 Key generation & hashing
├── utils.py               # 🧰 Logging and validation helpers
├── requirements.txt       # 📦 Python dependencies
└── README.md              # 📘 Project documentation
⚙️ Installation
1️⃣ Clone or Download the Project

Download or clone the repository.

git clone https://github.com/vvvvvivekkk/Secure-Image-Transfer-System.git

Move into the project folder:

cd Secure-Image-Transfer-System
2️⃣ Create a Virtual Environment (Recommended)
python -m venv venv

Activate it:

Windows
venv\Scripts\activate
macOS / Linux
source venv/bin/activate
3️⃣ Install Required Libraries
pip install -r requirements.txt
4️⃣ Create .env Configuration File

Copy the example configuration:

Windows
copy .env.example .env
macOS / Linux
cp .env.example .env

Edit .env and add your email details:

SENDER_EMAIL=your_email@gmail.com
SENDER_APP_PASSWORD=your_16_char_app_password
RECEIVER_EMAIL=receiver@example.com
📧 Email Configuration

The system uses:

Service	Server	Port
SMTP	smtp.gmail.com	465
IMAP	imap.gmail.com	Default
🔑 Gmail Users (Important)

To use Gmail you must:

1️⃣ Enable 2-Step Verification

👉 https://myaccount.google.com/security

2️⃣ Generate an App Password

👉 https://myaccount.google.com/apppasswords

Use that password inside the application.

▶️ Running the Application

Activate the virtual environment and run:

python main.py

The Secure Image Transfer System GUI will open.

🧑‍💻 How to Use the Application
1️⃣ Select Image

Click:

Select Image

Supported formats:

PNG
JPG
JPEG
BMP
GIF
TIFF

The app validates the image automatically.

2️⃣ Set or Generate Secret Key

You can either:

✏️ Enter your own passphrase

OR

🔑 Click Generate Strong Key

You can also press Copy Key to copy it to the clipboard.

Internally:

password → SHA256 → AES-256 key
3️⃣ Encrypt the Image

Click:

Encrypt Selected Image

The application will:

1️⃣ Read image bytes
2️⃣ Generate a random IV
3️⃣ Encrypt using AES-256
4️⃣ Save encrypted file

Output example:

photo.jpg.enc

⚠️ The original image remains untouched.

4️⃣ Configure Email

Fill the following fields:

📧 Sender Email

your_email@gmail.com

🔐 App Password

gmail_app_password

📨 Receiver Email

friend@example.com

You can toggle password visibility with the Show button.

Press:

Save Email Settings

The values will be saved inside .env.

5️⃣ Send Encrypted Image

Click:

Send Encrypted Image via Email

The application will:

📎 Attach the .enc file
📤 Send it via SMTP SSL

Errors such as authentication failure or network issues are handled automatically.

6️⃣ Receive Encrypted Files

Click:

Check Email & Download Files

The system will:

1️⃣ Connect to IMAP
2️⃣ Search inbox for .enc files
3️⃣ Download attachments

Files will be saved to:

downloads/
7️⃣ Decrypt the Image

Click:

Decrypt Encrypted File

Select the .enc file and provide the same secret key used during encryption.

The system will restore the original image.

Example output:

photo_decrypted.jpg
🔐 Security Details
Feature	Description
Encryption Algorithm	AES-256
Mode	CBC
Key Derivation	SHA-256
IV	Random 16-byte IV
Padding	PKCS7

Encryption is performed on raw file bytes, ensuring bit-perfect recovery.

⚠️ Always share your secret key through a different communication channel.

⚠️ Error Handling

The application safely handles:

❌ Invalid image files
❌ Incorrect decryption keys
❌ Email authentication failures
❌ Network connectivity issues
❌ Missing attachments

Clear and user-friendly error messages are displayed.

🧠 Development Notes
Encryption & Decryption

Core encryption logic is implemented in:

encryptor.py
decryptor.py

Both modules share the same AES + padding implementation.

GUI

The GUI is built using:

tkinter
ttk

Features:

Dark theme

Card layout

Background threads for heavy tasks

Responsive interface

Logging

Logs are written to:

secure_image_transfer.log

This helps with debugging and monitoring application behavior.

🧪 Verify Encryption Integrity

To confirm lossless encryption, run this test:

with open("example.png", "rb") as f1, open("example.png.dec", "rb") as f2:
    print(f1.read() == f2.read())

Output should be:

True

This confirms the decrypted image is identical to the original.

⭐ Future Improvements

Possible enhancements:

🔐 Hybrid Encryption (AES + RSA)

☁️ Cloud storage support

📱 Mobile app version

📊 File transfer history dashboard

🔑 Automatic key exchange

👨‍💻 Author

Vivek Reddy

Cybersecurity & AI enthusiast building secure systems with Python.