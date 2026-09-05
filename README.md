# PDF-Compress

Compressor de PDF com interface gráfica (Tkinter), usando **GhostScript** ou **PyMuPDF** como motor de compressão, com fallback automático entre eles.

Ideal para reduzir o tamanho de PDFs pesados (banners, documentos escaneados, apresentações) sem perder o conteúdo visual.

## Funcionalidades

- 🖥️ Interface gráfica simples (Windows e Linux)
- 🔧 **3 métodos de compressão**:
  - **Automático** — tenta GhostScript primeiro; se não estiver disponível, usa Python (PyMuPDF)
  - **GhostScript** — compressão profissional com perfis de qualidade (`/prepress`, `/printer`, `/ebook`, `/screen`)
  - **Python (PyMuPDF)** — rasteriza as páginas no DPI escolhido e recomprime em JPEG (não requer GhostScript)
- 🎚️ Controle de **qualidade JPEG** (50–95%) e **DPI** (72–300)
- 🎨 Otimização opcional de cores (redução para 256 cores)
- 📊 Log detalhado com tamanho original, comprimido e percentual de redução

## Pré-requisitos

| Requisito | Windows | Linux |
|---|---|---|
| Python 3.10+ | ✅ | ✅ |
| tkinter | Incluído no instalador do Python | `sudo apt install python3-tk` |
| GhostScript | **Opcional** ([download](https://ghostscript.com/releases/gsdnld.html)) | **Opcional** (`sudo apt install ghostscript`) |

> 💡 O GhostScript é **opcional**: sem ele, o método Python (PyMuPDF) funciona normalmente.

## Instalação e execução (código-fonte)

### Windows

```powershell
git clone https://github.com/coutogilson/PDF-Compress.git
cd PDF-Compress
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

### Linux

```bash
git clone https://github.com/coutogilson/PDF-Compress.git
cd PDF-Compress
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Executáveis (sem Python instalado)

Baixe a versão mais recente na página de [Releases](https://github.com/coutogilson/PDF-Compress/releases):

- **Windows**: `PDF-Compress.exe` — basta executar (não precisa de instalação)
- **Linux**: `PDF-Compress` — dê permissão de execução: `chmod +x PDF-Compress && ./PDF-Compress`

## Como compilar você mesmo

O build usa [PyInstaller](https://pyinstaller.org/) dentro do ambiente virtual:

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Windows
python -m PyInstaller --onefile --windowed --name PDF-Compress app.py

# Linux
python3 -m PyInstaller --onefile --windowed --name PDF-Compress app.py
```

O executável será gerado na pasta `dist/`.

## Como funciona

| Método | Prós | Contras |
|---|---|---|
| **GhostScript** | Rápido, preserva texto vetorial, perfis profissionais | Requer instalação externa |
| **Python (PyMuPDF)** | Não requer dependências externas, preserva dimensões exatas das páginas | Converte páginas em imagens (texto deixa de ser selecionável); mais lento em PDFs grandes |

No modo **Automático**, o app detecta o GhostScript (no PATH ou em `C:\Program Files\gs`) e faz fallback para o PyMuPDF se necessário.

## Publicando uma nova versão

As releases são compiladas automaticamente via GitHub Actions. Basta criar e enviar uma tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

O workflow gera os binários de Windows e Linux e os anexa à release.

## Segurança

- O app apenas lê e grava os arquivos PDF escolhidos pelo usuário — nenhum dado é enviado pela rede.
- Nenhuma credencial ou segredo é necessário para rodar ou compilar.

## Licença

Distribuído sob a licença [GPL v3](LICENSE).

