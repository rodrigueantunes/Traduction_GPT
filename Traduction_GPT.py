print("      ██████╗ ██╗  ")
print("     ██╔═══██╗██║  ")
print("     ██║   ██║██║  ")
print("     ██║   ██║██║  ")
print("     ╚██████╔╝██║  ")
print("      ╚═════╝ ╚═╝  ")
print("                   ")
print("    Antunes        ")
print("  Informatique     ")

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import pandas as pd
import openai
import os
import time
import threading
import json
from datetime import datetime
import subprocess
import tiktoken
import sys

# ------------------- Gestion des clés API -----------------------
KEYS_FILE = "openai_keys.json"

def load_api_keys():
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, "r", encoding="utf-8") as f:
            try:
                keys = json.load(f)
                return keys
            except Exception:
                return {}
    return {}

def save_api_keys(keys):
    with open(KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(keys, f, ensure_ascii=False, indent=2)

def show_api_key_manager():
    def refresh_key_list():
        keys = load_api_keys()
        key_list.delete(0, tk.END)
        for title in keys:
            key_list.insert(tk.END, title)
    def add_key():
        title = simpledialog.askstring("Titre de la clé", "Donnez un titre explicite pour cette clé API :")
        if not title: return
        key = simpledialog.askstring("Clé API", "Collez la clé API OpenAI :", show="*")
        if not key or not key.startswith("sk-"):
            messagebox.showerror("Erreur", "Clé API invalide.")
            return
        keys = load_api_keys()
        keys[title] = key
        save_api_keys(keys)
        refresh_key_list()
    def del_key():
        sel = key_list.curselection()
        if not sel: return
        title = key_list.get(sel[0])
        if messagebox.askyesno("Supprimer ?", f"Supprimer la clé API : {title} ?"):
            keys = load_api_keys()
            keys.pop(title, None)
            save_api_keys(keys)
            refresh_key_list()
    def select_key():
        sel = key_list.curselection()
        if sel:
            title = key_list.get(sel[0])
            selected_api_key_title.set(title)
            popup.destroy()
            update_selected_api_key()
    popup = tk.Toplevel(root)
    popup.title("Gestion des clés API OpenAI")
    popup.geometry("400x320")
    popup.grab_set()
    popup.resizable(False, False)
    ttk.Label(popup, text="Vos clés API enregistrées :", font=("Segoe UI", 12, "bold")).pack(pady=8)
    key_list = tk.Listbox(popup, height=8, font=("Segoe UI", 10))
    key_list.pack(fill="x", padx=20, pady=(0,8))
    btn_frame = ttk.Frame(popup)
    btn_frame.pack(fill="x", padx=18, pady=2)
    ttk.Button(btn_frame, text="Ajouter une clé", command=add_key).pack(side="left", expand=True, fill="x", padx=2)
    ttk.Button(btn_frame, text="Supprimer", command=del_key).pack(side="left", expand=True, fill="x", padx=2)
    ttk.Button(popup, text="Sélectionner la clé", command=select_key, style="Accent.TButton").pack(pady=6)
    refresh_key_list()
    popup.mainloop()

def update_selected_api_key(event=None):
    keys = load_api_keys()
    title = selected_api_key_title.get()
    if title in keys:
        api_key_var.set(keys[title])
    else:
        api_key_var.set("")

# --------------------------------------------------------------

def open_example_model():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "modele_traduction.xlsx")
    if not os.path.exists(model_path):
        messagebox.showerror("Erreur", f"Le fichier modèle n'existe pas : {model_path}")
        return
    try:
        if sys.platform.startswith("win"):
            os.startfile(model_path)
        elif sys.platform.startswith("darwin"):
            subprocess.call(["open", model_path])
        else:
            subprocess.call(["xdg-open", model_path])
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'ouvrir le modèle :\n{e}")

# --------------------------------------------------------------

MODEL_PRICING = {
    # Tarifs OpenAI officiels au 1er juillet 2025 (USD pour 1 000 tokens)
    "gpt-4o":            {"input": 0.005,  "output": 0.015},
    "gpt-4o-mini":       {"input": 0.0025, "output": 0.0075},
    "gpt-4-turbo":       {"input": 0.01,   "output": 0.03},
    "gpt-4":             {"input": 0.03,   "output": 0.06},
    "gpt-3.5-turbo":     {"input": 0.0005, "output": 0.0015},
    "gpt-3.5-turbo-0125":{"input": 0.0005, "output": 0.0015},
    "o3":                {"input": 0.03,   "output": 0.06},    # à ajuster si besoin
    "o3-pro":            {"input": 0.02,   "output": 0.08},
}

MODEL_LIST = list(MODEL_PRICING.keys())

