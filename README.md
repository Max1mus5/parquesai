# Parques_Distribuido_IA

Un juego de parques como sistema distribuido con un Bot IA avanzado, sistema de recomendaciones inteligente, comunicación en tiempo real y sincronización distribuida.

## Inicio Rápido

### Ejecutar Backend en Local (Windows)
```powershell
cd Backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install fastapi uvicorn[standard] pydantic pydantic-settings python-socketio sqlalchemy asyncpg alembic redis python-jose[cryptography] passlib[bcrypt] python-multipart slowapi
pip install numpy pandas joblib python-dotenv email-validator httpx aiofiles aiohttp --only-binary :all:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Guía detallada**: Ver [INSTALACION_LOCAL.md](INSTALACION_LOCAL.md)

### Ejecutar Frontend (UI Interface)

**Requisitos previos**:
- Node.js 18+ o superior
- pnpm (recomendado) o npm

**Instalación y ejecución**:
```bash
cd FronEnd
pnpm install
pnpm dev
```

O con npm:
```bash
cd FronEnd
npm install
npm run dev
```

**Configuración**:
1. Crea un archivo `.env` en `FronEnd/` basado en `.env.example`
2. Configura la URL del backend:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

**Acceso**:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Documentación API: http://localhost:8000/docs

**Características del Frontend**:
- Autenticación completa (Login/Register)
- Dashboard de usuario
- Sistema de rutas con React Router
- Integración con API REST del backend
- Diseño responsive
- Componentes TypeScript tipados

### Deploy en Render
**Guía completa**: Ver [DEPLOY_RENDER.md](DEPLOY_RENDER.md)

**Variables de entorno requeridas en Render**:
- `BACKEND_CORS_ORIGINS=*`
- `DATABASE_URL=postgresql+asyncpg://...`
- `SECRET_KEY=tu-clave-secreta`
- `ENVIRONMENT=production`

## Características Principales

- **Motor de Juego Parqués Completo**: Implementación completa del juego tradicional colombiano
- **Sistema de Autenticación JWT**: Registro, login y gestión de usuarios segura
- **WebSocket en Tiempo Real**: Comunicación instantánea entre jugadores con Socket.io
- **Bot IA Avanzado**: Múltiples algoritmos (Random, Minimax, MCTS) con diferentes niveles de dificultad
- **Sistema de Recomendaciones**: Motor inteligente basado en patrones de juego y preferencias
- **Sincronización Distribuida**: Algoritmo Berkeley para coordinación temporal entre nodos
- **API REST Completa**: Endpoints documentados para todas las funcionalidades

## Arquitectura del Sistema

```
Backend/
├── app/
│   ├── api/v1/          # Endpoints REST API
│   ├── auth/            # Sistema de autenticación JWT
│   ├── core/            # Configuración y utilidades
│   ├── db/              # Modelos y base de datos
│   ├── game/            # Motor de juego Parqués
│   ├── websocket/       # Sistema WebSocket
│   ├── ai/              # Sistema de IA y bots
│   ├── recommendations/ # Motor de recomendaciones
│   ├── distributed/     # Sincronización distribuida
│   └── main.py          # Aplicación principal

FronEnd/
├── src/
│   ├── components/
│   │   ├── auth/        # Componentes de autenticación
│   │   └── common/      # Componentes compartidos
│   ├── hooks/           # Custom hooks de React
│   ├── services/        # Servicios de API
│   ├── types/           # Definiciones TypeScript
│   ├── styles/          # Estilos CSS
│   └── main.tsx         # Punto de entrada
├── public/              # Recursos estáticos
└── vite.config.ts       # Configuración de Vite
```

## Backend - Servidor API

### Requisitos Previos

- **Python 3.11.9** (RECOMENDADO - evita problemas de compatibilidad)
- PostgreSQL
- pip

> ⚠️ **IMPORTANTE**: Python 3.13 tiene incompatibilidades con Pydantic. Use Python 3.11.9 o 3.12.x

### Instalación y Configuración

