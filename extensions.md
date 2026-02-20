# VS Code Extensions and Setup

Practical extension recommendations and setup steps for:

- Python
- React (JavaScript/TypeScript)
- Elasticsearch

---

## 1) Install extensions

When you open this project in VS code, you will be prompted to install extensions. Accept the prompt and all extensions will be installed. 

### Manual installation

Open Extensions in VS Code (`Ctrl+Shift+X`) and search for these IDs:

### Python
- `ms-python.python` (Python)
- `ms-python.vscode-pylance` (Pylance)
  - Intellisense
- `ms-python.autopep8` (autopep8)
  - Automatic formatting to pep8

### React / JavaScript / TypeScript

- `dbaeumer.vscode-eslint` (ESLint)
  - Linting support
- `esbenp.prettier-vscode` (Prettier - Code formatter)
  - Automatic formatting for JS and TS

### Elasticsearch

- `ria.elastic` (Elasticsearch for VSCode)
  - Query Elasticsearch directly
  - Syntax highlighting
- `humao.rest-client` (REST Client)
  - Send HTTP queries

Example REST Client request:

```http
GET https://example.com/comments/1 HTTP/1.1
```

---

## 2) Workspace settings

Formatting and linting are configured in `.vscode/settings.json` and apply automatically:

- **Python**: autopep8 format on save
- **JavaScript/TypeScript**: Prettier format on save
- **ESLint**: auto-fix on save (requires setup)

---

## 3) ESLint + Prettier setup

ESLint and Prettier work together:
- **Prettier** handles formatting (spacing, indentation)
- **ESLint** catches code quality issues (bugs, unused variables, React hooks violations)

### Setup steps

1. **Install ESLint**:
   ```bash
   npm install --save-dev eslint
   ```

2. **Create ESLint config**:
   ```bash
   npx eslint --init
   ```

3. **Install Prettier integration** (prevents formatting conflicts):
   ```bash
   npm install --save-dev eslint-config-prettier
   ```

4. **Update `.eslintrc.json`** to include Prettier config:
   ```json
   {
     "extends": [
       "eslint:recommended",
       "prettier"
     ]
   }
   ```

Once configured, workspace settings will auto-format with Prettier and auto-fix ESLint issues on save.