LANGUAGES = {
    "Espagnol": {"code": "es", "prompt": "espagnol industriel", "short": "ES"},
    "Anglais":  {"code": "en", "prompt": "anglais industriel",   "short": "EN"},
    "Italien":  {"code": "it", "prompt": "italien industriel",   "short": "IT"},
    "Portugais":{"code": "pt", "prompt": "portugais industriel", "short": "PT"},
    "Chinois":  {"code": "zh", "prompt": "chinois industriel",   "short": "ZH"},
    "Japonais": {"code": "ja", "prompt": "japonais industriel",  "short": "JA"},
    "Arabe":    {"code": "ar", "prompt": "arabe industriel",     "short": "AR"},
    "Russe":    {"code": "ru", "prompt": "russe industriel",     "short": "RU"}
}
LANGUAGE_LIST = list(LANGUAGES.keys())

PROMPT_TEMPLATE = (
    "Traduis le texte suivant en {lang_prompt}, sans rien omettre, "
    "en conservant strictement tous les %1, %2, etc. Ne modifie rien d’autre, "
    "et réponds uniquement par la traduction :\n\n\"{fr_text}\""
)

LOG_EVERY = 10
current_df = None
current_lang = LANGUAGE_LIST[0]
total_usage = {"prompt_tokens": 0, "completion_tokens": 0}

CORRECTION_FILE = "estimation_correction.json"

def load_correction_factor():
    if os.path.exists(CORRECTION_FILE):
        try:
            with open(CORRECTION_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("correction_factor", 1.0)
        except:
            pass
    return 1.0  # Par défaut pas de correction

def save_correction_factor(factor):
    with open(CORRECTION_FILE, "w", encoding="utf-8") as f:
        json.dump({"correction_factor": factor}, f)


def estimate_cost(df, model):
    # 1 token ≈ 4 chars ; output tokens ~ 0.8 * input tokens
    if 'fr' not in df.columns:
        return 0.0
    frs = df['fr'].dropna().astype(str)
    frs = frs[frs.str.strip() != ""]
    nb_chars = frs.map(len).sum()
    nb_tokens = nb_chars // 4
    output_tokens = int(nb_tokens * 0.8)
    price = MODEL_PRICING[model]
    cost = (nb_tokens/1000)*price['input'] + (output_tokens/1000)*price['output']
    correction = load_correction_factor()
    return round(cost * correction, 4)




def update_cost_estimate():
    model = model_var.get()
    if current_df is not None:
        total = len(current_df[current_df['fr'].astype(str).str.strip() != ""])
        cost = estimate_cost(current_df, model)
        print(f"[UI UPDATE] {total} lignes → estimation coût: {cost} $ ({model})")
        cost_var.set(f"Prévision : {total} lignes – coût estimé {cost} $ ({model})")
    else:
        cost_var.set("Prévision : –")

def browse_file():
    global current_df
    filename = filedialog.askopenfilename(
        title="Choisir le fichier Excel à traduire",
        filetypes=[("Excel files", "*.xlsx")]
    )
    if filename:
        file_var.set(filename)
        block_var.set(f"Fichier chargé : {os.path.basename(filename)}")
        try:
            df = pd.read_excel(filename, sheet_name=0)
            current_df = df
            update_cost_estimate()
        except Exception as e:
            current_df = None
            update_cost_estimate()
            messagebox.showerror("Erreur lecture Excel", str(e))

def on_model_change(event=None):
    update_cost_estimate()

def on_language_change(event=None):
    global current_lang
    current_lang = lang_var.get()
    lang_info = LANGUAGES[current_lang]
    lang_code = lang_info["code"]
    main_title.set(f"Traduction Excel FR ➔ {lang_info['short']} industriel")
    if current_df is not None:
        update_cost_estimate()

def call_openai(prompt, apikey, model):
    openai.api_key = apikey
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[{"role":"user","content":prompt}],
        temperature=0.0,
        max_tokens=512
    )
    usage = resp['usage']
    total_usage["prompt_tokens"]    += usage.get("prompt_tokens", 0)
    total_usage["completion_tokens"] += usage.get("completion_tokens", 0)
    return resp.choices[0].message.content.strip()

