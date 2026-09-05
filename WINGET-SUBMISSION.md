# Publicação no winget

Esta pasta contém os manifestos para publicar o PDF-Compress no repositório
oficial [`microsoft/winget-pkgs`](https://github.com/microsoft/winget-pkgs).

## Pré-requisitos

1. Repositório GitHub **público** (Settings → Danger Zone → Change visibility)
2. Release **publicada** (não draft) com o asset `PDF-Compress-windows-x64.exe`
3. Ferramenta `wingetcreate`: `winget install wingetcreate`

## Primeira submissão (manual, uma única vez)

1. Confira se o `InstallerSha256` em `coutogilson.PDF-Compress.installer.yaml`
   corresponde ao hash do `.exe` da release atual (para a v1.0.1 já está
   preenchido). Para conferir/recalcular:

   ```powershell
   Get-FileHash .\PDF-Compress-windows-x64.exe -Algorithm SHA256
   ```

2. Valide localmente:

   ```powershell
   winget validate --manifest .\winget\
   ```

3. Submeta (abre um PR no winget-pkgs automaticamente):

   ```powershell
   wingetcreate submit .\winget\
   ```

   > Na primeira submissão, será solicitado que você faça fork do
   > `microsoft/winget-pkgs` na sua conta GitHub.

5. Aguarde a validação da Microsoft (bot + revisão). Após o merge, o pacote
   fica disponível em ~24h via `winget install coutogilson.PDF-Compress`.

## Atualizações automáticas (releases futuras)

O workflow `release.yml` já inclui o job `publish-winget`
([winget-releaser](https://github.com/vedantmgoyal9/winget-releaser)), que
atualiza o pacote automaticamente a cada nova tag `v*`.

Para ativá-lo:

1. Crie um **Personal Access Token (clássico)** em
   https://github.com/settings/tokens com o escopo `public_repo`
2. No repositório: **Settings → Secrets and variables → Actions**
   - Crie o **secret** `WINGET_TOKEN` com o token
   - Crie a **variable** `WINGET_ENABLED` com valor `true`
3. A partir daí, todo `git push` de tag `v*` publica a release **e** abre
   o PR de atualização no winget-pkgs.

> ⚠️ Sem o secret configurado, o job é pulado (`if: vars.WINGET_ENABLED == 'true'`)
> e o build da release funciona normalmente.
