# GitHub Actions Workflows

## Sync with Upstream Repository

Este workflow permite sincronizar este repositorio con el repositorio original (upstream) de manera automática.

### Características

- **Ejecución manual**: El workflow solo se ejecuta cuando lo activas manualmente
- **Sin conflictos**: Utiliza estrategia de merge que acepta automáticamente los cambios del upstream
- **Credenciales personalizadas**: Los commits se realizan con las credenciales de "jeronimo"

### Cómo usar el workflow

1. Ve a la pestaña **Actions** en GitHub
2. Selecciona el workflow **"Sync with Upstream Repository"** en el panel izquierdo
3. Haz clic en el botón **"Run workflow"**
4. Selecciona la rama en la que quieres ejecutar el workflow
5. Haz clic en **"Run workflow"** para iniciar la sincronización

### Qué hace el workflow

1. **Checkout**: Clona el repositorio actual con todo su historial
2. **Configura credenciales**: Establece el nombre "jeronimo" y el email "jeronimor.dev@gmail.com"
3. **Añade upstream**: Configura el repositorio original como remote "upstream"
4. **Fetch**: Descarga los cambios del repositorio upstream
5. **Merge forzado**: Realiza un merge aceptando automáticamente los cambios del upstream en caso de conflicto
6. **Push**: Sube los cambios al repositorio actual

### Repositorio upstream

- **URL**: https://github.com/GeorgeKonrad29/Parques_Distribuido_IA.git
- **Rama sincronizada**: `main`

### Notas importantes

- ⚠️ **El workflow acepta automáticamente los cambios del upstream**, por lo que cualquier cambio local en conflicto será sobrescrito
- ✅ Los commits se realizarán con las credenciales especificadas (jeronimo / jeronimor.dev@gmail.com)
- 🔒 El workflow utiliza permisos de escritura (`contents: write`) para poder hacer push de los cambios
- 📝 El mensaje del commit de sincronización será: "Sync: Force pull from upstream (GeorgeKonrad29/Parques_Distribuido_IA)"