def export_log(log_lines, original_path):
    basename = os.path.splitext(os.path.basename(original_path))[0]
    out_path = os.path.join(os.path.dirname(original_path), f"{basename}_traduction_log.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        for line in log_lines:
            f.write(line + "\n")
    return out_path

def translate_file():
    apikey = api_key_var.get().strip()
    model = model_var.get()
    lang = lang_var.get()
    lang_info = LANGUAGES[lang]
    lang_code = lang_info["code"]
    xlsx_path = file_var.get()
    global current_df
    if not apikey or not apikey.startswith("sk-"):
        messagebox.showerror("Erreur", "Merci de sélectionner ou saisir une clé API OpenAI valide.")
        return
    if not xlsx_path or not os.path.exists(xlsx_path):
        messagebox.showerror("Erreur", "Merci de sélectionner un fichier XLSX valide.")
        return
    if current_df is None:
        messagebox.showerror("Erreur", "Aucun fichier chargé.")
        return

    df = current_df.copy()
    col_trad = lang_code
    if col_trad not in df.columns:
        df[col_trad] = ""
    if 'statut' not in df.columns:
        df['statut'] = ""
    total = len(df)
    estimated_cost = estimate_cost(df, model)
    proceed = messagebox.askyesno(
        "Traduire tout le fichier ?",
        f"{total} lignes seront traduites via OpenAI ({model}).\n"
        f"Langue : {lang} ({lang_code})\n"
        f"Coût estimé : ~{estimated_cost} $ (estimation).\n\nContinuer ?"
    )
    if not proceed:
        return

    log_lines = []
    start_time = datetime.now()
    temp_path = os.path.splitext(xlsx_path)[0] + f"_auto_save_{lang_code}.xlsx"

    for idx, row in df.iterrows():
        fr = str(row['fr'])
        if not isinstance(fr, str) or fr.strip() == "" or pd.isna(fr):
            df.at[idx, col_trad] = ""
            df.at[idx, "statut"] = "Vide"
            log_lines.append(f"{idx+1}\tVIDE")
            continue
        prompt = PROMPT_TEMPLATE.format(lang_prompt=lang_info["prompt"], fr_text=fr)
        try:
            trad = call_openai(prompt, apikey, model)
            if not trad or trad.strip() == "":
                df.at[idx, col_trad] = ""
                df.at[idx, "statut"] = "Erreur : réponse vide"
                log_lines.append(f"{idx+1}\tERREUR\tFR: {fr[:30]}...\tRéponse vide")
                continue
            trad = trad.strip()
            # Retire un seul couple de guillemets si présents, mais écrit toujours le résultat
            if (trad.startswith('"') and trad.endswith('"')) or (trad.startswith("'") and trad.endswith("'")):
                trad = trad[1:-1].strip()
            df.at[idx, col_trad] = trad
            df.at[idx, "statut"] = "OK"
            log_lines.append(f"{idx+1}\tOK\tFR: {fr[:30]}...\t{lang_code.upper()}: {trad[:30]}...")
        except Exception as e:
            df.at[idx, col_trad] = f"!! ERREUR OPENAI : {e}"
            df.at[idx, "statut"] = f"Erreur : {e}"
            log_lines.append(f"{idx+1}\tERREUR\tFR: {fr[:30]}...\t{e}")
        progress_var.set(f"Ligne {idx+1} / {total} ({int((idx+1)/total*100)}%)")
        progressbar['value'] = int((idx+1)/total*100)
        root.update()
        if idx % LOG_EVERY == 0 and idx != 0:
            df.to_excel(temp_path, index=False)
            export_log(log_lines, xlsx_path)
        time.sleep(0.7)

    df.to_excel(temp_path, index=False)
    log_path = export_log(log_lines, xlsx_path)

    out_path = filedialog.asksaveasfilename(
        title="Sauvegarder le résultat",
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("CSV", "*.csv")]
    )

    price = MODEL_PRICING[model]
    real_cost = (total_usage["prompt_tokens"]/1000)*price['input'] \
              + (total_usage["completion_tokens"]/1000)*price['output']
    print(f"Coût réel : {real_cost:.4f} $")

    if out_path:
        if out_path.endswith(".xlsx"):
            df.to_excel(out_path, index=False)
        else:
            df.to_csv(out_path, index=False, encoding="cp1252", quoting=1)
        elapsed = (datetime.now() - start_time).total_seconds()
        final_cost = estimate_cost(df, model)

        if final_cost > 0:
            new_factor = real_cost / final_cost
            save_correction_factor(new_factor)
            print(f"Facteur correction mis à jour : {new_factor:.3f}")
        else:
            print("Impossible de corriger le facteur (estimation nulle)")

        messagebox.showinfo(
            "Fini",
            f"Traduction terminée et sauvegardée :\n{out_path}\n\n"
            f"Log détaillé : {log_path}\n"
            f"Temps écoulé : {int(elapsed)} sec\n"
            f"Coût estimé total : ~{final_cost} $\n"
            f"Coût réel OpenAI : {real_cost:.4f} $"
        )


def threaded_translate():
    t = threading.Thread(target=translate_file)
    t.start()

# ----- Interface graphique moderne -----
root = tk.Tk()
main_title = tk.StringVar(value=f"Traduction Excel FR ➔ Multi-Langues industriel")
root.title(main_title.get())

style = ttk.Style()
try:
    style.theme_use('azure')
