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

| Arquivo | Plataforma | Uso |
|---|---|---|
| `PDF-Compress-windows-x64.exe` | Windows 10/11 (64 bits) | Executar direto, sem instalação |
| `PDF-Compress-linux-x64.AppImage` | Linux (64 bits) — **recomendado** | `chmod +x PDF-Compress-linux-x64.AppImage && ./PDF-Compress-linux-x64.AppImage` |
| `PDF-Compress-linux-x64` | Linux (64 bits) — binário simples | `chmod +x PDF-Compress-linux-x64 && ./PDF-Compress-linux-x64` |

> 💡 O **AppImage** é portátil e integra-se ao menu de aplicativos (com ícone) ao usar ferramentas como o [AppImageLauncher](https://github.com/TheAssassin/AppImageLauncher).

### ⚠️ Aviso do Windows SmartScreen

Ao baixar o `.exe` direto do navegador, o Windows pode exibir **"O Windows protegeu o computador"**. Isso acontece porque o executável é novo e **não possui assinatura de código digital** (certificado pago) — **não é vírus**.

Para executar mesmo assim:

1. Clique em **"Mais informações"**
2. Clique em **"Executar assim mesmo"**

**Como ter certeza de que o arquivo é legítimo:** compare o hash SHA-256 do arquivo baixado com o publicado na página da Release:

```powershell
Get-FileHash .\PDF-Compress-windows-x64.exe -Algorithm SHA256
```

**Alternativa sem aviso nenhum (recomendada):** instale via **winget** (gerenciador oficial da Microsoft), que valida o pacote:

```powershell
winget install coutogilson.PDF-Compress
```

> 💡 Com o tempo e o volume de downloads, a reputação do arquivo sobe no SmartScreen e o aviso deixa de aparecer naturalmente.

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

