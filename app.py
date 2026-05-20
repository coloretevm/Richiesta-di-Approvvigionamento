from __future__ import annotations

import sys
import json
import os
import base64
import hashlib
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from urllib import error as urlerror
from urllib import request as urlrequest

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


APP_TITLE = "Richiesta di Approvvigionamento"
APP_VERSION = "1.8"
TODAY = date.today()
DATE_TEXT = TODAY.strftime("%d/%m/%Y")
OUTPUT_DATE_TEXT = TODAY.strftime("%d-%m-%Y")
CURRENT_YEAR = TODAY.year
COUNTER_FILE = "richiesta_counter.json"
REQUEST_NUMBER_WIDTH = 4
GITHUB_OWNER = "coloretevm"
GITHUB_REPO = "Richiesta-di-Approvvigionamento"
GITHUB_BRANCH = "main"
GITHUB_TOKEN_ENV = "RICHIESTA_GITHUB_TOKEN"
GITHUB_TOKEN_FILE = "github_token.txt"
COUNTER_ADMIN_PASSWORD_HASH = "65f2099f216d2928d0f145e82ca8bf4580d8b9cf0878abc63d9ad239304afafa"
GITHUB_COUNTER_API_URL = (
    f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{COUNTER_FILE}"
)
GITHUB_MAX_RESERVE_ATTEMPTS = 5
FOOTER_TEXT = (
    "SISTEMA GESTIONE INTEGRATO - RICHIESTA DI APPROVVIGIONAMENTO"
)
ACCENT_COLOR = colors.HexColor("#0e3f86")
TEXT_COLOR = colors.HexColor("#1a1a1a")
LIGHT_FILL = colors.HexColor("#f7f8fa")
LINE_COLOR = colors.HexColor("#c9d2df")
TABLE_HEADER_FILL = colors.HexColor("#e8edf5")
SOFT_BLUE = colors.HexColor("#f3f7fc")
MUTED_TEXT = colors.HexColor("#5d6775")
PAGE_LEFT = 15 * mm
PAGE_RIGHT = 18 * mm
PAGE_WIDTH_CONTENT = A4[0] - PAGE_LEFT - PAGE_RIGHT

MAIN_OPTIONS = [
    ("commessa", "materiali per commessa / ord. n."),
    ("magazzino", "materiali a fondo magazzino"),
    ("consumo", "materiali di consumo"),
    ("terzi", "lavorazioni affidate a terzi"),
    ("attrezzature", "apparecchiature ed attrezzature"),
    ("altro", "altro"),
]

DETAIL_OPTIONS = [
    ("membrane", "membrane"),
    ("molle", "molle"),
    ("bulloneria", "bulloneria"),
    ("raccordi", "raccordi"),
    ("elettrovalvole", "elettrovalvole e bobine"),
    ("altro", "altro"),
]

UI_LANGUAGES = {
    "es": "Español",
    "it": "Italiano",
    "en": "English",
}

