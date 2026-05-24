import customtkinter as ctk
import kdl
from typing import Dict, List, Optional

# Set UI styling parameters
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

DEFAULT_KDL = r"""
type "rainbow-table"
from null
name "Site7Research"
id "cb87da84-0ff4-46c5-8472-ee1d82f7c6b9"
created_at "2026/05/24 12:14:35"

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
        self.geometry("800x620")
        self.resizable(False, False)

        self.encrypt_map: Dict[str, dict] = {}
        self.decrypt_map: Dict[str, Dict[str, str]] = {"code_a": {}, "code_b": {}, "code_c": {}}

        # Title Label
        self.title_label = ctk.CTkLabel(
            self, 
            text="SITE-7 CONTAINMENT MONITOR", 
            font=ctk.CTkFont(family="Courier", size=24, weight="bold"),
            text_color="#2ECC71"
        )
        self.title_label.pack(pady=(20, 10))

        # Main Tabview component
        self.tabview = ctk.CTkTabview(self, width=760, height=520)
        self.tabview.pack(pady=10)
        
        self.tab_trans = self.tabview.add("TRANSLATOR")
        self.tab_import = self.tabview.add("IMPORT TABLE")
        self.tab_credits = self.tabview.add("PROJECT FILES & CREDITS")

        self.setup_translator_tab()
        self.setup_import_tab()
        self.setup_credits_tab()

        self.load_table_from_kdl(DEFAULT_KDL)

    def load_table_from_kdl(self, kdl_text: str) -> bool:
        try:
            doc = kdl.parse(kdl_text)
            content_node = next((node for node in doc if node.name == "content"), None)
            if not content_node:
                return False

            new_encrypt = {}
            new_decrypt = {"code_a": {}, "code_b": {}, "code_c": {}}

            for entry in content_node.children:
                if entry.name == "entry":
                    original = None
                    code_a_vals = []
                    code_b_val = None
                    code_c_val = None

                    for child in entry.children:
                        if child.name == "original":
                            original = str(child.args[0]).upper()
                        elif child.name == "code_a":
                            if child.args and child.args[0] is not None:
                                code_a_vals = [str(arg) for arg in child.args]
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
                            "code_c": code_c_val
                        }
                        for val in code_a_vals:
                            new_decrypt["code_a"][val] = original
                        if code_b_val:
                            new_decrypt["code_b"][code_b_val] = original
                        if code_c_val:
                            new_decrypt["code_c"][code_c_val] = original

            self.encrypt_map = new_encrypt
            self.decrypt_map = new_decrypt
            return True
        except Exception as e:
            print("KDL Parsing error:", e)
            return False

    def setup_translator_tab(self):
        opt_frame = ctk.CTkFrame(self.tab_trans, fg_color="transparent")
        opt_frame.pack(pady=10, fill="x", padx=20)

        self.cipher_var = ctk.StringVar(value="code_b")
        self.action_var = ctk.StringVar(value="decrypt")

        # Select target cipher
        ctk.CTkLabel(opt_frame, text="Cipher Target:", font=("Courier", 12, "bold")).grid(row=0, column=0, padx=5, sticky="w")
        self.opt_cipher = ctk.CTkOptionMenu(opt_frame, variable=self.cipher_var, values=["code_a", "code_b", "code_c"])
        self.opt_cipher.grid(row=0, column=1, padx=10, sticky="w")

        # Select mode
        ctk.CTkLabel(opt_frame, text="Operation Mode:", font=("Courier", 12, "bold")).grid(row=1, column=0, padx=5, pady=10, sticky="w")
        ctk.CTkRadioButton(opt_frame, text="Encrypt", variable=self.action_var, value="encrypt").grid(row=1, column=1, padx=10)
        ctk.CTkRadioButton(opt_frame, text="Decrypt", variable=self.action_var, value="decrypt").grid(row=1, column=2, padx=10)

        # Text input areas
        ctk.CTkLabel(self.tab_trans, text="Input Payload:", font=("Courier", 12)).pack(anchor="w", padx=20)
        self.text_input = ctk.CTkTextbox(self.tab_trans, height=120, font=("Courier", 13))
        self.text_input.pack(fill="x", padx=20, pady=5)
        self.text_input.insert("1.0", "///\\\\-///\\-////\\-///\\o = ////\\\\-///\\-////\\-///\\o")

        # Execute Button
        self.btn_run = ctk.CTkButton(
            self.tab_trans, 
            text="EXECUTE ALIGNMENT PROCESS", 
            command=self.run_translation, 
            fg_color="#27AE60", 
            hover_color="#1E8449"
        )
        self.btn_run.pack(pady=15)

        ctk.CTkLabel(self.tab_trans, text="Decoded Result:", font=("Courier", 12)).pack(anchor="w", padx=20)
        self.text_output = ctk.CTkTextbox(self.tab_trans, height=100, font=("Courier", 13, "bold"), text_color="#2ECC71")
        self.text_output.pack(fill="x", padx=20, pady=5)
        self.text_output.configure(state="disabled")

    def run_translation(self):
        input_data = self.text_input.get("1.0", "end-1c").strip()
        cipher = self.cipher_var.get()
        action = self.action_var.get()

        if not input_data:
            return

        result_text = ""
        if action == "encrypt":
            words = input_data.upper().split()
            encoded_words = []
            for word in words:
                encoded_chars = []
                for char in word:
                    if char in self.encrypt_map:
                        data = self.encrypt_map[char]
                        if cipher == "code_a":
                            val = data["code_a"][0] if data["code_a"] else "?"
                        else:
                            val = data[cipher] if data[cipher] else "?"
                        encoded_chars.append(val)
                    else:
                        encoded_chars.append("?")
                encoded_words.append("-".join(encoded_chars))
            result_text = " = ".join(encoded_words)

        else:  # Decrypt
            words = input_data.split("=")
            decoded_words = []
            target_map = self.decrypt_map[cipher]
            
            for word in words:
                tokens = word.strip().split("-")
                decoded_chars = []
                for token in tokens:
                    token_clean = token.strip()
                    if token_clean:
                        decoded_chars.append(target_map.get(token_clean, "?"))
                decoded_words.append("".join(decoded_chars))
            result_text = " ".join(decoded_words)

        self.text_output.configure(state="normal")
        self.text_output.delete("1.0", "end")
        self.text_output.insert("1.0", result_text)
        self.text_output.configure(state="disabled")

    def setup_import_tab(self):
        ctk.CTkLabel(
            self.tab_import, 
            text="Paste KDL Document configuration details to update mapping rules:", 
            font=("Courier", 12)
        ).pack(anchor="w", padx=20, pady=10)

        self.kdl_input = ctk.CTkTextbox(self.tab_import, height=280, font=("Courier", 11))
        self.kdl_input.pack(fill="x", padx=20, pady=5)
        self.kdl_input.insert("1.0", DEFAULT_KDL)

        self.lbl_status = ctk.CTkLabel(self.tab_import, text="Active Status: Loaded Default Mappings", font=("Courier", 11, "bold"), text_color="#3498DB")
        self.lbl_status.pack(side="left", padx=20, pady=10)

        btn_import = ctk.CTkButton(
            self.tab_import, 
            text="PARSE SYSTEMS TABLE", 
            command=self.execute_import, 
            fg_color="#2980B9", 
            hover_color="#1F618D"
        )
        btn_import.pack(side="right", padx=20, pady=10)

    def execute_import(self):
        text_payload = self.kdl_input.get("1.0", "end-1c").strip()
        success = self.load_table_from_kdl(text_payload)
        if success:
            self.lbl_status.configure(text="Active Status: Import Successful", text_color="#2ECC71")
        else:
            self.lbl_status.configure(text="Active Status: Parsing Failed!", text_color="#E74C3C")

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

        credit_box = ctk.CTkTextbox(self.tab_credits, width=720, height=420, font=("Courier", 12))
        credit_box.pack(pady=10, padx=10)
        credit_box.insert("1.0", lore_and_credits)
        credit_box.configure(state="disabled")

if __name__ == "__main__":
    app = Site7DesktopApp()
    app.mainloop()