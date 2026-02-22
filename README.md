# 🖱️✨ Mimikey 

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10-pink.svg?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/Platform-macOS%20%7C%20Windows-blue.svg?style=for-the-badge">
</div>

> **A cozy, open-source, and hyper-realistic human typing simulator.** 🎀

Mimikey is a premium desktop application designed to bypass detection by perfectly simulating human keystrokes. Whether you are pasting a long essay or a quick paragraph, Mimikey types it out for you with realistic delays, natural typos, and self-correcting behavior. 

Forget clunky, robotic macro scripts. Mimikey feels alive, looks beautiful, and sits quietly on your screen. ☁️

---

### 📸 Preview
*(Drop an animated GIF of Mimikey typing here! Just drag and drop the `.gif` file into this GitHub editor and it will generate the link)*

---

## 🕵️‍♂️ The "Not a Keylogger" Transparency Note
Let's address the elephant in the room: **Mimikey requires low-level keyboard permissions.** Because this app uses global hotkeys (allowing you to pause/start the typing even when the app is minimized), it requires system-level keyboard monitoring. **Mimikey does not log, save, or transmit your keystrokes.** The code is completely open-source so you can verify exactly how your data is handled. 

### 🛡️ Required OS Permissions
To run this script, your operating system will ask for the following:
* **🍎 macOS:** You must grant your Terminal (or VS Code) **Accessibility** and **Input Monitoring** permissions in `System Settings > Privacy & Security`. This allows the script to physically simulate pressing the keys and listen for the emergency stop hotkey.
* **🪟 Windows:** You may need to run your command prompt as **Administrator** so the script can interface with the Windows keyboard API without being blocked by Windows Defender.

---

## 🌸 Features
* **🧠 Smart Humanization Engine:** Simulates realistic delays based on punctuation, key travel distance, and fatigue.
* **Oops... Typos:** Occasionally hits the wrong adjacent key and physically navigates back to fix it.
* **🎯 Perfectionism Slider:** Decide if the bot catches 100% of its mistakes, or if it intentionally leaves a few behind.
* **💻 Live Action Terminal:** Watch the bot's internal monologue in real-time as it thinks, wanders, and fixes errors.
* **🎨 6 Aesthetic Themes:** Boots up in *Cotton Candy* default, with options like *Dracula*, *Matrix*, and *Cyber*.

---

## 🚀 Installation & Setup

Since Mimikey interacts heavily with your OS, it is distributed as a raw Python script so you can verify the source code.

**1. Clone the repository**
```bash
git clone https://github.com/vex-codes/Mimikey.git
cd mimikey