UI_TEXTS = {
    "es": {
        "app_title": "Richiesta di Approvvigionamento",
        "window_title": "Generador de Richiesta di Approvvigionamento",
        "subtitle": "Completa el formulario, cambia el idioma cuando quieras y genera el PDF final.",
        "tab_form": "Formulario",
        "tab_language": "Idioma",
        "language_title": "Idioma de la aplicación",
        "language_help": "Elige el idioma de la interfaz. El PDF seguirá manteniendo la estructura del formulario.",
        "language_label": "Idioma",
        "quick_hint": "Cuando termines de rellenar los datos, pulsa el botón para crear el PDF.",
        "request_number": "Richiesta: N. {number}",
        "request_number_error": "Richiesta: N. no disponible",
        "generate_pdf": "Generar PDF",
        "reset_form": "Limpiar formulario",
        "counter_admin_button": "Modificar N. richiesta",
        "section_top": "Parte superior",
        "section_detail": "Particolare",
        "section_materials": "Distinta",
        "main_extra": "Texto a la derecha si eliges la primera o la última opción",
        "detail_extra": "Texto a la derecha de altro",
        "materials_help": "Añade materiales y el PDF los colocará por filas en la tabla.",
        "add_material": "Añadir material",
        "edit_material": "Editar seleccionado",
        "delete_material": "Eliminar seleccionado",
        "footer_info": "Fecha automática: {date} | Spedizione a: Tecnidro | Richiedente: Altro Ente - Rodriguez Manuel Mateo",
        "status_ready": "Completa el formulario y genera el PDF final.",
        "status_material_added": "Material agregado correctamente.",
        "status_material_updated": "Material actualizado correctamente.",
        "status_material_deleted": "Material eliminado.",
        "status_form_reset": "Formulario reiniciado.",
        "status_pdf_generated": "PDF generado en: {path}",
        "material_dialog_title": "Material",
        "material_description": "Descripción",
        "material_quantity": "Cantidad",
        "material_delivery": "Fecha de entrega requerida",
        "material_order": "Orden n. ____ del ____",
        "cancel": "Cancelar",
        "accept": "Aceptar",
        "warn_material_complete": "Completa descripción, cantidad, fecha de entrega y referencia de orden.",
        "warn_select_edit": "Selecciona un material para editar.",
        "warn_select_delete": "Selecciona un material para eliminar.",
        "warn_main_extra": "Si eliges la primera o la última opción, completa el texto de la derecha.",
        "warn_detail_extra": "Si marcas 'altro' en PARTICOLARE, completa el texto de la derecha.",
        "warn_need_materials": "Agrega al menos un material en DISTINTA.",
        "save_pdf_title": "Guardar PDF",
        "pdf_ok": "PDF generado correctamente.\n\n{path}",
        "pdf_error": "No se pudo generar el PDF.\n\n{error}",
        "github_token_missing": "Falta el token de GitHub. Coloca `github_token.txt` junto al .exe o configura la variable `RICHIESTA_GITHUB_TOKEN`.",
        "github_counter_error": "No se pudo reservar el número en GitHub.\n\n{error}",
        "github_reserving": "Reservando número de richiesta en GitHub...",
        "counter_password_title": "Modificar número richiesta",
        "counter_password_prompt": "Contraseña:",
        "counter_password_error": "Contraseña incorrecta.",
        "counter_number_title": "Nuevo número richiesta",
        "counter_number_prompt": "Próximo número de richiesta:",
        "counter_update_ok": "Número de richiesta actualizado en GitHub: N. {number}",
        "columns": ["Descripción", "Cant.", "Entrega requerida", "Orden n. del"],
    },
    "it": {
        "app_title": "Richiesta di approvvigionamento",
        "window_title": "Generatore Richiesta di approvvigionamento",
        "subtitle": "Compila il modulo, cambia lingua quando vuoi e genera il PDF finale.",
        "tab_form": "Modulo",
        "tab_language": "Lingua",
        "language_title": "Lingua dell'applicazione",
        "language_help": "Scegli la lingua dell'interfaccia. Il PDF manterrà la struttura del modulo.",
        "language_label": "Lingua",
        "quick_hint": "Quando hai finito di compilare i dati, premi il pulsante per creare il PDF.",
        "request_number": "Richiesta: N. {number}",
        "request_number_error": "Richiesta: N. non disponibile",
        "generate_pdf": "Genera PDF",
        "reset_form": "Pulisci modulo",
        "counter_admin_button": "Modifica N. richiesta",
        "section_top": "Parte superiore",
        "section_detail": "Particolare",
        "section_materials": "Distinta",
        "main_extra": "Testo a destra se scegli la prima o l'ultima opzione",
        "detail_extra": "Testo a destra di altro",
        "materials_help": "Aggiungi materiali e il PDF li inserirà riga per riga nella tabella.",
        "add_material": "Aggiungi materiale",
        "edit_material": "Modifica selezionato",
        "delete_material": "Elimina selezionato",
        "footer_info": "Data automatica: {date} | Spedizione a: Tecnidro | Richiedente: Altro Ente - Rodriguez Manuel Mateo",
        "status_ready": "Compila il modulo e genera il PDF finale.",
        "status_material_added": "Materiale aggiunto correttamente.",
        "status_material_updated": "Materiale aggiornato correttamente.",
        "status_material_deleted": "Materiale eliminato.",
        "status_form_reset": "Modulo ripristinato.",
        "status_pdf_generated": "PDF generato in: {path}",
        "material_dialog_title": "Materiale",
        "material_description": "Descrizione",
        "material_quantity": "Quantità",
        "material_delivery": "Data consegna richiesta",
        "material_order": "Ordine n. ____ del ____",
        "cancel": "Annulla",
        "accept": "Conferma",
        "warn_material_complete": "Completa descrizione, quantità, data di consegna e riferimento ordine.",
        "warn_select_edit": "Seleziona un materiale da modificare.",
        "warn_select_delete": "Seleziona un materiale da eliminare.",
        "warn_main_extra": "Se scegli la prima o l'ultima opzione, compila il testo a destra.",
        "warn_detail_extra": "Se selezioni 'altro' in PARTICOLARE, compila il testo a destra.",
        "warn_need_materials": "Aggiungi almeno un materiale nella DISTINTA.",
        "save_pdf_title": "Salva PDF",
        "pdf_ok": "PDF generato correttamente.\n\n{path}",
        "pdf_error": "Impossibile generare il PDF.\n\n{error}",
        "github_token_missing": "Token GitHub mancante. Metti `github_token.txt` accanto al .exe oppure configura la variabile `RICHIESTA_GITHUB_TOKEN`.",
        "github_counter_error": "Impossibile prenotare il numero su GitHub.\n\n{error}",
        "github_reserving": "Prenotazione del numero richiesta su GitHub...",
        "counter_password_title": "Modifica numero richiesta",
        "counter_password_prompt": "Password:",
        "counter_password_error": "Password non corretta.",
        "counter_number_title": "Nuovo numero richiesta",
        "counter_number_prompt": "Prossimo numero richiesta:",
        "counter_update_ok": "Numero richiesta aggiornato su GitHub: N. {number}",
        "columns": ["Descrizione", "Q.t.", "Consegna richiesta", "Ordine n. del"],
    },
    "en": {
        "app_title": "Procurement request",
        "window_title": "Procurement request generator",
        "subtitle": "Fill in the form, switch language anytime, and generate the final PDF.",
        "tab_form": "Form",
        "tab_language": "Language",
        "language_title": "Application language",
        "language_help": "Choose the interface language. The PDF will still keep the form structure.",
        "language_label": "Language",
        "quick_hint": "When you finish entering the data, press the button to create the PDF.",
        "request_number": "Request: No. {number}",
        "request_number_error": "Request: No. unavailable",
        "generate_pdf": "Generate PDF",
        "reset_form": "Clear form",
        "counter_admin_button": "Edit request no.",
        "section_top": "Top section",
        "section_detail": "Particolare",
        "section_materials": "Distinta",
        "main_extra": "Text on the right if you choose the first or the last option",
        "detail_extra": "Text on the right of altro",
        "materials_help": "Add materials and the PDF will place them row by row in the table.",
        "add_material": "Add material",
        "edit_material": "Edit selected",
        "delete_material": "Delete selected",
        "footer_info": "Automatic date: {date} | Spedizione a: Tecnidro | Richiedente: Altro Ente - Rodriguez Manuel Mateo",
        "status_ready": "Complete the form and generate the final PDF.",
        "status_material_added": "Material added successfully.",
        "status_material_updated": "Material updated successfully.",
        "status_material_deleted": "Material deleted.",
        "status_form_reset": "Form reset.",
        "status_pdf_generated": "PDF generated at: {path}",
        "material_dialog_title": "Material",
        "material_description": "Description",
        "material_quantity": "Quantity",
        "material_delivery": "Requested delivery date",
        "material_order": "Order no. ____ dated ____",
        "cancel": "Cancel",
        "accept": "Accept",
        "warn_material_complete": "Complete description, quantity, delivery date, and order reference.",
        "warn_select_edit": "Select a material to edit.",
        "warn_select_delete": "Select a material to delete.",
        "warn_main_extra": "If you choose the first or last option, fill in the text on the right.",
        "warn_detail_extra": "If you check 'altro' in PARTICOLARE, fill in the text on the right.",
        "warn_need_materials": "Add at least one material in DISTINTA.",
        "save_pdf_title": "Save PDF",
        "pdf_ok": "PDF generated successfully.\n\n{path}",
        "pdf_error": "Could not generate the PDF.\n\n{error}",
        "github_token_missing": "Missing GitHub token. Put `github_token.txt` next to the .exe or configure `RICHIESTA_GITHUB_TOKEN`.",
        "github_counter_error": "Could not reserve the request number on GitHub.\n\n{error}",
        "github_reserving": "Reserving request number on GitHub...",
        "counter_password_title": "Edit request number",
        "counter_password_prompt": "Password:",
        "counter_password_error": "Incorrect password.",
        "counter_number_title": "New request number",
        "counter_number_prompt": "Next request number:",
        "counter_update_ok": "Request number updated on GitHub: No. {number}",
        "columns": ["Description", "Qty.", "Requested delivery", "Order no. / date"],
    },
}


@dataclass
class MaterialRow:
    description: str
    quantity: str
    delivery_date: str
    order_reference: str


def resource_path(relative_path: str) -> Path:
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path


def runtime_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def format_request_number(number: int) -> str:
    return f"{max(1, number):0{REQUEST_NUMBER_WIDTH}d}"


def default_counter_data() -> dict[str, object]:
    return {
        "year": CURRENT_YEAR,
        "next_number": 1,
        "updated_at": "",
        "updated_by": "",
    }


def normalize_counter_data(data: object) -> dict[str, object]:
    counter = default_counter_data()
    if not isinstance(data, dict):
        return counter
    try:
        counter_year = int(data.get("year", CURRENT_YEAR))
    except (TypeError, ValueError):
        counter_year = CURRENT_YEAR
    if counter_year != CURRENT_YEAR:
        return counter

    try:
        next_number = int(data.get("next_number", 1))
    except (TypeError, ValueError):
        next_number = 1

    counter["year"] = CURRENT_YEAR
    counter["next_number"] = max(1, next_number)
    counter["updated_at"] = str(data.get("updated_at", "") or "")
    counter["updated_by"] = str(data.get("updated_by", "") or "")
    return counter