1. **Clonar el repositorio**:
```bash
git clone https://github.com/GeorgeKonrad29/Parques_Distribuido_IA.git
cd Parques_Distribuido_IA/Backend
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Configurar base de datos**:
```bash
# Aplicar migraciones
alembic upgrade head
```

4. **Ejecutar el servidor**:
```bash
# Servidor de desarrollo con recarga automática
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Servidor de producción
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 🌐 Endpoints Principales

#### Autenticación
- `POST /api/v1/auth/register` - Registro de usuario
- `POST /api/v1/auth/login` - Inicio de sesión
- `GET /api/v1/auth/profile` - Perfil del usuario

#### Juego
- `POST /api/v1/game/create` - Crear nueva partida
- `POST /api/v1/game/{game_id}/join` - Unirse a partida
- `GET /api/v1/game/{game_id}/state` - Estado del juego
- `POST /api/v1/game/{game_id}/move` - Realizar movimiento
- `POST /api/v1/game/{game_id}/roll-dice` - Lanzar dado
- `POST /api/v1/game/{game_id}/pass-turn` - Pasar turno

#### WebSocket
- `GET /api/v1/websocket/rooms` - Listar salas activas
- `WebSocket /ws/{game_id}` - Conexión WebSocket para juego

#### IA y Bots
- `POST /api/v1/ai/bot/create` - Crear bot IA
- `POST /api/v1/ai/bot/{bot_id}/move` - Movimiento del bot
- `GET /api/v1/ai/difficulty-levels` - Niveles de dificultad
- `POST /api/v1/ai/bot/{bot_id}/configure` - Configurar bot

#### Recomendaciones
- `GET /api/v1/recommendations/user/{user_id}` - Recomendaciones personalizadas
- `POST /api/v1/recommendations/feedback` - Enviar feedback
- `GET /api/v1/recommendations/trending` - Tendencias populares
- `GET /api/v1/recommendations/similar-players` - Jugadores similares

#### Sincronización Distribuida
- `GET /api/v1/sync/health` - Estado del sistema de sincronización
- `GET /api/v1/sync/time` - Tiempo sincronizado del nodo
- `POST /api/v1/sync/nodes/register` - Registrar nodo
- `GET /api/v1/sync/metrics` - Métricas de sincronización

### 🔧 Módulos del Sistema

#### 1. **Motor de Juego** (`app/game/`)
- **Constantes**: Configuración del tablero y reglas
- **Validaciones**: Validación de movimientos y reglas
- **Servicios**: Lógica de negocio del juego
- **Endpoints**: API REST para interacciones de juego

#### 2. **Sistema WebSocket** (`app/websocket/`)
- **Manager**: Gestión de conexiones y salas
- **Events**: Eventos en tiempo real (movimientos, chat, notificaciones)
- **Authentication**: Autenticación JWT para WebSocket
- **Rooms**: Sistema de salas por partida

#### 3. **Sistema de IA** (`app/ai/`)
- **RandomBot**: Bot con movimientos aleatorios
- **MinimaxBot**: Bot con algoritmo Minimax y poda alfa-beta
- **MCTSBot**: Bot con Monte Carlo Tree Search
- **Difficulty Levels**: Configuración de dificultad adaptativa
- **Evaluation**: Funciones de evaluación de posiciones

#### 4. **Sistema de Recomendaciones** (`app/recommendations/`)
- **Pattern Analyzer**: Análisis de patrones de juego
- **Recommendation Engine**: Motor de recomendaciones personalizado
- **Service**: Servicios de recomendaciones y feedback
- **ML Models**: Modelos de aprendizaje automático

#### 5. **Sincronización Distribuida** (`app/distributed/`)

**⚠️ NOTA IMPORTANTE: Sincronización en Producción**

El proyecto incluye dos estrategias de sincronización:

##### **A) Algoritmo de Berkeley (Implementado pero no usado en producción)**
- **Ubicación**: `app/distributed/berkeley_algorithm.py`
- **Propósito**: Sincronización de tiempo entre múltiples nodos distribuidos
- **Estado**: ✅ Implementado completamente
- **Uso**: ❌ No activo en producción (Render + Vercel)