except:
    style.theme_use('clam')

root.geometry("670x570")
root.minsize(560, 440)
root.configure(bg="#f6f9fa")

file_var = tk.StringVar()
block_var = tk.StringVar()
api_key_var = tk.StringVar()
selected_api_key_title = tk.StringVar()
model_var = tk.StringVar(value=MODEL_LIST[0])
lang_var = tk.StringVar(value=LANGUAGE_LIST[0])
progress_var = tk.StringVar()
cost_var = tk.StringVar()

frame = ttk.Frame(root, padding=30, style="Card.TFrame")
frame.place(relx=0.5, rely=0.5, anchor="center")

ttk.Label(frame, textvariable=main_title, font=("Segoe UI", 18, "bold")).grid(row=0, column=0, columnspan=3, pady=(0,16))

ttk.Label(frame, text="Fichier XLSX à traduire :", font=("Segoe UI", 11)).grid(row=1, column=0, sticky="w")
ttk.Entry(frame, textvariable=file_var, width=44, font=("Segoe UI", 10)).grid(row=2, column=0, pady=(0,4), sticky="we")
ttk.Button(frame, text="Parcourir...", command=browse_file, style="Accent.TButton").grid(row=2, column=1, padx=8)
ttk.Label(frame, textvariable=block_var, foreground="#1976d2", font=("Segoe UI", 10, "italic")).grid(row=3, column=0, sticky="w", columnspan=3, pady=(0,4))
ttk.Button(frame, text="Modèle Exemple", command=open_example_model, width=18).grid(row=2, column=2, padx=2)

ttk.Label(frame, textvariable=cost_var, font=("Segoe UI", 11, "bold"), foreground="#00897b").grid(row=4, column=0, columnspan=3, sticky="w", pady=(0,8))

ttk.Label(frame, text="Langue de traduction :", font=("Segoe UI", 11)).grid(row=5, column=0, sticky="w", pady=(6,0))
lang_menu = ttk.Combobox(frame, textvariable=lang_var, values=LANGUAGE_LIST, state="readonly", width=22, font=("Segoe UI", 10))
lang_menu.grid(row=5, column=1, pady=(0,4), sticky="w")
lang_menu.bind("<<ComboboxSelected>>", on_language_change)

# --- Sélection clé API
ttk.Label(frame, text="Clé API OpenAI :", font=("Segoe UI", 11)).grid(row=6, column=0, sticky="w", pady=(6,0))
api_key_combo = ttk.Combobox(frame, textvariable=selected_api_key_title, values=list(load_api_keys().keys()), state="readonly", width=22, font=("Segoe UI", 10))
api_key_combo.grid(row=6, column=1, pady=(0,4), sticky="w")
api_key_combo.bind("<<ComboboxSelected>>", update_selected_api_key)
ttk.Button(frame, text="Gérer les clés API", command=show_api_key_manager, width=18).grid(row=6, column=2, padx=4)

ttk.Entry(frame, textvariable=api_key_var, width=44, show="*", font=("Segoe UI", 10)).grid(row=7, column=0, pady=(0,8), sticky="we", columnspan=3)

ttk.Label(frame, text="Modèle OpenAI :", font=("Segoe UI", 11)).grid(row=8, column=0, sticky="w")
model_menu = ttk.Combobox(frame, textvariable=model_var, values=MODEL_LIST, state="readonly", width=22, font=("Segoe UI", 10))
model_menu.grid(row=8, column=1, pady=(0,4), sticky="w")
model_menu.bind("<<ComboboxSelected>>", on_model_change)

ttk.Button(frame, text="Traduire tout le fichier", command=threaded_translate, style="Accent.TButton", width=30).grid(row=9, column=0, pady=16, columnspan=3)

progressbar = ttk.Progressbar(frame, length=340, mode='determinate')
progressbar.grid(row=10, column=0, columnspan=3, pady=(0,4))

ttk.Label(frame, textvariable=progress_var, foreground="#e53935", font=("Segoe UI", 10, "bold")).grid(row=11, column=0, columnspan=3, sticky="w", pady=(0,8))

ttk.Label(frame, text="Respecte strictement les variables %1, %2, etc.\nLog, auto-save et coût estimé affichés avant/après.\nModèles : GPT-4o, GPT-4, O3, etc.",
          font=("Segoe UI", 9, "italic"), foreground="#616161").grid(row=12, column=0, columnspan=3, pady=(10,0))

style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"), foreground="white", background="#1976d2")
style.map("Accent.TButton",
    background=[("active", "#1565c0"), ("disabled", "#b0bec5")],
    foreground=[("disabled", "#eeeeee")])
style.configure("Card.TFrame", background="white", borderwidth=1, relief="groove")

update_cost_estimate()
root.mainloop()