def load_github_token() -> str:
    env_token = os.environ.get(GITHUB_TOKEN_ENV, "").strip()
    if env_token:
        return env_token

    token_paths = [
        resource_path(GITHUB_TOKEN_FILE),
        runtime_dir() / GITHUB_TOKEN_FILE,
    ]
    for token_path in token_paths:
        try:
            if token_path.is_file():
                token = token_path.read_text(encoding="utf-8").strip()
                if token:
                    return token
        except OSError:
            continue
    return ""


def github_headers(token: str = "") -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Richiesta-di-Approvvigionamento",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def github_error_detail(exc: urlerror.HTTPError) -> str:
    try:
        payload = exc.read().decode("utf-8", errors="replace")
        data = json.loads(payload)
        message = str(data.get("message", "")).strip()
        if message:
            return f"GitHub HTTP {exc.code}: {message}"
    except Exception:
        pass
    return f"GitHub HTTP {exc.code}: {exc.reason}"


def github_request_json(
    url: str,
    *,
    token: str = "",
    data: dict[str, object] | None = None,
    method: str | None = None,
) -> dict[str, object]:
    body = None
    headers = github_headers(token)
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urlrequest.Request(
        url,
        data=body,
        headers=headers,
        method=method,
    )
    try:
        with urlrequest.urlopen(request, timeout=20) as response:
            raw = response.read().decode("utf-8")
    except urlerror.HTTPError:
        raise
    except urlerror.URLError as exc:
        raise RuntimeError(f"No se pudo conectar con GitHub: {exc.reason}") from exc
    return json.loads(raw) if raw else {}


def fetch_github_counter(token: str = "") -> tuple[dict[str, object], str | None]:
    url = f"{GITHUB_COUNTER_API_URL}?ref={GITHUB_BRANCH}"
    try:
        data = github_request_json(url, token=token)
    except urlerror.HTTPError as exc:
        if exc.code == 404:
            return default_counter_data(), None
        raise RuntimeError(github_error_detail(exc)) from exc

    content = str(data.get("content", "") or "")
    sha = str(data.get("sha", "") or "") or None
    try:
        decoded = base64.b64decode(content).decode("utf-8")
        counter_data = json.loads(decoded)
    except Exception:
        counter_data = {}
    return normalize_counter_data(counter_data), sha


def load_next_request_number() -> int:
    counter, _sha = fetch_github_counter()
    return int(counter.get("next_number", 1) or 1)


def save_github_counter(
    counter: dict[str, object],
    sha: str | None,
    token: str,
    message: str,
) -> None:
    content = json.dumps(counter, indent=2, ensure_ascii=False) + "\n"
    payload: dict[str, object] = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        "branch": GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha
    try:
        github_request_json(GITHUB_COUNTER_API_URL, token=token, data=payload, method="PUT")
    except urlerror.HTTPError as exc:
        raise RuntimeError(github_error_detail(exc)) from exc


