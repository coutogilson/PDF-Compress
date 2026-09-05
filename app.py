import os
import sys
import json
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import scrolledtext
import threading
import webbrowser
from PIL import Image
import io

APP_VERSION = "1.1.0"

DEFAULTS = {
    "quality": 85,
    "dpi": 150,
    "method": "auto",
    "optimize": False,
}


def get_config_path():
    """Retorna o caminho do arquivo de configuração por SO."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        folder = os.path.join(base, "PDF-Compress")
    else:
        folder = os.path.join(os.path.expanduser("~"), ".config", "pdf-compress")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "config.json")

class PDFCompressor:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Compressor de PDF v{APP_VERSION} - Alta Qualidade")
        self.root.geometry("780x720")
        self.root.minsize(680, 640)
        self.root.resizable(True, True)
        
        # Carregar pré-definições salvas
        cfg = self.load_config()

        # Variáveis
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.compression_level = tk.IntVar(value=cfg["quality"])
        self.dpi_level = tk.IntVar(value=cfg["dpi"])
        self.optimize_var = tk.BooleanVar(value=cfg["optimize"])
        self.is_compressing = False
        self.last_output_path = None
        self._initial_method = cfg["method"]

        self.setup_ui()

        # Auto-salvar pré-definições ao fechar
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Compressor de PDF", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Seleção do arquivo de entrada
        ttk.Label(main_frame, text="Arquivo PDF:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_file).grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(main_frame, text="Selecionar", command=self.select_input_file, width=12).grid(row=1, column=2, pady=5, sticky=tk.E)

        # Seleção do arquivo de saída
        ttk.Label(main_frame, text="Salvar como:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_file).grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(main_frame, text="Destino", command=self.select_output_file, width=12).grid(row=2, column=2, pady=5, sticky=tk.E)
        
        # Opções de compressão
        options_frame = ttk.LabelFrame(main_frame, text="Opções de Compressão", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)
        options_frame.columnconfigure(1, weight=1)
        
        # Qualidade da imagem (JPEG)
        ttk.Label(options_frame, text="Qualidade JPEG:").grid(row=0, column=0, sticky=tk.W, pady=5)
        quality_scale = ttk.Scale(options_frame, from_=50, to=95, variable=self.compression_level, 
                                  orient=tk.HORIZONTAL, length=200)
        quality_scale.grid(row=0, column=1, padx=10, pady=5, sticky=(tk.W, tk.E))
        ttk.Label(options_frame, textvariable=self.compression_level).grid(row=0, column=2, padx=5, pady=5)
        
        # DPI para imagens (passos de 10, com marcas em 150 e 300)
        ttk.Label(options_frame, text="DPI (resolução):").grid(row=1, column=0, sticky=tk.W, pady=5)
        dpi_scale = ttk.Scale(options_frame, from_=70, to=300, variable=self.dpi_level,
                             orient=tk.HORIZONTAL, command=self._round_dpi)
        dpi_scale.grid(row=1, column=1, padx=10, pady=5, sticky=(tk.W, tk.E))
        self.dpi_value_label = ttk.Label(options_frame, text=str(self.dpi_level.get()), width=4)
        self.dpi_value_label.grid(row=1, column=2, padx=5, pady=5)

        # Régua de DPI com ticks nas posições exatas (70, 150 e 300)
        self.dpi_ruler = tk.Canvas(options_frame, height=22, highlightthickness=0)
        self.dpi_ruler.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=10)
        self.dpi_ruler.bind("<Configure>", self._draw_dpi_ruler)
        self.dpi_ruler.bind("<Button-1>", self._dpi_ruler_click)
        self._update_dpi_label()

        # Método de compressão
        ttk.Label(options_frame, text="Método:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.compression_method = tk.StringVar(value=self._initial_method)
        method_frame = ttk.Frame(options_frame)
        method_frame.grid(row=3, column=1, columnspan=2, sticky=tk.W, padx=10, pady=5)
        ttk.Radiobutton(method_frame, text="Automático", value="auto",
                       variable=self.compression_method).grid(row=0, column=0, padx=(0, 10))
        ttk.Radiobutton(method_frame, text="GhostScript", value="ghostscript",
                       variable=self.compression_method).grid(row=0, column=1, padx=(0, 10))
        ttk.Radiobutton(method_frame, text="Python (PyMuPDF)", value="python",
                       variable=self.compression_method).grid(row=0, column=2)

        # Informações sobre os métodos de compressão
        info_frame = ttk.LabelFrame(options_frame, text="Sobre os métodos", padding="8")
        info_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 5))
        info_frame.columnconfigure(0, weight=1)

        gs_text = ("GhostScript: melhor qualidade para imagens e mantém a individualidade "
                   "das imagens e textos selecionáveis, mas os arquivos ficam maiores e "
                   "requer a ferramenta instalada no dispositivo.")
        py_text = ("Python (PyMuPDF): gera arquivos menores, porém renderiza cada página "
                   "como uma única imagem — os textos deixam de ser selecionáveis e as "
                   "imagens perdem a individualidade no PDF.")

        ttk.Label(info_frame, text=gs_text, wraplength=560, justify=tk.LEFT,
                 foreground="#1a5276").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=py_text, wraplength=560, justify=tk.LEFT,
                 foreground="#7b4b00").grid(row=1, column=0, sticky=tk.W, pady=2)

        gs_link = ttk.Label(info_frame, text="⬇ Baixar GhostScript (oficial)",
                           foreground="#0563c1", cursor="hand2")
        gs_link.grid(row=2, column=0, sticky=tk.W, pady=(4, 0))
        gs_link.bind("<Button-1>", lambda e: webbrowser.open(
            "https://ghostscript.com/releases/gsdnld.html"))

        # Checkbox para otimização adicional (desmarcado por padrão)
        ttk.Checkbutton(options_frame, text="Otimizar imagens (reduzir cores)",
                       variable=self.optimize_var).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Botões de ação
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=4, column=0, columnspan=3, pady=15)

        self.compress_button = ttk.Button(action_frame, text="Comprimir PDF",
                                         command=self.start_compression, width=18)
        self.compress_button.grid(row=0, column=0, padx=4)

        self.clear_button = ttk.Button(action_frame, text="Limpar",
                                      command=self.clear_fields, width=12)
        self.clear_button.grid(row=0, column=1, padx=4)

        self.open_pdf_button = ttk.Button(action_frame, text="📄 Abrir PDF",
                                         command=self.open_output_pdf, width=14,
                                         state='disabled')
        self.open_pdf_button.grid(row=0, column=2, padx=4)

        self.open_folder_button = ttk.Button(action_frame, text="📁 Abrir pasta",
                                            command=self.open_output_folder, width=14,
                                            state='disabled')
        self.open_folder_button.grid(row=0, column=3, padx=4)

        self.restore_button = ttk.Button(action_frame, text="Restaurar padrões",
                                        command=self.restore_defaults, width=18)
        self.restore_button.grid(row=0, column=4, padx=4)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Log de mensagens
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=60, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Ajustar tamanho
        self.root.update()
        main_frame.rowconfigure(6, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
    def log_message(self, message):
        """Adiciona mensagem ao log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()

    def _round_dpi(self, value):
        """Arredonda o DPI para o múltiplo de 10, com snap magnético em 150 e 300."""
        dpi = float(value)
        # Snap: se estiver a até 6 de distância de um valor-chave, "gruda" nele
        for snap in (150, 300):
            if abs(dpi - snap) <= 6:
                dpi = snap
                break
        dpi = int(round(dpi / 10.0) * 10)
        dpi = max(70, min(300, dpi))
        if self.dpi_level.get() != dpi:
            self.dpi_level.set(dpi)
        self._update_dpi_label()

    DPI_MIN = 70
    DPI_MAX = 300
    DPI_MARKS = (70, 150, 300)

    def _draw_dpi_ruler(self, event=None):
        """Desenha a régua com ticks e rótulos nas posições proporcionais exatas."""
        c = self.dpi_ruler
        c.delete("all")
        width = c.winfo_width()
        if width < 2:
            return
        span = self.DPI_MAX - self.DPI_MIN
        for mark in self.DPI_MARKS:
            x = (mark - self.DPI_MIN) / span * (width - 2) + 1
            major = mark in (150, 300)
            color = "#1a5276" if major else "#999999"
            # tick
            c.create_line(x, 2, x, 12 if major else 8, fill=color,
                          width=2 if major else 1)
            # rótulo
            c.create_text(x, 18, text=str(mark),
                          font=("Arial", 8, "bold" if major else "normal"),
                          fill=color)
        # linha de base
        c.create_line(1, 12, width - 1, 12, fill="#dddddd")

    def _dpi_ruler_click(self, event):
        """Clicar na régua posiciona o slider no DPI correspondente."""
        width = self.dpi_ruler.winfo_width()
        if width < 2:
            return
        frac = min(max((event.x - 1) / (width - 2), 0.0), 1.0)
        self.dpi_level.set(self.DPI_MIN + frac * (self.DPI_MAX - self.DPI_MIN))
        self._round_dpi(self.dpi_level.get())

    def _update_dpi_label(self):
        """Atualiza o rótulo do DPI, destacando 150 e 300."""
        dpi = self.dpi_level.get()
        destaque = dpi in (150, 300)
        self.dpi_value_label.config(
            text=str(dpi),
            font=("Arial", 9, "bold") if destaque else ("Arial", 9, "normal"),
            foreground="#1a5276" if destaque else "#000000",
        )

    def load_config(self):
        """Carrega pré-definições salvas; retorna DEFAULTS se não existir."""
        try:
            with open(get_config_path(), "r", encoding="utf-8") as f:
                data = json.load(f)
            cfg = dict(DEFAULTS)
            for key in DEFAULTS:
                if key in data:
                    cfg[key] = data[key]
            return cfg
        except Exception:
            return dict(DEFAULTS)

    def save_config(self):
        """Salva as pré-definições atuais."""
        try:
            data = {
                "quality": int(self.compression_level.get()),
                "dpi": int(self.dpi_level.get()),
                "method": self.compression_method.get(),
                "optimize": bool(self.optimize_var.get()),
            }
            with open(get_config_path(), "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Não foi possível salvar as pré-definições: {e}")

    def on_close(self):
        """Salva pré-definições e fecha a aplicação."""
        self.save_config()
        self.root.destroy()

    def restore_defaults(self):
        """Restaura as pré-definições padrão e remove o arquivo de configuração."""
        self.compression_level.set(DEFAULTS["quality"])
        self.dpi_level.set(DEFAULTS["dpi"])
        self.compression_method.set(DEFAULTS["method"])
        self.optimize_var.set(DEFAULTS["optimize"])
        self._update_dpi_label()
        try:
            os.remove(get_config_path())
        except OSError:
            pass
        self.log_message("Pré-definições restauradas para os padrões.")

    def _open_path(self, path):
        """Abre um arquivo ou pasta no aplicativo padrão do SO."""
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def open_output_pdf(self):
        """Abre o PDF comprimido gerado por último."""
        if self.last_output_path and os.path.exists(self.last_output_path):
            self._open_path(self.last_output_path)
        else:
            messagebox.showwarning("Aviso", "Nenhum PDF comprimido disponível.")

    def open_output_folder(self):
        """Abre a pasta onde está o PDF comprimido."""
        if self.last_output_path and os.path.exists(self.last_output_path):
            self._open_path(os.path.dirname(self.last_output_path))
        else:
            messagebox.showwarning("Aviso", "Nenhum PDF comprimido disponível.")

    def select_input_file(self):
        """Seleciona arquivo PDF de entrada"""
        filename = filedialog.askopenfilename(
            title="Selecionar arquivo PDF",
            filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            # Sugerir nome para arquivo de saída
            base_name = os.path.splitext(filename)[0]
            self.output_file.set(f"{base_name}_comprimido.pdf")
            self.log_message(f"Arquivo selecionado: {os.path.basename(filename)}")
    
    def select_output_file(self):
        """Seleciona arquivo de saída"""
        filename = filedialog.asksaveasfilename(
            title="Salvar arquivo PDF como",
            defaultextension=".pdf",
            filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")]
        )
        if filename:
            self.output_file.set(filename)
            self.log_message(f"Destino definido: {os.path.basename(filename)}")
    
    def clear_fields(self):
        """Limpa os campos do formulário"""
        self.input_file.set("")
        self.output_file.set("")
        self.last_output_path = None
        self.open_pdf_button.config(state='disabled')
        self.open_folder_button.config(state='disabled')
        self.log_text.delete(1.0, tk.END)
        self.progress.stop()
        self.progress['value'] = 0
        self.log_message("Campos limpos")
    
    def compress_pdf(self, input_path, output_path, quality, dpi, optimize):
        """Comprime o PDF renderizando cada página como imagem JPEG otimizada.

        Usa PyMuPDF (fitz) para rasterizar as páginas no DPI escolhido,
        recomprime com Pillow e reconstrói o PDF preservando as dimensões
        originais de cada página.
        """
        try:
            import pymupdf

            src_doc = pymupdf.open(input_path)
            out_doc = pymupdf.open()

            total_pages = src_doc.page_count
            self.log_message(f"Processando {total_pages} páginas...")

            for page_num in range(total_pages):
                self.log_message(f"Processando página {page_num + 1}/{total_pages}")

                page = src_doc.load_page(page_num)
                rect = page.rect

                # Renderiza a página inteira no DPI desejado
                pix = page.get_pixmap(dpi=dpi, alpha=False)
                img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

                # Otimizar cores se solicitado
                if optimize:
                    img = img.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
                    img = img.convert("RGB")

                # Comprime como JPEG
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=quality, optimize=True)
                jpeg_bytes = buffer.getvalue()

                # Recria a página com o tamanho original e insere a imagem
                new_page = out_doc.new_page(width=rect.width, height=rect.height)
                new_page.insert_image(rect, stream=jpeg_bytes)

                pix = None
                img = None

            # Salvar PDF comprimido com limpeza de objetos e deflate
            out_doc.save(output_path, garbage=4, deflate=True)
            out_doc.close()
            src_doc.close()

            # Calcular redução de tamanho
            original_size = os.path.getsize(input_path)
            compressed_size = os.path.getsize(output_path)
            reduction = ((original_size - compressed_size) / original_size) * 100

            self.log_message(f"Compressão concluída!")
            self.log_message(f"Tamanho original: {original_size / 1024:.2f} KB")
            self.log_message(f"Tamanho comprimido: {compressed_size / 1024:.2f} KB")
            self.log_message(f"Redução: {reduction:.1f}%")

            return True

        except Exception as e:
            self.log_message(f"Erro durante compressão: {str(e)}")
            return False
    
    def find_ghostscript(self):
        """Localiza o executável do GhostScript. Retorna o caminho ou None."""
        import subprocess
        import sys
        import glob
        import shutil

        if sys.platform == 'win32':
            # 1) Verificar no PATH
            for exe in ('gswin64c', 'gswin32c'):
                found = shutil.which(exe)
                if found:
                    return found
            # 2) Procurar nos diretórios de instalação padrão (versão mais recente primeiro)
            possible_paths = [
                r'C:\Program Files\gs\gs*\bin\gswin64c.exe',
                r'C:\Program Files\gs\gs*\bin\gswin32c.exe',
                r'C:\Program Files (x86)\gs\gs*\bin\gswin32c.exe',
            ]
            for path_pattern in possible_paths:
                matches = sorted(glob.glob(path_pattern), reverse=True)
                if matches:
                    return matches[0]
            return None
        else:  # Linux/Mac
            return shutil.which('gs')

    def compress_with_ghostscript(self, input_path, output_path, quality, dpi):
        """Método alternativo usando GhostScript (se disponível)"""
        import subprocess

        try:
            gs_path = self.find_ghostscript()

            if not gs_path:
                self.log_message("GhostScript não encontrado no sistema.")
                return False

            if gs_path:
                # Mapear a qualidade para o perfil do GhostScript
                if quality >= 85:
                    pdf_settings = '/prepress'   # alta qualidade (300 dpi)
                elif quality >= 70:
                    pdf_settings = '/printer'    # boa qualidade (300 dpi)
                elif quality >= 55:
                    pdf_settings = '/ebook'      # média qualidade (150 dpi)
                else:
                    pdf_settings = '/screen'     # baixa qualidade (72 dpi)

                cmd = [
                    gs_path,
                    '-sDEVICE=pdfwrite',
                    f'-dPDFSETTINGS={pdf_settings}',
                    f'-dNOPAUSE',
                    f'-dQUIET',
                    f'-dBATCH',
                    f'-dColorImageResolution={dpi}',
                    f'-dGrayImageResolution={dpi}',
                    f'-dMonoImageResolution={dpi}',
                    f'-dCompatibilityLevel=1.4',
                    f'-sOutputFile={output_path}',
                    input_path
                ]

                self.log_message(f"Usando GhostScript para compressão (perfil {pdf_settings})...")
                self.log_message(f"Executável: {gs_path}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    self.log_message(f"GhostScript retornou erro (código {result.returncode}):")
                    if result.stderr:
                        self.log_message(result.stderr.strip()[:500])
                    return False

                if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                    self.log_message("GhostScript não gerou um arquivo de saída válido.")
                    return False

                original_size = os.path.getsize(input_path)
                compressed_size = os.path.getsize(output_path)
                reduction = ((original_size - compressed_size) / original_size) * 100

                self.log_message(f"Compressão concluída!")
                self.log_message(f"Tamanho original: {original_size / 1024:.2f} KB")
                self.log_message(f"Tamanho comprimido: {compressed_size / 1024:.2f} KB")
                self.log_message(f"Redução: {reduction:.1f}%")
                return True
            
        except Exception as e:
            self.log_message(f"GhostScript não disponível: {str(e)}")
            return False
        return False
    
    def start_compression(self):
        """Inicia o processo de compressão em thread separada"""
        if self.is_compressing:
            messagebox.showwarning("Aviso", "Uma compressão já está em andamento!")
            return
        
        input_path = self.input_file.get()
        output_path = self.output_file.get()
        
        if not input_path or not os.path.exists(input_path):
            messagebox.showerror("Erro", "Selecione um arquivo PDF válido!")
            return
            
        if not output_path:
            messagebox.showerror("Erro", "Defina o caminho para salvar o arquivo!")
            return
            
        if output_path == input_path:
            messagebox.showerror("Erro", "O arquivo de saída não pode ser o mesmo que o de entrada!")
            return
        
        # Iniciar compressão em thread separada
        self.is_compressing = True
        self.compress_button.config(state='disabled')
        self.progress.start(10)
        self.log_message("\n" + "="*50)
        self.log_message("Iniciando compressão...")
        
        thread = threading.Thread(target=self._compression_task, args=(input_path, output_path))
        thread.daemon = True
        thread.start()
    
    def _compression_task(self, input_path, output_path):
        """Tarefa de compressão em background"""
        try:
            quality = self.compression_level.get()
            dpi = self.dpi_level.get()
            optimize = self.optimize_var.get()
            
            self.log_message(f"Qualidade: {quality}%")
            self.log_message(f"DPI: {dpi}")
            self.log_message(f"Otimizar: {'Sim' if optimize else 'Não'}")
            
            method = self.compression_method.get()
            method_names = {'auto': 'Automático', 'ghostscript': 'GhostScript', 'python': 'Python (PyMuPDF)'}
            self.log_message(f"Método: {method_names[method]}")

            success = False

            if method in ("auto", "ghostscript"):
                success = self.compress_with_ghostscript(input_path, output_path, quality, dpi)
                if not success and method == "ghostscript":
                    self.log_message("❌ GhostScript falhou ou não está disponível.")
                    return

            # Se GhostScript falhar (no modo automático) ou for o escolhido, usar método Python
            if not success:
                self.log_message("Usando método Python (pode ser mais lento)...")
                success = self.compress_pdf(input_path, output_path, quality, dpi, optimize)
            
            if success:
                self.last_output_path = output_path
                self.open_pdf_button.config(state='normal')
                self.open_folder_button.config(state='normal')
                self.log_message("✅ Compressão finalizada com sucesso!")
                messagebox.showinfo("Sucesso", f"PDF comprimido salvo em:\n{output_path}")
            else:
                self.log_message("❌ Falha na compressão")
                messagebox.showerror("Erro", "Falha ao comprimir o PDF. Verifique o log para detalhes.")
                
        except Exception as e:
            self.log_message(f"❌ Erro: {str(e)}")
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")
        finally:
            self.is_compressing = False
            self.compress_button.config(state='normal')
            self.progress.stop()
            self.progress['value'] = 100

def main():
    root = tk.Tk()
    app = PDFCompressor(root)
    root.mainloop()

if __name__ == "__main__":
    main()