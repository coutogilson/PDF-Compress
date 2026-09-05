import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import scrolledtext
import threading
from PIL import Image
import io

APP_VERSION = "1.0.0"

class PDFCompressor:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Compressor de PDF v{APP_VERSION} - Alta Qualidade")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Variáveis
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.compression_level = tk.IntVar(value=85)
        self.dpi_level = tk.IntVar(value=150)
        self.is_compressing = False
        
        self.setup_ui()
        
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
        ttk.Entry(main_frame, textvariable=self.input_file, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Selecionar", command=self.select_input_file).grid(row=1, column=2, pady=5)
        
        # Seleção do arquivo de saída
        ttk.Label(main_frame, text="Salvar como:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_file, width=50).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Destino", command=self.select_output_file).grid(row=2, column=2, pady=5)
        
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
        
        # DPI para imagens
        ttk.Label(options_frame, text="DPI (resolução):").grid(row=1, column=0, sticky=tk.W, pady=5)
        dpi_scale = ttk.Scale(options_frame, from_=72, to=300, variable=self.dpi_level,
                             orient=tk.HORIZONTAL, length=200)
        dpi_scale.grid(row=1, column=1, padx=10, pady=5, sticky=(tk.W, tk.E))
        ttk.Label(options_frame, textvariable=self.dpi_level).grid(row=1, column=2, padx=5, pady=5)
        
        # Método de compressão
        ttk.Label(options_frame, text="Método:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.compression_method = tk.StringVar(value="auto")
        method_frame = ttk.Frame(options_frame)
        method_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=10, pady=5)
        ttk.Radiobutton(method_frame, text="Automático", value="auto",
                       variable=self.compression_method).grid(row=0, column=0, padx=(0, 10))
        ttk.Radiobutton(method_frame, text="GhostScript", value="ghostscript",
                       variable=self.compression_method).grid(row=0, column=1, padx=(0, 10))
        ttk.Radiobutton(method_frame, text="Python (PyMuPDF)", value="python",
                       variable=self.compression_method).grid(row=0, column=2)

        # Checkbox para otimização adicional
        self.optimize_images = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Otimizar imagens (reduzir cores)", 
                       variable=self.optimize_images).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Botões de ação
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        self.compress_button = ttk.Button(action_frame, text="Comprimir PDF", 
                                         command=self.start_compression, width=20)
        self.compress_button.grid(row=0, column=0, padx=5)
        
        self.clear_button = ttk.Button(action_frame, text="Limpar", 
                                      command=self.clear_fields, width=15)
        self.clear_button.grid(row=0, column=1, padx=5)
        
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
            optimize = self.optimize_images.get()
            
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