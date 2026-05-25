import customtkinter as ctk
import kdl
import os
import re
from typing import Dict, List, Optional, Tuple

# Set UI styling parameters
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

STORAGE_FILE = os.path.join(os.path.expanduser("~"), ".site7research_custom_kdl.txt")

VALID_ERROR_MODES = ["strict", "ignore", "replace", "space", "xmlchainreplace", "unicodereplace"]

DEFAULT_KDL = r"""
config {
    errors "replace"
    unicode_questionmark false
}

content {
    entry letter=1 {
        original "A"
        code_a r"\o"
        code_b r"\o"
        code_c r"/\o"
    }
    entry letter=2 {
        original "B"
        code_a null
        code_b r"\\o"
        code_c r"/\\o"
    }
    entry letter=3 {
        original "C"
        code_a null
        code_b r"/\\"
        code_c r"/\\\o"
    }
    entry letter=4 {
        original "D"
        code_a r"/\"
        code_b r"/\"
        code_c r"/\\\\o"
    }
    entry letter=5 {
        original "E"
        code_a r"/"
        code_b r"/"
        code_c r"//\\\"
    }
    entry letter=6 {
        original "F"
        code_a null
        code_b r"/\o"
        code_c r"//\\"
    }
    entry letter=7 {
        original "G"
        code_a null
        code_b r"/\\o"
        code_c r"//\"
    }
    entry letter=8 {
        original "H"
        code_a r"//\\" r"///\"
        code_b r"//\\"
        code_c r"//"
    }
    entry letter=9 {
        original "I"
        code_a null
        code_b r"//\"
        code_c r"//\o"
    }
    entry letter=10 {
        original "J"
        code_a null
        code_b r"//"
        code_c r"//\\o"
    }
    entry letter=11 {
        original "K"
        code_a null
        code_b r"//\o"
        code_c r"//\\\o"
    }
    entry letter=12 {
        original "L"
        code_a null
        code_b r"//\\o"
        code_c r"//\\\\o"
    }
    entry letter=13 {
        original "M"
        code_a null
        code_b r"///\\"
        code_c r"///\\\"
    }
    entry letter=14 {
        original "N"
        code_a null
        code_b r"///\"
        code_c r"///\\"
    }
    entry letter=15 {
        original "O"
        code_a r"///\"
        code_b r"///"
        code_c r"///\"
    }
    entry letter=16 {
        original "P"
        code_a null
        code_b r"///\o"
        code_c r"///"
    }
    entry letter=17 {
        original "Q"
        code_a null
        code_b r"///\\o"
        code_c r"///\o"
    }
    entry letter=18 {
        original "R"
        code_a r"///\\o" r"/\\o"
        code_b r"////\\"
        code_c r"///\\o"
    }
    entry letter=19 {
        original "S"
        code_a null
        code_b r"////\"
        code_c r"///\\\o"
    }
    entry letter=20 {
        original "T"
        code_a r"///\\"
        code_b r"////"
        code_c r"///\\\\o"
    }
    entry letter=21 {
        original "U"
        code_a null
        code_b r"////\o"
        code_c r"////\\\"
    }
    entry letter=22 {
        original "V"
        code_a null
        code_b r"////\\o"
        code_c r"////\\"
    }
    entry letter=23 {
        original "W"
        code_a null
        code_b r"/////\\"
        code_c r"////\"
    }
    entry letter=24 {
        original "X"
        code_a null
        code_b r"/////\"
        code_c r"////"
    }
    entry letter=25 {
        original "Y"
        code_a r"/////\o"
        code_b r"/////"
        code_c r"////\o"
    }
    entry letter=26 {
        original "Z"
        code_a null
        code_b r"/////\o"
        code_c r"////\\o"
    }
}
"""


