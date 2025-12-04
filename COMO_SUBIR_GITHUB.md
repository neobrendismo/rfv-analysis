# Como Subir o Projeto no GitHub

## 📋 Pré-requisitos

1. **Conta no GitHub:** Crie em [github.com](https://github.com) se ainda não tiver
2. **Git instalado:** Verifique com `git --version` no terminal

---

## 🚀 Método 1: Via Terminal (Recomendado)

### Passo 1: Verificar se Git está instalado

Abra o PowerShell ou CMD na pasta do projeto e execute:

```bash
git --version
```

Se não estiver instalado, baixe em: [git-scm.com](https://git-scm.com/download/win)

### Passo 2: Inicializar o repositório Git

```bash
cd C:\Users\BrendaBarros\Desktop\RFV_2
git init
```

### Passo 3: Adicionar todos os arquivos

```bash
git add .
```

### Passo 4: Fazer o primeiro commit

```bash
git commit -m "Initial commit: Aplicação RFV completa"
```

### Passo 5: Criar repositório no GitHub

1. Acesse [github.com](https://github.com)
2. Clique no botão **"+"** no canto superior direito
3. Selecione **"New repository"**
4. Preencha:
   - **Repository name:** `rfv-analysis` (ou o nome que preferir)
   - **Description:** "Aplicação de análise RFV para segmentação de clientes"
   - **Visibility:** Escolha Public ou Private
   - **NÃO marque** "Initialize with README" (já temos um)
5. Clique em **"Create repository"**

### Passo 6: Conectar repositório local ao GitHub

O GitHub vai mostrar comandos. Use estes (substitua `SEU_USUARIO` pelo seu username):

```bash
git remote add origin https://github.com/SEU_USUARIO/rfv-analysis.git
git branch -M main
git push -u origin main
```

**Nota:** Se pedir usuário e senha:
- **Usuário:** Seu username do GitHub
- **Senha:** Use um **Personal Access Token** (não sua senha normal)
  - Como criar token: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token
  - Permissões: marque `repo`

---

## 🖱️ Método 2: Via GitHub Desktop (Mais Fácil)

### Passo 1: Instalar GitHub Desktop

Baixe em: [desktop.github.com](https://desktop.github.com)

### Passo 2: Fazer login

1. Abra GitHub Desktop
2. Faça login com sua conta GitHub

### Passo 3: Adicionar repositório local

1. Clique em **"File"** → **"Add Local Repository"**
2. Selecione a pasta: `C:\Users\BrendaBarros\Desktop\RFV_2`
3. Clique em **"Add repository"**

### Passo 4: Fazer commit

1. No GitHub Desktop, você verá todos os arquivos modificados
2. Na parte inferior, escreva uma mensagem: `"Initial commit: Aplicação RFV completa"`
3. Clique em **"Commit to main"**

### Passo 5: Publicar no GitHub

1. Clique no botão **"Publish repository"** no topo
2. Escolha:
   - **Name:** `rfv-analysis`
   - **Description:** "Aplicação de análise RFV para segmentação de clientes"
   - **Visibility:** Public ou Private
3. Clique em **"Publish repository"**

**Pronto!** Seu código está no GitHub! 🎉

---

## 📝 Método 3: Via Interface Web do GitHub (Upload Manual)

### Passo 1: Criar repositório no GitHub

1. Acesse [github.com](https://github.com)
2. Clique em **"+"** → **"New repository"**
3. Preencha os dados e clique em **"Create repository"**

### Passo 2: Upload de arquivos

1. Na página do repositório, clique em **"uploading an existing file"**
2. Arraste e solte os arquivos da pasta do projeto
3. **IMPORTANTE:** Não arraste:
   - `node_modules/` (muito grande)
   - `venv/` ou `env/` (ambiente virtual)
   - Arquivos temporários
4. Escreva mensagem de commit: `"Initial commit"`
5. Clique em **"Commit changes"**

**Nota:** Este método não é recomendado para projetos grandes.

---

## ✅ Verificar se funcionou

Após qualquer método, acesse:
```
https://github.com/SEU_USUARIO/rfv-analysis
```

Você deve ver todos os arquivos do projeto lá!

---

## 🔒 Arquivos que NÃO devem ir para o GitHub

O arquivo `.gitignore` já está configurado para ignorar:

- `node_modules/` - Dependências do Node.js
- `venv/` ou `env/` - Ambiente virtual Python
- Arquivos temporários
- Arquivos de configuração local

**Verifique o `.gitignore` antes de fazer commit!**

---

## 📤 Atualizar o Repositório (Futuras Mudanças)

Sempre que fizer alterações:

### Via Terminal:
```bash
git add .
git commit -m "Descrição das mudanças"
git push
```

### Via GitHub Desktop:
1. Faça as alterações nos arquivos
2. No GitHub Desktop, veja as mudanças
3. Escreva mensagem de commit
4. Clique em **"Commit to main"**
5. Clique em **"Push origin"**

---

## 🆘 Problemas Comuns

### Erro: "fatal: not a git repository"
**Solução:** Execute `git init` na pasta do projeto

### Erro: "authentication failed"
**Solução:** Use Personal Access Token em vez de senha

### Erro: "remote origin already exists"
**Solução:** 
```bash
git remote remove origin
git remote add origin https://github.com/SEU_USUARIO/rfv-analysis.git
```

### Arquivos muito grandes
**Solução:** Verifique se `node_modules` e `venv` estão no `.gitignore`

---

## 💡 Dica Extra: README Atrativo

Seu `README.md` já está bom! Mas você pode adicionar:
- Badges (status, versão)
- Screenshots da aplicação
- Link para demo (se hospedar)

---

**Pronto para subir! Escolha o método que preferir!** 🚀