def reserve_next_request_number(token: str) -> int:
    if not token:
        raise RuntimeError("GitHub token mancante.")

    for _attempt in range(GITHUB_MAX_RESERVE_ATTEMPTS):
        counter, sha = fetch_github_counter(token)
        reserved_number = int(counter.get("next_number", 1) or 1)
        next_counter = dict(counter)
        next_counter["year"] = CURRENT_YEAR
        next_counter["next_number"] = reserved_number + 1
        next_counter["updated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        next_counter["updated_by"] = os.environ.get("COMPUTERNAME", "").strip() or os.environ.get("USERNAME", "").strip()
        try:
            message = f"Reserve richiesta {CURRENT_YEAR} N. {format_request_number(reserved_number)}"
            save_github_counter(next_counter, sha, token, message)
            return reserved_number
        except RuntimeError as exc:
            if "GitHub HTTP 409" in str(exc):
                continue
            raise
    raise RuntimeError("GitHub ha ricevuto aggiornamenti simultanei. Riprova tra qualche secondo.")


def set_next_request_number(token: str, next_number: int) -> None:
    if not token:
        raise RuntimeError("GitHub token mancante.")
    counter, sha = fetch_github_counter(token)
    updated_counter = dict(counter)
    updated_counter["year"] = CURRENT_YEAR
    updated_counter["next_number"] = max(1, int(next_number))
    updated_counter["updated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    updated_counter["updated_by"] = os.environ.get("COMPUTERNAME", "").strip() or os.environ.get("USERNAME", "").strip()
    message = f"Set richiesta counter {CURRENT_YEAR} N. {format_request_number(int(updated_counter['next_number']))}"
    save_github_counter(updated_counter, sha, token, message)


def default_pdf_filename(request_number: int) -> str:
    number = format_request_number(request_number)
    return f"Richiesta di approvvigionamento N. {number} - {OUTPUT_DATE_TEXT}.pdf"


class MaterialDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, translate, material: MaterialRow | None = None) -> None:
        super().__init__(parent)
        self.translate = translate
        self.title(self.translate("material_dialog_title"))
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(bg="#161a22")

        self.result: MaterialRow | None = None

        container = ttk.Frame(self, padding=16)
        container.pack(fill="both", expand=True)

        labels = [
            self.translate("material_description"),
            self.translate("material_quantity"),
            self.translate("material_delivery"),
            self.translate("material_order"),
        ]
        for row, label in enumerate(labels):
            ttk.Label(container, text=label).grid(row=row, column=0, sticky="w", pady=(0 if row == 0 else 10, 0))

        self.description_var = tk.StringVar(value=material.description if material else "")
        self.quantity_var = tk.StringVar(value=material.quantity if material else "")
        self.delivery_var = tk.StringVar(value=material.delivery_date if material else "")
        self.order_var = tk.StringVar(value=material.order_reference if material else "")

        ttk.Entry(container, textvariable=self.description_var, width=58).grid(
            row=0, column=1, sticky="ew", padx=(12, 0)
        )
        ttk.Entry(container, textvariable=self.quantity_var, width=20).grid(
            row=1, column=1, sticky="w", padx=(12, 0), pady=(10, 0)
        )
        ttk.Entry(container, textvariable=self.delivery_var, width=20).grid(
            row=2, column=1, sticky="w", padx=(12, 0), pady=(10, 0)
        )
        ttk.Entry(container, textvariable=self.order_var, width=30).grid(
            row=3, column=1, sticky="w", padx=(12, 0), pady=(10, 0)
        )

        buttons = ttk.Frame(container)
        buttons.grid(row=4, column=0, columnspan=2, sticky="e", pady=(18, 0))
        ttk.Button(buttons, text=self.translate("cancel"), command=self.destroy).pack(side="right")
        ttk.Button(buttons, text=self.translate("accept"), command=self._save).pack(side="right", padx=(0, 8))

        container.columnconfigure(1, weight=1)
        self.bind("<Return>", lambda event: self._save())
        self.bind("<Escape>", lambda event: self.destroy())

        self.wait_visibility()
        self.focus()

    def _save(self) -> None:
        description = self.description_var.get().strip()
        quantity = self.quantity_var.get().strip()
        delivery = self.delivery_var.get().strip()
        order_reference = self.order_var.get().strip()

        if not all([description, quantity, delivery, order_reference]):
            messagebox.showwarning(
                APP_TITLE,
                self.translate("warn_material_complete"),
                parent=self,
            )
            return

        self.result = MaterialRow(
            description=description,
            quantity=quantity,
            delivery_date=delivery,
            order_reference=order_reference,
        )
        self.destroy()


class ProcurementApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.language_var = tk.StringVar(value="it")
        self.root.title(self.t("app_title"))
        self.root.geometry("1040x760")
        self.root.minsize(980, 700)
        self.root.configure(bg="#11151c")

        self.main_option_var = tk.StringVar(value="commessa")
        self.main_option_text_var = tk.StringVar()
        self.detail_vars = {key: tk.BooleanVar(value=False) for key, _ in DETAIL_OPTIONS}
        self.detail_other_text_var = tk.StringVar()
        self.status_var = tk.StringVar(
            value=self.t("status_ready")
        )
        self.request_number_var = tk.StringVar()

        self.materials: list[MaterialRow] = []

        self._configure_style()
        self._build_ui()
        self._apply_language()
        self._refresh_request_number_label()
        self._refresh_dynamic_fields()
        self.root.bind("<Control-g>", lambda event: self.generate_pdf())

    def t(self, key: str, **kwargs) -> str:
        text = UI_TEXTS[self.language_var.get()][key]
        return text.format(**kwargs) if kwargs else text

    def _configure_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")

        bg = "#11151c"
        panel = "#171c24"
        panel_alt = "#1d2430"
        text = "#f2f5f9"
        muted = "#a9b4c2"
        accent = "#244f95"
        border = "#2d3644"
        field = "#0f141b"

        style.configure(".", background=bg, foreground=text)
        style.configure("TFrame", background=bg)
        style.configure("Card.TFrame", background=panel)
        style.configure("Inner.TFrame", background=panel_alt)
        style.configure("Toolbar.TFrame", background=panel_alt)
        style.configure("TLabel", background=bg, foreground=text)
        style.configure("Muted.TLabel", background=bg, foreground=muted)
        style.configure("Card.TLabel", background=panel, foreground=text)
        style.configure("Toolbar.TLabel", background=panel_alt, foreground=text)
        style.configure("TLabelframe", background=panel, foreground=text, bordercolor=border)
        style.configure("TLabelframe.Label", background=panel, foreground=text)
        style.configure("TButton", background=accent, foreground="white", borderwidth=0, focusthickness=0, padding=(12, 8))
        style.map("TButton", background=[("active", "#2b5fb3")])
        style.configure("Primary.TButton", background="#3d7cff", foreground="white", borderwidth=0, padding=(16, 10))
        style.map("Primary.TButton", background=[("active", "#5b92ff")])
        style.configure("Secondary.TButton", background=panel_alt, foreground=text, borderwidth=1, bordercolor=border, padding=(12, 8))
        style.map("Secondary.TButton", background=[("active", "#273244")])
        style.configure("TEntry", fieldbackground=field, foreground=text, insertcolor=text, bordercolor=border)
        style.configure("TCombobox", fieldbackground=field, background=field, foreground=text, arrowcolor=text)
        style.map("TCombobox", fieldbackground=[("readonly", field)], foreground=[("readonly", text)])
        style.configure("TRadiobutton", background=panel, foreground=text)
        style.configure("TCheckbutton", background=panel, foreground=text)
        style.configure("Treeview", background=field, fieldbackground=field, foreground=text, bordercolor=border, rowheight=30)
        style.configure("Treeview.Heading", background=panel_alt, foreground=text, relief="flat")
        style.map("Treeview", background=[("selected", "#2b5fb3")], foreground=[("selected", "white")])
        style.configure("TNotebook", background=bg, borderwidth=0)
        style.configure("TNotebook.Tab", background=panel, foreground=muted, padding=(14, 8))
        style.map("TNotebook.Tab", background=[("selected", accent)], foreground=[("selected", "white")])

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=16, style="TFrame")
        container.pack(fill="both", expand=True)

        header_row = ttk.Frame(container, style="TFrame")
        header_row.pack(fill="x")

        self.logo_label = ttk.Label(header_row, style="TLabel")
        self.logo_label.pack(side="left", anchor="n", padx=(0, 12))
        self._load_ui_logo()

        header_text = ttk.Frame(header_row, style="TFrame")
        header_text.pack(side="left", fill="x", expand=True)

        self.title_label = ttk.Label(
            header_text,
            text=self.t("window_title"),
            font=("Segoe UI", 18, "bold"),
        )
        self.title_label.pack(anchor="w")
        self.subtitle_label = ttk.Label(
            header_text,
            text=self.t("subtitle"),
            style="Muted.TLabel",
        )
        self.subtitle_label.pack(anchor="w", pady=(4, 14))

        quick_actions = ttk.Frame(container, style="TFrame")
        quick_actions.pack(fill="x", pady=(0, 14))
        self.generate_button_top = ttk.Button(
            quick_actions,
            text=self.t("generate_pdf"),
            command=self.generate_pdf,
            style="Primary.TButton",
        )
        self.generate_button_top.pack(side="right")
        self.reset_button_top = ttk.Button(
            quick_actions,
            text=self.t("reset_form"),
            command=self.reset_form,
        )
        self.reset_button_top.pack(side="right", padx=(0, 8))
        self.quick_hint_label = ttk.Label(
            quick_actions,
            text=self.t("quick_hint"),
            style="Muted.TLabel",
        )
        self.quick_hint_label.pack(side="left")
        self.request_number_label = ttk.Label(
            quick_actions,
            textvariable=self.request_number_var,
            style="Muted.TLabel",
            font=("Segoe UI", 10, "bold"),
        )
        self.request_number_label.pack(side="left", padx=(18, 0))

        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True)

        self.form_tab = ttk.Frame(self.notebook, padding=12, style="TFrame")
        self.language_tab = ttk.Frame(self.notebook, padding=18, style="TFrame")
        self.notebook.add(self.form_tab, text=self.t("tab_form"))
        self.notebook.add(self.language_tab, text=self.t("tab_language"))

        top = ttk.Frame(self.form_tab, style="TFrame")
        top.pack(fill="x")

        self._build_main_options(top)
        self._build_details(top)
        self._build_materials(self.form_tab)
        self._build_footer(self.form_tab)
        self._build_language_tab()

    def _load_ui_logo(self) -> None:
        logo_path = resource_path("assets/logo_tecnidro_dark.png")
        if not logo_path.exists():
            return

        try:
            raw_logo = tk.PhotoImage(file=str(logo_path))
            self.logo_image = raw_logo.subsample(3, 3)
            self.logo_label.configure(image=self.logo_image)
        except Exception:
            self.logo_label.configure(text="TECNIDRO")

    def _build_main_options(self, parent: ttk.Frame) -> None:
        section = ttk.LabelFrame(parent, text=self.t("section_top"))
        section.pack(side="left", fill="both", expand=True)
        self.main_section = section
        self.main_radios: dict[str, ttk.Radiobutton] = {}

        for row, (key, label) in enumerate(MAIN_OPTIONS):
            radio = ttk.Radiobutton(
                section,
                text=label,
                value=key,
                variable=self.main_option_var,
                command=self._refresh_dynamic_fields,
            )
            radio.grid(row=row, column=0, sticky="w", padx=12, pady=6)
            self.main_radios[key] = radio

        self.main_extra_label = ttk.Label(
            section,
            text=self.t("main_extra"),
            style="Card.TLabel",
        )
        self.main_extra_label.grid(row=0, column=1, sticky="w", padx=(18, 6))
        self.main_extra_entry = ttk.Entry(section, textvariable=self.main_option_text_var, width=42)
        self.main_extra_entry.grid(row=1, column=1, sticky="nw", padx=(18, 12))

    def _build_details(self, parent: ttk.Frame) -> None:
        section = ttk.LabelFrame(parent, text=self.t("section_detail"))
        section.pack(side="left", fill="both", expand=True, padx=(16, 0))
        self.detail_section = section
        self.detail_checks: dict[str, ttk.Checkbutton] = {}

        for row, (key, label) in enumerate(DETAIL_OPTIONS):
            check = ttk.Checkbutton(
                section,
                text=label,
                variable=self.detail_vars[key],
                command=self._refresh_dynamic_fields,
            )
            check.grid(row=row, column=0, sticky="w", padx=12, pady=6)
            self.detail_checks[key] = check

        self.detail_extra_label = ttk.Label(section, text=self.t("detail_extra"), style="Card.TLabel")
        self.detail_extra_label.grid(row=0, column=1, sticky="w", padx=(18, 6))
        self.detail_other_entry = ttk.Entry(section, textvariable=self.detail_other_text_var, width=34)
        self.detail_other_entry.grid(row=1, column=1, sticky="nw", padx=(18, 12))

    def _build_materials(self, parent: ttk.Frame) -> None:
        section = ttk.LabelFrame(parent, text=self.t("section_materials"))
        section.pack(fill="both", expand=True, pady=(16, 0))
        self.materials_section = section

        self.materials_help_label = ttk.Label(
            section,
            text=self.t("materials_help"),
            style="Card.TLabel",
        )
        self.materials_help_label.pack(anchor="w", padx=12, pady=(10, 10))

        toolbar = ttk.Frame(section, padding=(12, 0, 12, 10), style="Toolbar.TFrame")
        toolbar.pack(fill="x", padx=12, pady=(0, 10))
        self.materials_toolbar = toolbar
        self.materials_toolbar_label = ttk.Label(
            toolbar,
            text="",
            style="Toolbar.TLabel",
            font=("Segoe UI", 10, "bold"),
        )
        self.materials_toolbar_label.pack(side="left")
        self.add_material_button = ttk.Button(
            toolbar,
            text=self.t("add_material"),
            command=self.add_material,
        )
        self.add_material_button.pack(side="right")
        self.edit_material_button = ttk.Button(
            toolbar,
            text=self.t("edit_material"),
            command=self.edit_material,
            style="Secondary.TButton",
        )
        self.edit_material_button.pack(side="right", padx=8)
        self.delete_material_button = ttk.Button(
            toolbar,
            text=self.t("delete_material"),
            command=self.delete_material,
            style="Secondary.TButton",
        )
        self.delete_material_button.pack(side="right")

        columns = ("description", "quantity", "delivery", "order")
        self.tree = ttk.Treeview(section, columns=columns, show="headings", height=13)
        self.material_columns = columns
        self.tree.column("description", width=420)
        self.tree.column("quantity", width=90, anchor="center")
        self.tree.column("delivery", width=150, anchor="center")
        self.tree.column("order", width=190, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=12, pady=(0, 10))

    def _build_footer(self, parent: ttk.Frame) -> None:
        footer = ttk.Frame(parent, style="TFrame")
        footer.pack(fill="x", pady=(14, 0))
        self.footer = footer

        self.footer_info_label = ttk.Label(
            footer,
            text=self.t("footer_info", date=DATE_TEXT),
            style="Muted.TLabel",
        )
        self.footer_info_label.pack(anchor="w")

        actions = ttk.Frame(footer)
        actions.pack(fill="x", pady=(12, 0))
        self.reset_button_bottom = ttk.Button(actions, text=self.t("reset_form"), command=self.reset_form)
        self.reset_button_bottom.pack(side="right")

        self.status_label = ttk.Label(footer, textvariable=self.status_var, style="Muted.TLabel")
        self.status_label.pack(anchor="w", pady=(10, 0))

        author_row = ttk.Frame(footer, style="TFrame")
        author_row.pack(fill="x", pady=(8, 0))
        self.author_label = ttk.Label(author_row, text="By Manuel Rodriguez", style="Muted.TLabel")
        self.author_label.pack(side="right")

    def _build_language_tab(self) -> None:
        card = ttk.Frame(self.language_tab, padding=22, style="Card.TFrame")
        card.pack(fill="x", anchor="n")
        self.language_title_label = ttk.Label(card, text=self.t("language_title"), font=("Segoe UI", 15, "bold"), style="Card.TLabel")
        self.language_title_label.pack(anchor="w")
        self.language_help_label = ttk.Label(card, text=self.t("language_help"), style="Card.TLabel")
        self.language_help_label.pack(anchor="w", pady=(6, 18))

        row = ttk.Frame(card, style="Card.TFrame")
        row.pack(fill="x")
        self.language_label = ttk.Label(row, text=self.t("language_label"), style="Card.TLabel")
        self.language_label.pack(side="left")
        self.language_combo = ttk.Combobox(
            row,
            state="readonly",
            width=18,
            values=[UI_LANGUAGES[key] for key in UI_LANGUAGES],
        )
        self.language_combo.current(list(UI_LANGUAGES).index(self.language_var.get()))
        self.language_combo.bind("<<ComboboxSelected>>", self._on_language_change)
        self.language_combo.pack(side="left", padx=(12, 0))

        admin_row = ttk.Frame(card, style="Card.TFrame")
        admin_row.pack(fill="x", pady=(22, 0))
        self.counter_admin_button = ttk.Button(
            admin_row,
            text=self.t("counter_admin_button"),
            command=self.change_request_number,
            style="Secondary.TButton",
        )
        self.counter_admin_button.pack(side="left")

    def _on_language_change(self, _event=None) -> None:
        selected_label = self.language_combo.get()
        for code, label in UI_LANGUAGES.items():
            if label == selected_label:
                self.language_var.set(code)
                break
        self._apply_language()

    def _apply_language(self) -> None:
        self.root.title(self.t("app_title"))
        self.title_label.configure(text=self.t("window_title"))
        self.subtitle_label.configure(text=self.t("subtitle"))
        self.quick_hint_label.configure(text=self.t("quick_hint"))
        self.generate_button_top.configure(text=self.t("generate_pdf"))
        self.reset_button_top.configure(text=self.t("reset_form"))
        self.reset_button_bottom.configure(text=self.t("reset_form"))
        self.counter_admin_button.configure(text=self.t("counter_admin_button"))
        self.main_section.configure(text=self.t("section_top"))
        self.detail_section.configure(text=self.t("section_detail"))
        self.materials_section.configure(text=self.t("section_materials"))
        self.main_extra_label.configure(text=self.t("main_extra"))
        self.detail_extra_label.configure(text=self.t("detail_extra"))
        self.materials_help_label.configure(text=self.t("materials_help"))
        self.materials_toolbar_label.configure(text=self.t("section_materials"))
        self.add_material_button.configure(text=self.t("add_material"))
        self.edit_material_button.configure(text=self.t("edit_material"))
        self.delete_material_button.configure(text=self.t("delete_material"))
        self.footer_info_label.configure(text=self.t("footer_info", date=DATE_TEXT))
        self._refresh_request_number_label()
        self.notebook.tab(0, text=self.t("tab_form"))
        self.notebook.tab(1, text=self.t("tab_language"))
        self.language_title_label.configure(text=self.t("language_title"))
        self.language_help_label.configure(text=self.t("language_help"))
        self.language_label.configure(text=self.t("language_label"))

        for key, radio in self.main_radios.items():
            radio.configure(text=dict(MAIN_OPTIONS)[key])
        for key, check in self.detail_checks.items():
            check.configure(text=dict(DETAIL_OPTIONS)[key])

        headings = self.t("columns")
        for column_id, heading in zip(self.material_columns, headings):
            self.tree.heading(column_id, text=heading)

        if self.status_var.get() in {
            UI_TEXTS["es"]["status_ready"],
            UI_TEXTS["it"]["status_ready"],
            UI_TEXTS["en"]["status_ready"],
        }:
            self.status_var.set(self.t("status_ready"))

    def _refresh_request_number_label(self) -> None:
        try:
            number = format_request_number(load_next_request_number())
            self.request_number_var.set(self.t("request_number", number=number))
        except Exception:
            self.request_number_var.set(self.t("request_number_error"))

    def _get_github_token(self) -> str:
        return load_github_token()

    def _check_counter_password(self, password: str) -> bool:
        digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return digest == COUNTER_ADMIN_PASSWORD_HASH

    def change_request_number(self) -> None:
        password = simpledialog.askstring(
            self.t("counter_password_title"),
            self.t("counter_password_prompt"),
            parent=self.root,
            show="*",
        )
        if password is None:
            return
        if not self._check_counter_password(password):
            messagebox.showerror(self.t("app_title"), self.t("counter_password_error"))
            return

        try:
            current_number = load_next_request_number()
        except Exception:
            current_number = 1

        next_number = simpledialog.askinteger(
            self.t("counter_number_title"),
            self.t("counter_number_prompt"),
            parent=self.root,
            minvalue=1,
            maxvalue=9999,
            initialvalue=current_number,
        )
        if next_number is None:
            return

        token = self._get_github_token()
        if not token:
            messagebox.showerror(self.t("app_title"), self.t("github_token_missing"))
            return

        try:
            set_next_request_number(token, next_number)
        except Exception as exc:
            messagebox.showerror(self.t("app_title"), self.t("github_counter_error", error=exc))
            self._refresh_request_number_label()
            return

        self._refresh_request_number_label()
        number_text = format_request_number(next_number)
        self.status_var.set(self.t("counter_update_ok", number=number_text))
        messagebox.showinfo(self.t("app_title"), self.t("counter_update_ok", number=number_text))

    def _refresh_dynamic_fields(self) -> None:
        main_needs_text = self.main_option_var.get() in {"commessa", "altro"}
        if main_needs_text:
            self.main_extra_entry.state(["!disabled"])
        else:
            self.main_option_text_var.set("")
            self.main_extra_entry.state(["disabled"])

        if self.detail_vars["altro"].get():
            self.detail_other_entry.state(["!disabled"])
        else:
            self.detail_other_text_var.set("")
            self.detail_other_entry.state(["disabled"])

    def add_material(self) -> None:
        dialog = MaterialDialog(self.root, self.t)
        self.root.wait_window(dialog)
        if dialog.result is None:
            return
        self.materials.append(dialog.result)
        self._refresh_materials()
        self.status_var.set(self.t("status_material_added"))

    def edit_material(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo(self.t("app_title"), self.t("warn_select_edit"))
            return

        index = self.tree.index(selected[0])
        dialog = MaterialDialog(self.root, self.t, self.materials[index])
        self.root.wait_window(dialog)
        if dialog.result is None:
            return

        self.materials[index] = dialog.result
        self._refresh_materials()
        self.status_var.set(self.t("status_material_updated"))

    def delete_material(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo(self.t("app_title"), self.t("warn_select_delete"))
            return

        index = self.tree.index(selected[0])
        del self.materials[index]
        self._refresh_materials()
        self.status_var.set(self.t("status_material_deleted"))

    def _refresh_materials(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        for material in self.materials:
            self.tree.insert(
                "",
                "end",
                values=(
                    material.description,
                    material.quantity,
                    material.delivery_date,
                    material.order_reference,
                ),
            )

    def reset_form(self) -> None:
        self.main_option_var.set("commessa")
        self.main_option_text_var.set("")
        self.detail_other_text_var.set("")
        for variable in self.detail_vars.values():
            variable.set(False)
        self.materials.clear()
        self._refresh_materials()
        self._refresh_dynamic_fields()
        self.status_var.set(self.t("status_form_reset"))

    def validate_form(self) -> bool:
        if self.main_option_var.get() in {"commessa", "altro"} and not self.main_option_text_var.get().strip():
            messagebox.showwarning(
                self.t("app_title"),
                self.t("warn_main_extra"),
            )
            return False

        if self.detail_vars["altro"].get() and not self.detail_other_text_var.get().strip():
            messagebox.showwarning(
                self.t("app_title"),
                self.t("warn_detail_extra"),
            )
            return False

        if not self.materials:
            messagebox.showwarning(self.t("app_title"), self.t("warn_need_materials"))
            return False

        return True

    def generate_pdf(self) -> None:
        if not self.validate_form():
            return

        try:
            preview_number = load_next_request_number()
        except Exception as exc:
            messagebox.showerror(self.t("app_title"), self.t("github_counter_error", error=exc))
            self._refresh_request_number_label()
            return

        default_name = default_pdf_filename(preview_number)
        output_path = filedialog.asksaveasfilename(
            title=self.t("save_pdf_title"),
            defaultextension=".pdf",
            initialfile=default_name,
            filetypes=[("PDF", "*.pdf")],
        )
        if not output_path:
            return

        token = self._get_github_token()
        if not token:
            messagebox.showerror(self.t("app_title"), self.t("github_token_missing"))
            return

        self.status_var.set(self.t("github_reserving"))
        self.root.update_idletasks()
        try:
            request_number = reserve_next_request_number(token)
        except Exception as exc:
            messagebox.showerror(self.t("app_title"), self.t("github_counter_error", error=exc))
            self._refresh_request_number_label()
            return

        output_path = str(Path(output_path).with_name(default_pdf_filename(request_number)))
        try:
            generate_procurement_pdf(
                output_path=Path(output_path),
                selected_main_option=self.main_option_var.get(),
                main_option_text=self.main_option_text_var.get().strip(),
                detail_flags={key: var.get() for key, var in self.detail_vars.items()},
                detail_other_text=self.detail_other_text_var.get().strip(),
                materials=self.materials,
                request_number=request_number,
            )
        except Exception as exc:
            messagebox.showerror(self.t("app_title"), self.t("pdf_error", error=exc))
            self._refresh_request_number_label()
            return

        self._refresh_request_number_label()
        self.status_var.set(self.t("status_pdf_generated", path=output_path))
        messagebox.showinfo(self.t("app_title"), self.t("pdf_ok", path=output_path))


def wrap_text(pdf: canvas.Canvas, text: str, max_width: float, font_name: str, font_size: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]

    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if stringWidth(candidate, font_name, font_size) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_checkbox(
    pdf: canvas.Canvas,
    x: float,
    y: float,
    label: str,
    checked: bool,
    extra_text: str = "",
    extra_text_x: float | None = None,
) -> None:
    size = 9
    pdf.setStrokeColor(TEXT_COLOR)
    pdf.rect(x, y - size + 1, size, size)
    if checked:
        pdf.setLineWidth(1.2)
        pdf.line(x + 2, y - size + 3, x + size - 2, y - 2)
        pdf.line(x + 2, y - 2, x + size - 2, y - size + 3)
        pdf.setLineWidth(1)

    pdf.setFillColor(TEXT_COLOR)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(x + 15, y - 8, label)
    if extra_text:
        text_x = extra_text_x if extra_text_x is not None else x + 15 + stringWidth(label, "Helvetica", 10) + 8
        pdf.drawString(text_x, y - 8, extra_text)
    pdf.setStrokeColor(colors.black)


def draw_signature(pdf: canvas.Canvas, x: float, y: float) -> None:
    signature_path = resource_path("assets/signature_rodriguez.png")
    if not signature_path.exists():
        return

    signature = ImageReader(str(signature_path))
    image_width, image_height = signature.getSize()
    max_width = 48 * mm
    max_height = 12 * mm
    scale = min(max_width / image_width, max_height / image_height)
    draw_width = image_width * scale
    draw_height = image_height * scale
    draw_y = y + (max_height - draw_height) / 2
    pdf.drawImage(signature, x, draw_y, width=draw_width, height=draw_height, mask="auto")


def draw_logo(pdf: canvas.Canvas, x: float, y: float, width: float, height: float) -> None:
    logo_path = resource_path("assets/logo_tecnidro.png")
    if not logo_path.exists():
        return

    logo = ImageReader(str(logo_path))
    pdf.drawImage(logo, x, y, width=width, height=height, preserveAspectRatio=True, mask="auto")


def draw_material_table_header(pdf: canvas.Canvas, y: float) -> float:
    left = PAGE_LEFT
    widths = [97 * mm, 20 * mm, 33 * mm, 27 * mm]
    headers = ["Descrizione", "Q.t.", "Consegna richiesta", "Ordine n. del"]

    pdf.setFillColor(TABLE_HEADER_FILL)
    pdf.roundRect(left, y - 16, sum(widths), 18, 4, fill=1, stroke=0)
    pdf.setFillColor(TEXT_COLOR)
    pdf.setFont("Helvetica-Bold", 9)

    cursor = left
    for width, header in zip(widths, headers):
        pdf.setStrokeColor(LINE_COLOR)
        pdf.rect(cursor, y - 16, width, 18, fill=0, stroke=1)
        pdf.drawString(cursor + 4, y - 10, header)
        cursor += width

    pdf.setStrokeColor(colors.black)
    return y - 18


def draw_section_card(
    pdf: canvas.Canvas,
    x: float,
    top_y: float,
    width: float,
    height: float,
    title: str,
) -> None:
    pdf.setFillColor(LIGHT_FILL)
    pdf.setStrokeColor(LINE_COLOR)
    pdf.roundRect(x, top_y - height, width, height, 7, fill=1, stroke=1)

    pdf.setFillColor(ACCENT_COLOR)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(x + 5 * mm, top_y - 11, title)
    pdf.setStrokeColor(colors.HexColor("#d7e0ec"))
    pdf.setLineWidth(1)
    pdf.line(x + 5 * mm, top_y - 16, x + width - 5 * mm, top_y - 16)

    pdf.setFillColor(TEXT_COLOR)
    pdf.setStrokeColor(colors.black)


def generate_procurement_pdf(
    output_path: Path,
    selected_main_option: str,
    main_option_text: str,
    detail_flags: dict[str, bool],
    detail_other_text: str,
    materials: list[MaterialRow],
    request_number: int,
) -> None:
    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    page_width, page_height = A4
    request_number_text = f"N. {format_request_number(request_number)}"

    def draw_header(current_y: float) -> float:
        left = PAGE_LEFT
        right = page_width - PAGE_RIGHT
        header_bottom = current_y - 20 * mm

        pdf.setFillColor(colors.white)
        pdf.setStrokeColor(LINE_COLOR)
        pdf.setLineWidth(1)
        pdf.roundRect(left, header_bottom, right - left, 32 * mm, 7, fill=1, stroke=1)
        pdf.setFillColor(ACCENT_COLOR)
        pdf.roundRect(left, header_bottom + 27 * mm, right - left, 5 * mm, 7, fill=1, stroke=0)
        pdf.setFillColor(colors.HexColor("#d7e0ec"))
        pdf.line(left, header_bottom + 9 * mm, right, header_bottom + 9 * mm)

        draw_logo(pdf, left + 3.5 * mm, header_bottom + 11 * mm, 26 * mm, 12 * mm)

        pdf.setFillColor(ACCENT_COLOR)
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(left + 52 * mm, header_bottom + 19 * mm, "Richiesta di Approvvigionamento")
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawRightString(right - 4 * mm, header_bottom + 20 * mm, request_number_text)
        pdf.setFillColor(MUTED_TEXT)
        pdf.setFont("Helvetica", 9)
        pdf.drawString(left + 52 * mm, header_bottom + 12.5 * mm, "Sistema Gestione Integrato")
        pdf.setStrokeColor(LINE_COLOR)
        pdf.line(left + 52 * mm, header_bottom + 10 * mm, right - 4 * mm, header_bottom + 10 * mm)
        pdf.setFillColor(MUTED_TEXT)
        pdf.setFont("Helvetica", 9)
        pdf.drawString(left + 4 * mm, header_bottom + 3 * mm, "Modulo aziendale di approvvigionamento")
        pdf.drawRightString(right - 4 * mm, header_bottom + 3 * mm, DATE_TEXT)
        pdf.setStrokeColor(colors.black)
        pdf.setLineWidth(1)
        return header_bottom - 8 * mm

    y = draw_header(page_height - 18 * mm)

    draw_section_card(pdf, PAGE_LEFT, y + 2, PAGE_WIDTH_CONTENT, 55 * mm, "Tipologia")
    y -= 13 * mm

    extra_text_x = 112 * mm
    for key, label in MAIN_OPTIONS:
        extra = ""
        if key == selected_main_option and key in {"commessa", "altro"}:
            extra = main_option_text
        draw_checkbox(
            pdf,
            18 * mm,
            y,
            label,
            checked=selected_main_option == key,
            extra_text=extra,
            extra_text_x=extra_text_x if key in {"commessa", "altro"} else None,
        )
        if key in {"commessa", "altro"}:
            pdf.setStrokeColor(LINE_COLOR)
            pdf.line(extra_text_x - 2 * mm, y - 9, 186 * mm, y - 9)
            pdf.setStrokeColor(colors.black)
        y -= 7 * mm

    y -= 2 * mm
    draw_section_card(pdf, PAGE_LEFT, y + 2, PAGE_WIDTH_CONTENT, 36 * mm, "Particolare")
    y -= 13 * mm

    left_x = 18 * mm
    right_x = 96 * mm
    detail_y = y

    for index, (key, label) in enumerate(DETAIL_OPTIONS[:3]):
        draw_checkbox(pdf, left_x, detail_y - index * 7 * mm, label, detail_flags.get(key, False))

    for index, (key, label) in enumerate(DETAIL_OPTIONS[3:]):
        extra = detail_other_text if key == "altro" and detail_flags.get(key, False) else ""
        draw_checkbox(
            pdf,
            right_x,
            detail_y - index * 7 * mm,
            label,
            detail_flags.get(key, False),
            extra_text=extra,
        )
        if key == "altro":
            pdf.setStrokeColor(LINE_COLOR)
            pdf.line(right_x + 16 * mm, detail_y - index * 7 * mm - 9, 186 * mm, detail_y - index * 7 * mm - 9)
            pdf.setStrokeColor(colors.black)

    y = detail_y - 33 * mm
    pdf.setFont("Helvetica-Bold", 11)
    pdf.setFillColor(ACCENT_COLOR)
    pdf.roundRect(PAGE_LEFT, y - 6, PAGE_WIDTH_CONTENT, 8 * mm, 4, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.drawString(18 * mm, y - 1, "Distinta")
    y -= 10 * mm

    y = draw_material_table_header(pdf, y)
    pdf.setFont("Helvetica", 9)

    left = PAGE_LEFT
    widths = [97 * mm, 20 * mm, 33 * mm, 27 * mm]
    line_height = 5 * mm

    def ensure_space(required_height: float) -> None:
        nonlocal y
        if y - required_height < 42 * mm:
            pdf.showPage()
            y = draw_header(page_height - 18 * mm)
            pdf.setFont("Helvetica-Bold", 11)
            pdf.setFillColor(ACCENT_COLOR)
            pdf.roundRect(PAGE_LEFT, y - 6, PAGE_WIDTH_CONTENT, 8 * mm, 4, fill=1, stroke=0)
            pdf.setFillColor(colors.white)
            pdf.drawString(18 * mm, y - 1, "Distinta (continua)")
            y -= 8 * mm
            y = draw_material_table_header(pdf, y)
            pdf.setFont("Helvetica", 9)

    row_index = 0
    for material in materials:
        description_lines = wrap_text(pdf, material.description, widths[0] - 8, "Helvetica", 9)
        order_lines = wrap_text(pdf, material.order_reference, widths[3] - 8, "Helvetica", 9)
        row_height = max(len(description_lines), len(order_lines), 1) * line_height + 4
        ensure_space(row_height)

        cursor = left
        if row_index % 2 == 0:
            pdf.setFillColor(colors.white)
        else:
            pdf.setFillColor(SOFT_BLUE)
        pdf.setStrokeColor(LINE_COLOR)
        pdf.rect(cursor, y - row_height, widths[0], row_height, fill=1, stroke=1)
        pdf.setFillColor(TEXT_COLOR)
        text_y = y - 11
        for line in description_lines:
            pdf.drawString(cursor + 4, text_y, line)
            text_y -= line_height

        cursor += widths[0]
        pdf.rect(cursor, y - row_height, widths[1], row_height, fill=0, stroke=1)
        pdf.drawCentredString(cursor + widths[1] / 2, y - 11, material.quantity)

        cursor += widths[1]
        pdf.rect(cursor, y - row_height, widths[2], row_height, fill=0, stroke=1)
        pdf.drawCentredString(cursor + widths[2] / 2, y - 11, material.delivery_date)

        cursor += widths[2]
        pdf.rect(cursor, y - row_height, widths[3], row_height, fill=0, stroke=1)
        order_y = y - 11
        for line in order_lines[:2]:
            pdf.drawCentredString(cursor + widths[3] / 2, order_y, line)
            order_y -= line_height

        pdf.setStrokeColor(colors.black)
        y -= row_height
        row_index += 1

    ensure_space(40 * mm)
    y -= 7 * mm

    pdf.setFillColor(TEXT_COLOR)
    pdf.setFont("Helvetica", 10)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(15 * mm, y, "Note:")
    pdf.setStrokeColor(LINE_COLOR)
    pdf.line(27 * mm, y - 2, 186 * mm, y - 2)
    y -= 8 * mm

    pdf.drawString(15 * mm, y, "Imballo:")
    pdf.line(31 * mm, y - 2, 186 * mm, y - 2)
    y -= 10 * mm

    shipping_y = y
    shipping_baseline = shipping_y - 8
    pdf.setFillColor(TEXT_COLOR)
    pdf.drawString(15 * mm, shipping_baseline, "Spedizione a")
    draw_checkbox(pdf, 40 * mm, shipping_baseline + 8, "Tecnidro", True)
    draw_checkbox(pdf, 82 * mm, shipping_baseline + 8, "Altro destinatario", False)
    pdf.setStrokeColor(LINE_COLOR)
    pdf.line(126 * mm, shipping_baseline + 4, 186 * mm, shipping_baseline + 4)
    y -= 12 * mm

    requester_y = y
    pdf.setFillColor(TEXT_COLOR)
    pdf.drawString(15 * mm, requester_y - 5, f"Data: {DATE_TEXT}")
    pdf.drawString(58 * mm, requester_y - 5, "Richiedente:")
    checkbox_y = requester_y + 3
    draw_checkbox(pdf, 88 * mm, checkbox_y, "MAG", False)
    draw_checkbox(pdf, 110 * mm, checkbox_y, "Altro Ente", True)
    pdf.drawString(145 * mm, requester_y - 5, "Rodriguez Manuel Mateo")
    y -= 13 * mm

    pdf.drawString(58 * mm, y, "Firma:")
    draw_signature(pdf, 70 * mm, y - 4.5 * mm)
    y -= 13 * mm

    pdf.drawString(15 * mm, y, "Per ricevuta:")
    pdf.setStrokeColor(LINE_COLOR)
    pdf.line(45 * mm, y - 2, 186 * mm, y - 2)

    pdf.setFont("Helvetica", 8)
    pdf.setFillColor(colors.HexColor("#666666"))
    pdf.drawCentredString(page_width / 2, 10 * mm, FOOTER_TEXT)
    pdf.save()


def main() -> None:
    root = tk.Tk()
    ProcurementApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
