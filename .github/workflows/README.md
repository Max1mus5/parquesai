# GitHub Actions Workflows

## Sync with Upstream Repository

Este workflow permite sincronizar este repositorio con el repositorio original (upstream) de manera automática.

### Características

- **Ejecución manual**: El workflow solo se ejecuta cuando lo activas manualmente
- **Sin conflictos**: Utiliza estrategia de merge que acepta automáticamente los cambios del upstream
- **Credenciales personalizadas**: Los commits se realizan con las credenciales de "jeronimo"
- **Token personalizado**: Utiliza un Personal Access Token (PAT) para autenticación

### Configuración inicial requerida

⚠️ **IMPORTANTE**: Antes de usar el workflow, debes configurar el secret `PAT_TOKEN` en GitHub:

1. Ve a **Settings** → **Secrets and variables** → **Actions**
2. Haz clic en **New repository secret**
3. Nombre: `PAT_TOKEN`
4. Valor: Tu Personal Access Token de GitHub con permisos de `repo` y `workflow`
5. Haz clic en **Add secret**

**Cómo crear un Personal Access Token:**
1. Ve a tu perfil de GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Haz clic en **Generate new token (classic)**
3. Dale un nombre descriptivo (ej: "Sync Upstream Token")
4. Selecciona los siguientes permisos:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
5. Haz clic en **Generate token**
6. **IMPORTANTE**: Copia el token inmediatamente (solo se muestra una vez)
7. Guárdalo de forma segura

### Cómo usar el workflow

1. Ve a la pestaña **Actions** en GitHub
2. Selecciona el workflow **"Sync with Upstream Repository"** en el panel izquierdo
3. Haz clic en el botón **"Run workflow"**
4. Selecciona la rama en la que quieres ejecutar el workflow
5. Haz clic en **"Run workflow"** para iniciar la sincronización

### Qué hace el workflow

1. **Checkout**: Clona el repositorio actual con todo su historial usando el PAT_TOKEN
2. **Configura credenciales**: Establece el nombre "jeronimo" y el email "jeronimor.dev@gmail.com"
3. **Añade upstream**: Configura el repositorio original como remote "upstream"
4. **Fetch**: Descarga los cambios del repositorio upstream
5. **Merge forzado**: Realiza un merge aceptando automáticamente los cambios del upstream en caso de conflicto
6. **Push**: Sube los cambios al repositorio actual usando el PAT_TOKEN

### Repositorio upstream

- **URL**: https://github.com/GeorgeKonrad29/Parques_Distribuido_IA.git
- **Rama sincronizada**: `main`

### Notas importantes

- ⚠️ **El workflow acepta automáticamente los cambios del upstream**, por lo que cualquier cambio local en conflicto será sobrescrito
- ✅ Los commits se realizarán con las credenciales especificadas (jeronimo / jeronimor.dev@gmail.com)
- 🔒 El workflow utiliza permisos de escritura (`contents: write`) para poder hacer push de los cambios
- 🔑 Requiere configurar el secret `PAT_TOKEN` antes de ejecutar
- 📝 El mensaje del commit de sincronización será: "Sync: Force pull from upstream (GeorgeKonrad29/Parques_Distribuido_IA)"
- ⚠️ **NUNCA compartas tu Personal Access Token públicamente** - siempre usa GitHub Secrets