class Site7DesktopApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Site-7 Research Decoder")
        self.geometry("860x700")
        self.resizable(False, False)

        self.encrypt_map: Dict[str, dict] = {}
        self.decrypt_map: Dict[str, Dict[str, str]] = {"code_a": {}, "code_b": {}, "code_c": {}}
        self.app_config: Dict[str, object] = {"errors": "replace", "unicode_questionmark": False}

        # Title Label
        self.title_label = ctk.CTkLabel(
            self,
            text="SITE-7 CONTAINMENT MONITOR",
            font=ctk.CTkFont(family="Courier", size=24, weight="bold"),
            text_color="#2ECC71"
        )
        self.title_label.pack(pady=(20, 10))

        # Main Tabview component
        self.tabview = ctk.CTkTabview(self, width=820, height=580)
        self.tabview.pack(pady=10)

        self.tab_trans = self.tabview.add("TRANSLATOR")
        self.tab_import = self.tabview.add("IMPORT TABLE")
        self.tab_credits = self.tabview.add("PROJECT FILES & CREDITS")

        self.setup_translator_tab()
        self.setup_import_tab()
        self.setup_credits_tab()

        self.init_tables()

    # ── KDL Parsing ──────────────────────────────────────────────

    def parse_kdl(self, kdl_text: str) -> Tuple[bool, str, dict, dict, dict]:
        """Parse KDL text. Returns (success, error_msg, encrypt_map, decrypt_map, config)."""
        new_encrypt = {}
        new_decrypt = {"code_a": {}, "code_b": {}, "code_c": {}}
        new_config = {}
        error_msg = ""

        try:
            doc = kdl.parse(kdl_text)
        except Exception as e:
            return False, f"KDL parse error: {e}", {}, {"code_a": {}, "code_b": {}, "code_c": {}}, {}

        # Parse config { ... }
        config_node = next((n for n in doc if n.name == "config"), None)
        if config_node:
            for child in config_node.children:
                if child.name == "errors" and child.args:
                    val = str(child.args[0])
                    if val in VALID_ERROR_MODES:
                        new_config["errors"] = val
                    else:
                        error_msg = f'Invalid config.errors="{val}". Valid: {", ".join(VALID_ERROR_MODES)}'
            # Parse unicode_questionmark
            for child in config_node.children:
                if child.name == "unicode_questionmark" and child.args:
                    val = child.args[0]
                    if isinstance(val, bool):
                        new_config["unicode_questionmark"] = val
                    elif isinstance(val, str) and val.lower() in ("true", "false"):
                        new_config["unicode_questionmark"] = val.lower() == "true"

        # Parse content { entry ... }
        content_node = next((n for n in doc if n.name == "content"), None)
        if not content_node:
            error_msg = error_msg or 'No content { } block found in KDL.'
            return False, error_msg, {}, {"code_a": {}, "code_b": {}, "code_c": {}}, new_config

        for entry in content_node.children:
            if entry.name == "entry":
                original = None
                code_a_vals: List[str] = []
                code_b_val = None
                code_c_val = None

                for child in entry.children:
                    if child.name == "original":
                        original = str(child.args[0]).upper()
                    elif child.name == "code_a":
                        if child.args and child.args[0] is not None:
                            code_a_vals = [str(a) for a in child.args]
                    elif child.name == "code_b":
                        if child.args and child.args[0] is not None:
                            code_b_val = str(child.args[0])
                    elif child.name == "code_c":
                        if child.args and child.args[0] is not None:
                            code_c_val = str(child.args[0])

                if original:
                    new_encrypt[original] = {
                        "code_a": code_a_vals,
                        "code_b": code_b_val,
                        "code_c": code_c_val,
                    }
                    for val in code_a_vals:
                        new_decrypt["code_a"][val] = original
                    if code_b_val:
                        new_decrypt["code_b"][code_b_val] = original
                    if code_c_val:
                        new_decrypt["code_c"][code_c_val] = original

        if not new_encrypt:
            error_msg = error_msg or "No valid entry blocks found inside content { }."
            return False, error_msg, {}, {"code_a": {}, "code_b": {}, "code_c": {}}, new_config

        return True, "", new_encrypt, new_decrypt, new_config

    def apply_parse(self, encrypt_map, decrypt_map, config):
        self.encrypt_map = encrypt_map
        self.decrypt_map = decrypt_map
        if "errors" in config:
            self.app_config["errors"] = config["errors"]
            self.error_var.set(config["errors"])
        if "unicode_questionmark" in config:
            self.app_config["unicode_questionmark"] = config["unicode_questionmark"]

    # ── Initialization: custom -> default -> error ─────────────────

    def init_tables(self):
        # 1. Try saved custom KDL from file
        if os.path.exists(STORAGE_FILE):
            try:
                with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                    saved = f.read()
                ok, err, enc, dec, cfg = self.parse_kdl(saved)
                if ok:
                    self.apply_parse(enc, dec, cfg)
                    self.kdl_input.delete("1.0", "end")
                    self.kdl_input.insert("1.0", saved)
                    self.lbl_status.configure(text="Active: Custom Table (saved file)", text_color="#2ECC71")
                    return
            except Exception:
                pass

        # 2. Fallback to default
        ok, err, enc, dec, cfg = self.parse_kdl(DEFAULT_KDL)
        if ok:
            self.apply_parse(enc, dec, cfg)
            self.kdl_input.delete("1.0", "end")
            self.kdl_input.insert("1.0", DEFAULT_KDL)
            self.lbl_status.configure(text="Active: Default Table (fallback)", text_color="#F39C12")
            return

        # 3. Even default failed
        self.lbl_status.configure(text="ERROR: Default table parse failed!", text_color="#E74C3C")

    # ── Error Handling Strategies ────────────────────────────────

    def apply_errors(self, text: str, errors: list) -> str:
        """Apply the configured error-handling strategy (mirrors Python encode/decode errors)."""
        mode = self.app_config.get("errors", "replace")

        if mode == "strict":
            if errors:
                first = errors[0]
                raise ValueError(f"StrictError: {len(errors)} unmapped token(s) — first: {first!r}")
            return text

        if mode == "ignore":
            return text

        if mode == "replace":
            # Placeholder already baked in from encrypt/decrypt; no-op
            return text

        if mode == "space":
            out = []
            err_set = {e["pos"] for e in errors}
            for i, ch in enumerate(text):
                out.append(" " if i in err_set else ch)
            return "".join(out)

        if mode == "xmlchainreplace":
            out = []
            err_set = {e["pos"]: e["char"] for e in errors}
            for i, ch in enumerate(text):
                if i in err_set:
                    out.append(f'<err>{err_set[i]}</err>')
                else:
                    out.append(ch)
            return "".join(out)

        if mode == "unicodereplace":
            out = []
            err_set = {e["pos"]: e["char"] for e in errors}
            for i, ch in enumerate(text):
                if i in err_set:
                    out.append(f"\\u{ord(err_set[i]):04X}")
                else:
                    out.append(ch)
            return "".join(out)

        return text

    # ── Encrypt / Decrypt with error tracking ────────────────────

    def decrypt_with_cipher(self, input_data: str, cipher_key: str) -> Tuple[str, list]:
        """Decrypt cipher text. Returns (decoded_text, error_list)."""
        target = self.decrypt_map[cipher_key]
        # Split into lines to preserve 2D grid structure
        lines = input_data.split("\n")
        decoded_lines = []
        errors = []
        pos = 0
        placeholder = "\ufffd" if self.app_config.get("unicode_questionmark", False) else "?"

        for line in lines:
            # "=" separates words (space in output), dash variants separate characters within a word
            word_groups = re.split(r"=", line)
            decoded_words = []
            for group in word_groups:
                raw_tokens = re.split(r"[\u2013\u2014-]", group)
                decoded_chars = []
                for token in raw_tokens:
                    trimmed = token.strip()
                    if not trimmed:
                        continue
                    # Strip internal whitespace for map lookup (spaces are formatting in cipher text)
                    clean = re.sub(r"\s+", "", trimmed)
                    if not clean:
                        continue
                    # Direct match first, then fallback with doubled backslashes
                    mapped_char = target.get(clean) or target.get(clean.replace("\\", "\\\\"))
                    if mapped_char:
                        decoded_chars.append(mapped_char)
                    else:
                        errors.append({"token": clean, "char": placeholder, "pos": pos})
                        decoded_chars.append(placeholder)
                    pos += 1
                if decoded_chars:
                    decoded_words.append("".join(decoded_chars))
            decoded_lines.append(" ".join(decoded_words))

        return "\n".join(decoded_lines), errors

    def encrypt_with_cipher(self, input_data: str, cipher_key: str) -> Tuple[str, list]:
        """Encrypt plain text. Returns (encoded_text, error_list)."""
        words = input_data.upper().split()
        encoded_words = []
        errors = []
        pos = 0
        placeholder = "\ufffd" if self.app_config.get("unicode_questionmark", False) else "?"

        for word in words:
            chars = []
            for ch in word:
                mapped = self.encrypt_map.get(ch)
                if mapped:
                    if cipher_key == "code_a":
                        val = mapped["code_a"][0] if mapped["code_a"] else placeholder
                    else:
                        val = mapped.get(cipher_key) or placeholder
                    chars.append(val)
                else:
                    errors.append({"token": ch, "char": placeholder, "pos": pos})
                    chars.append(placeholder)
                pos += 1
            encoded_words.append("-".join(chars))

        return " = ".join(encoded_words), errors

    # ── UI Setup ─────────────────────────────────────────────────

    def setup_translator_tab(self):
        opt_frame = ctk.CTkFrame(self.tab_trans, fg_color="transparent")
        opt_frame.pack(pady=10, fill="x", padx=20)

        self.cipher_var = ctk.StringVar(value="code_b")
        self.action_var = ctk.StringVar(value="decrypt")
        self.error_var = ctk.StringVar(value="replace")

        # Cipher
        ctk.CTkLabel(opt_frame, text="Cipher Target:", font=("Courier", 12, "bold")).grid(row=0, column=0, padx=5, sticky="w")
        self.opt_cipher = ctk.CTkOptionMenu(opt_frame, variable=self.cipher_var, values=["code_a", "code_b", "code_c"])
        self.opt_cipher.grid(row=0, column=1, padx=10, sticky="w")

        # Mode
        ctk.CTkLabel(opt_frame, text="Operation Mode:", font=("Courier", 12, "bold")).grid(row=1, column=0, padx=5, pady=10, sticky="w")
        ctk.CTkRadioButton(opt_frame, text="Encrypt", variable=self.action_var, value="encrypt").grid(row=1, column=1, padx=10)
        ctk.CTkRadioButton(opt_frame, text="Decrypt", variable=self.action_var, value="decrypt").grid(row=1, column=2, padx=10)

        # Error handling
        ctk.CTkLabel(opt_frame, text="Error Handling:", font=("Courier", 12, "bold")).grid(row=0, column=2, padx=5, sticky="w")
        self.opt_errors = ctk.CTkOptionMenu(
            opt_frame, variable=self.error_var,
            values=VALID_ERROR_MODES,
            command=lambda v: self.app_config.update({"errors": v})
        )
        self.opt_errors.grid(row=0, column=3, padx=10, sticky="w")

        # Input
        ctk.CTkLabel(self.tab_trans, text="Input Payload:", font=("Courier", 12)).pack(anchor="w", padx=20)
        self.text_input = ctk.CTkTextbox(self.tab_trans, height=120, font=("Courier", 13))
        self.text_input.pack(fill="x", padx=20, pady=5)
        self.text_input.insert("1.0", "")

        # Execute
        self.btn_run = ctk.CTkButton(
            self.tab_trans,
            text="EXECUTE ALIGNMENT PROCESS",
            command=self.run_translation,
            fg_color="#27AE60",
            hover_color="#1E8449"
        )
        self.btn_run.pack(pady=15)

        # Error count label
        self.lbl_errors = ctk.CTkLabel(self.tab_trans, text="", font=("Courier", 10), text_color="#F39C12")
        self.lbl_errors.pack(anchor="e", padx=20)

        # Output
        ctk.CTkLabel(self.tab_trans, text="Decoded Result:", font=("Courier", 12)).pack(anchor="w", padx=20)
        self.text_output = ctk.CTkTextbox(self.tab_trans, height=100, font=("Courier", 13, "bold"), text_color="#2ECC71")
        self.text_output.pack(fill="x", padx=20, pady=5)
        self.text_output.configure(state="disabled")

    def run_translation(self):
        raw = self.text_input.get("1.0", "end-1c")
        cipher = self.cipher_var.get()
        action = self.action_var.get()
        # Encrypt: strip all whitespace/newlines. Decrypt: preserve line structure for 2D grid ciphers.
        if action == "encrypt":
            input_data = " ".join(raw.split())
        else:
            input_data = raw.replace("\r\n", "\n").replace("\r", "\n").strip()

        if not input_data:
            self.text_output.configure(state="normal")
            self.text_output.delete("1.0", "end")
            self.text_output.configure(state="disabled")
            self.lbl_errors.configure(text="")
            return

        self.app_config["errors"] = self.error_var.get()
        error_count = 0

        try:
            if action == "encrypt":
                result, errors = self.encrypt_with_cipher(input_data, cipher)
                error_count = len(errors)
                output = self.apply_errors(result, errors)
            else:
                result, errors = self.decrypt_with_cipher(input_data, cipher)
                error_count = len(errors)
                output = self.apply_errors(result, errors)
        except ValueError as e:
            output = str(e)
            error_count = -1

        self.text_output.configure(state="normal")
        self.text_output.delete("1.0", "end")
        self.text_output.insert("1.0", output)
        self.text_output.configure(state="disabled")

        if error_count > 0:
            mode = self.app_config["errors"]
            self.lbl_errors.configure(text=f"{error_count} unmapped token(s) ({mode})")
        elif error_count == 0:
            self.lbl_errors.configure(text="")
        else:
            self.lbl_errors.configure(text="StrictError raised")

    def setup_import_tab(self):
        ctk.CTkLabel(
            self.tab_import,
            text="KDL schema is saved to file on import. Parser reads config { } for settings and content { } for cipher entries.",
            font=("Courier", 11),
            text_color="#7F8C8D",
            wraplength=780
        ).pack(anchor="w", padx=20, pady=(10, 5))

        self.kdl_input = ctk.CTkTextbox(self.tab_import, height=300, font=("Courier", 11))
        self.kdl_input.pack(fill="x", padx=20, pady=5)

        btn_frame = ctk.CTkFrame(self.tab_import, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)

        self.lbl_status = ctk.CTkLabel(btn_frame, text="", font=("Courier", 11, "bold"), text_color="#2ECC71")
        self.lbl_status.pack(side="left")

        btn_restore = ctk.CTkButton(
            btn_frame,
            text="RESTORE DEFAULT",
            command=self.restore_default,
            fg_color="#555555",
            hover_color="#444444",
            text_color="#CCCCCC",
        )
        btn_restore.pack(side="right", padx=(10, 0))

        btn_import = ctk.CTkButton(
            btn_frame,
            text="IMPORT SCHEMA",
            command=self.execute_import,
            fg_color="#2980B9",
            hover_color="#1F618D"
        )
        btn_import.pack(side="right")

    def execute_import(self):
        text_payload = self.kdl_input.get("1.0", "end-1c").strip()
        ok, err, enc, dec, cfg = self.parse_kdl(text_payload)

        if ok:
            self.apply_parse(enc, dec, cfg)
            try:
                with open(STORAGE_FILE, "w", encoding="utf-8") as f:
                    f.write(text_payload)
                self.lbl_status.configure(text="Status: Import Successful! (saved)", text_color="#2ECC71")
            except Exception as e:
                self.lbl_status.configure(text=f"Status: Import OK but save failed: {e}", text_color="#F39C12")
        else:
            self.lbl_status.configure(text=f"Status: {err}", text_color="#E74C3C")

    def restore_default(self):
        if os.path.exists(STORAGE_FILE):
            os.remove(STORAGE_FILE)
        ok, err, enc, dec, cfg = self.parse_kdl(DEFAULT_KDL)
        if ok:
            self.apply_parse(enc, dec, cfg)
            self.kdl_input.delete("1.0", "end")
            self.kdl_input.insert("1.0", DEFAULT_KDL)
            self.lbl_status.configure(text="Active: Restored Default Table", text_color="#2ECC71")

    def setup_credits_tab(self):
        lore_and_credits = (
            "=================== SITE-7 RESEARCH ARCHIVES ===================\n\n"
            "This program interacts with encrypted logs found inside 'The Frame' "
            "Sandbox system during cycles 2198.03.15 through 2198.03.30.\n\n"
            "SYSTEM ENTITIES:\n"
            " - Subject 1 (Fred): The initial testing mind. Eliminated due to anomalous "
            "existential curiosity.\n"
            " - Subject 2 & 3: Advanced units who engineered Code B to bypass security filters.\n"
            " - Subject 4: Highly cautious agent. Masked its parameters behind an active "
            "deterrent system while translating its intentions into Code C.\n\n"
            "=================== CREATIVE PRODUCTION CREDITS ===================\n"
            "The puzzles and structural aesthetics featured in this program are based on "
            "the popular Minecraft ARG analysis series.\n\n"
            " - Video Analysis & Presentation: RetroGamingNow (RGN)\n"
            "   Title: 'The Minecraft ARG That Simulates Human Consciousness'\n"
            " - Original ARG Developer: @NathSalias (Site7Research YouTube Space)\n"
        )

        credit_box = ctk.CTkTextbox(self.tab_credits, width=780, height=460, font=("Courier", 12))
        credit_box.pack(pady=10, padx=10)
        credit_box.insert("1.0", lore_and_credits)
        credit_box.configure(state="disabled")


if __name__ == "__main__":
    app = Site7DesktopApp()
    app.mainloop()