**¿Por qué no se usa Berkeley en producción?**
```
Limitaciones de PaaS/Serverless:
✗ Requiere múltiples nodos activos simultáneamente
✗ Comunicación peer-to-peer entre contenedores no disponible
✗ Instancias efímeras que se reinician/duermen
✗ No hay control sobre reloj del sistema en contenedores
✗ Render Free tier: auto-sleep después de 15min inactividad
```

##### **B) Sincronización Centralizada (USADO EN PRODUCCIÓN)** ⭐
- **Algoritmo**: Centralized Timestamp-based Synchronization (similar a Cristian's Algorithm)
- **Implementación**: `app/services/game_service.py`
- **Autoridad Temporal**: PostgreSQL en Neon
- **Características**:
  - ✅ PostgreSQL como **Single Source of Truth**
  - ✅ Timestamps UTC del servidor como orden total
  - ✅ Crash Recovery automático desde BD
  - ✅ Eventual Consistency vía polling
  - ✅ Primary-Backup con BD como primario

**Comparación con algoritmos clásicos:**
```python
# Cristian's Algorithm (1989) - MÁS SIMILAR ✓
Cliente ← Servidor (timestamp)
Cliente ajusta su reloj

# Nuestro caso:
Backend ← PostgreSQL (timestamps)
Backend usa timestamps de BD directamente

# Berkeley Algorithm - Implementado pero no usado
Maestro solicita tiempo a todos los esclavos
Maestro calcula promedio y envía ajustes
Todos ajustan sus relojes
```

**Componentes del sistema distribuido:**
- **Node Management**: Gestión de nodos maestro/esclavo (Berkeley)
- **Time Coordination**: Coordinación temporal (timestamps centralizados)
- **Sync Service**: Servicio de sincronización (híbrido)
- **Database Authority**: PostgreSQL como autoridad temporal (producción)

### 📡 Comunicación en Tiempo Real

El sistema utiliza **Socket.io** para comunicación bidireccional:

```javascript
// Conexión WebSocket
const socket = io(`ws://localhost:8000/ws/${gameId}`, {
    auth: {
        token: "jwt_token_here"
    }
});

// Eventos principales
socket.on('game_updated', (data) => {
    // Actualizar estado del juego
});

socket.on('player_moved', (data) => {
    // Procesar movimiento de jugador
});

socket.on('dice_rolled', (data) => {
    // Mostrar resultado del dado
});
```

### 🤖 Integración con IA

```javascript
// Crear bot IA
const bot = await fetch('/api/v1/ai/bot/create', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        bot_type: 'minimax',
        difficulty: 'medium',
        game_id: gameId
    })
});

// Solicitar movimiento del bot
const move = await fetch(`/api/v1/ai/bot/${botId}/move`, {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        game_state: currentGameState
    })
});
```

### 📊 Sistema de Recomendaciones

```javascript
// Obtener recomendaciones personalizadas
const recommendations = await fetch(`/api/v1/recommendations/user/${userId}`, {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});

// Enviar feedback
await fetch('/api/v1/recommendations/feedback', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        recommendation_id: recId,
        rating: 5,
        feedback_type: 'positive'
    })
});
```

### 🔄 Sincronización Distribuida

```javascript
// Verificar estado de sincronización
const syncStatus = await fetch('/api/v1/sync/health');

// Obtener tiempo sincronizado
const syncTime = await fetch('/api/v1/sync/time/synchronized');

// Sincronizar evento de juego
await fetch('/api/v1/sync/events/sync', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        event_type: 'move',
        game_id: gameId,
        timestamp: Date.now(),
        data: moveData
    })
});
```

### 🔍 Health Check

El servidor proporciona un endpoint de health check:

```bash
curl http://localhost:8000/health
```

Respuesta:
```json
{
    "status": "healthy",
    "timestamp": 1763247964.58042
}
```

### 📝 Logs y Monitoreo

- **Logs del servidor**: `Backend/server.log`
- **Métricas de IA**: Disponibles en `/api/v1/ai/metrics`
- **Métricas de sincronización**: Disponibles en `/api/v1/sync/metrics`
- **Estado de WebSocket**: Disponible en `/api/v1/websocket/status`

### Desarrollo

Para desarrollo del frontend, el servidor debe estar ejecutándose en `http://localhost:8000` con CORS habilitado para permitir conexiones desde el cliente.

**Backend incluye**:
- **Recarga automática** en modo desarrollo
- **Documentación automática** en `/docs` (Swagger UI)
- **Esquemas OpenAPI** en `/openapi.json`
- **WebSocket testing** en `/ws-test`

**Frontend incluye**:
- **Hot Module Replacement (HMR)** con Vite
- **TypeScript** para tipado estático
- **React Router** para navegación
- **ESLint** para linting
- **Componentes reutilizables**

### Consideraciones Importantes

**Configuración de CORS**:
- En desarrollo, el backend debe tener `BACKEND_CORS_ORIGINS=*` en `.env`
- En producción, especificar los dominios permitidos

**Puertos por defecto**:
- Backend: `8000`
- Frontend: `5173`

**Variables de entorno**:
- Backend: `Backend/.env`
- Frontend: `FronEnd/.env`

**Orden de ejecución**:
1. Iniciar Backend primero
2. Luego iniciar Frontend
3. El Frontend se conectará automáticamente al Backend

## Frontend - Interfaz de Usuario

### Requisitos Previos

- **Node.js 18+** o superior
- **npm** o **pnpm** (recomendado)

### Instalación y Configuración

1. **Navegar al directorio del frontend**:
```bash
cd FronEnd
```

2. **Instalar dependencias**:
```bash
# Con npm
npm install

# O con pnpm (recomendado)
pnpm install
```

3. **Configurar variables de entorno**:
```bash
# Crear archivo .env basado en .env.example
cp .env.example .env
```

Contenido del `.env`:
```env
# URL del backend API
VITE_API_URL=http://localhost:8000

# Configuración de desarrollo
VITE_NODE_ENV=development
```

4. **Ejecutar el servidor de desarrollo**:
```bash
# Con npm
npm run dev

# O con pnpm
pnpm dev
```

El frontend estará disponible en: http://localhost:5173

### Stack Tecnológico

- **React 19** - Biblioteca UI
- **TypeScript** - Tipado estático
- **Vite** - Build tool y dev server
- **React Router** - Navegación
- **Lucide React** - Iconos

### Estructura del Proyecto

```
FronEnd/
├── src/
│   ├── components/
│   │   ├── auth/
│   │   │   ├── AuthPage.tsx        # Página principal de autenticación
│   │   │   ├── LoginForm.tsx       # Formulario de inicio de sesión
│   │   │   └── RegisterForm.tsx    # Formulario de registro
│   │   └── common/
│   │       ├── Dashboard.tsx       # Panel principal del usuario
│   │       └── Loading.tsx         # Componente de carga
│   ├── hooks/
│   │   └── useAuth.tsx             # Hook personalizado para autenticación
│   ├── services/
│   │   └── authService.ts          # Servicios de API para autenticación
│   ├── types/
│   │   ├── api.ts                  # Tipos para respuestas de API
│   │   └── auth.ts                 # Tipos para autenticación
│   ├── styles/
│   │   └── globals.css             # Estilos globales
│   ├── App.tsx                     # Componente raíz
│   ├── main.tsx                    # Punto de entrada
│   └── index.css                   # Estilos base
├── public/                         # Recursos estáticos
├── .env                            # Variables de entorno (local)
├── .env.example                    # Plantilla de variables de entorno
├── vite.config.ts                  # Configuración de Vite
├── tsconfig.json                   # Configuración de TypeScript
└── package.json                    # Dependencias y scripts
```

### Scripts Disponibles

```bash
# Desarrollo - Inicia servidor con HMR
npm run dev

# Build - Compila para producción
npm run build

# Preview - Vista previa del build de producción
npm run preview

# Lint - Ejecuta ESLint
npm run lint
```

### Características Implementadas

#### Autenticación
- **Registro de usuarios**: Formulario completo con validación
- **Inicio de sesión**: Login con email y contraseña
- **Gestión de tokens**: Almacenamiento seguro de JWT
- **Persistencia de sesión**: Mantiene sesión activa
- **Cierre de sesión**: Limpieza de datos de usuario

#### Interfaz
- **Diseño responsive**: Adaptable a móviles y desktop
- **Componentes reutilizables**: Arquitectura modular
- **Tipado TypeScript**: Seguridad de tipos en toda la aplicación
- **Navegación fluida**: React Router para rutas
- **Estados de carga**: Feedback visual durante peticiones

### Integración con Backend

El frontend se comunica con el backend a través de la API REST:

```typescript
// Ejemplo de servicio de autenticación
import { API_URL } from './config';

export const authService = {
  async login(email: string, password: string) {
    const response = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });
    return response.json();
  },
  
  async register(userData: RegisterData) {
    const response = await fetch(`${API_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });
    return response.json();
  }
};
```

### Variables de Entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `VITE_API_URL` | URL del backend API | `http://localhost:8000` |
| `VITE_NODE_ENV` | Entorno de ejecución | `development` |

### Desarrollo

**Hot Module Replacement (HMR)**:
- Cambios en componentes se reflejan instantáneamente
- No es necesario recargar la página
- Estado de la aplicación se mantiene

**TypeScript**:
- Autocompletado inteligente
- Detección de errores en tiempo de desarrollo
- Mejor experiencia de desarrollo

**ESLint**:
- Reglas configuradas para React y TypeScript
- Detecta problemas de código automáticamente
- Mantiene consistencia en el código

### Build para Producción

```bash
# Compilar para producción
npm run build

# El resultado estará en: dist/
# Archivos optimizados y minificados
# Assets con hash para cache busting
```

### Troubleshooting Frontend

**Error: Cannot connect to backend**
- Verifica que el backend esté corriendo en `http://localhost:8000`
- Revisa la variable `VITE_API_URL` en `.env`
- Verifica CORS en el backend

**Error: Module not found**
```bash
# Reinstalar dependencias
rm -rf node_modules package-lock.json
npm install
```

**Error: Port already in use**
```bash
# Vite usa puerto 5173 por defecto
# Si está ocupado, Vite asignará uno automático
# O especifica uno diferente:
npm run dev -- --port 3000
```

### 🔐 Autenticación

Todos los endpoints protegidos requieren un token JWT en el header:
```
Authorization: Bearer <jwt_token>
```

El token se obtiene mediante login y debe incluirse en todas las peticiones autenticadas y conexiones WebSocket.

## 🔧 Troubleshooting

### Error: `ForwardRef._evaluate() missing 1 required keyword-only argument: 'recursive_guard'`

**Problema**: Python 3.13 incompatible con Pydantic 2.6.1

**Solución**:
1. **Opción 1 (Recomendada)**: Cambiar a Python 3.11.9
   ```bash
   # Con pyenv
   pyenv install 3.11.9
   pyenv local 3.11.9
   
   # Recrear entorno virtual
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # o
   venv\Scripts\activate     # Windows
   
   pip install -r Backend/requirements.txt
   ```

2. **Opción 2**: Usar Python 3.12.x
   ```bash
   # Similar al anterior pero con 3.12.x
   pyenv install 3.12.7
   pyenv local 3.12.7
   ```

### Error: `ModuleNotFoundError: No module named 'socketio'`

**Problema**: Falta instalar `python-socketio`

**Solución**:
```bash
cd Backend
pip install -r requirements.txt
```

### Para Render

**Build Command**: `cd Backend && pip install -r requirements.txt`
**Start Command**: `./start.sh`

**Variables de entorno obligatorias**:
```
PYTHON_VERSION=3.11.9
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_BjwQ2ZtsCnR5@ep-young-salad-a8nr0kos-pooler.eastus2.azure.neon.tech/neondb?ssl=require
SECRET_KEY=tu-clave-secreta-super-segura-para-produccion-2024
ENVIRONMENT=production
DEBUG=false
BACKEND_CORS_ORIGINS=*
```

> ⚠️ **IMPORTANTE para CORS**: 
> - Para permitir todos los orígenes: `BACKEND_CORS_ORIGINS=*`
> - Para orígenes específicos: `BACKEND_CORS_ORIGINS=https://miapp.com,https://www.miapp.com`
> - NO usar formato JSON en Render: `["https://miapp.com"]` ❌
