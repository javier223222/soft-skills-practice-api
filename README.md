# Soft Skill Practice Service

Microservicio para la gestión de prácticas de habilidades blandas (soft skills) como parte de una aplicación educativa enfocada en el desarrollo profesional de usuarios del área de tecnología.

## 🎯 Propósito

Este microservicio permite:

- **Gestionar el catálogo de soft skills** - Conflict Resolution, Critical Thinking, Empathy, etc.
- **Registrar prácticas individuales** por escenario para cada usuario
- **Generar feedback personalizado** utilizando un servicio LLM externo
- **Calcular el avance porcentual** del usuario por habilidad
- **Exponer endpoints REST** para iniciar y registrar prácticas

## 🏗️ Arquitectura

### Tecnologías Utilizadas

- **FastAPI** - Framework web moderno y de alto rendimiento
- **SQLModel** - ORM ligero que combina SQLAlchemy con Pydantic
- **PostgreSQL** - Base de datos relacional
- **Docker & Docker Compose** - Containerización y orquestación
- **Pydantic** - Validación de datos y serialización

### Estructura del Proyecto

```
softSkillPracticeService/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicación FastAPI principal
│   ├── config.py              # Configuración de la aplicación
│   ├── database.py            # Configuración de la base de datos
│   ├── models.py              # Modelos SQLModel
│   ├── schemas.py             # Esquemas Pydantic para API
│   ├── routers/               # Endpoints REST
│   │   ├── __init__.py
│   │   ├── soft_skills.py     # Catálogo de soft skills
│   │   ├── practice.py        # Sesiones de práctica
│   │   ├── progress.py        # Progreso del usuario
│   │   └── health.py          # Health checks
│   └── services/              # Lógica de negocio
│       ├── __init__.py
│       ├── practice_service.py # Gestión de prácticas
│       └── feedback_service.py # Integración con LLM
├── scripts/
│   └── populate_data.py       # Script para datos iniciales
├── tests/
│   ├── __init__.py
│   └── test_main.py           # Tests unitarios
├── docker-compose.yml         # Orquestación de servicios
├── Dockerfile                 # Imagen del microservicio
├── requirements.txt           # Dependencias Python
├── .env.example              # Variables de entorno ejemplo
└── README.md                 # Este archivo
```

## 🗄️ Modelo de Datos

### Tablas Principales

1. **`soft_skills`** - Catálogo de habilidades blandas
2. **`soft_skill_scenarios`** - Escenarios de práctica por habilidad
3. **`practice_tracking`** - Historial de sesiones de práctica
4. **`feedback_practice`** - Feedback generado por IA
5. **`soft_skill_progress`** - Progreso del usuario (tabla calculada)
6. **`tracking_logs`** - Auditoría y analytics

### Métricas de Evaluación

Cada práctica se evalúa en 5 dimensiones (escala 1-5):

- **Clarity** - Claridad del mensaje
- **Empathy** - Nivel de empatía demostrado
- **Assertiveness** - Asertividad en la comunicación
- **Listening** - Capacidad de escucha activa
- **Confidence** - Nivel de confianza transmitido

## 🚀 Instalación y Ejecución

### Prerrequisitos

- Docker y Docker Compose
- Python 3.11+ (para desarrollo local)

### Ejecución con Docker

1. **Clonar el repositorio:**
```bash
git clone <repository-url>
cd softSkillPracticeService
```

2. **Configurar variables de entorno:**
```bash
cp .env.example .env
# Editar .env con los valores apropiados
```

3. **Levantar los servicios:**
```bash
docker-compose up -d
```

4. **Poblar datos iniciales:**
```bash
docker-compose exec api python scripts/populate_data.py
```

### Ejecución Local (Desarrollo)

1. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

2. **Configurar base de datos PostgreSQL:**
```bash
# Crear base de datos local o usar Docker solo para PostgreSQL
docker run --name postgres-dev -e POSTGRES_DB=soft_skill_practice_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:15-alpine
```

3. **Ejecutar la aplicación:**
```bash
uvicorn app.main:app --reload
```

## 📚 API Endpoints

### Documentación Interactiva

Una vez ejecutando, visitar:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Endpoints Principales

#### Soft Skills

```http
GET /soft-skills/                    # Obtener todas las soft skills
GET /soft-skills/{id}                # Obtener soft skill específica
GET /soft-skills/{id}/scenarios      # Obtener escenarios de una skill
```

#### Prácticas

```http
POST /practice/start                 # Iniciar sesión de práctica
POST /practice/submit               # Enviar y completar práctica
```

#### Progreso

```http
GET /progress/{user_id}             # Progreso general del usuario
GET /progress/{user_id}/soft-skills/{skill_id}  # Progreso en skill específica
```

#### Health Check

```http
GET /health/                        # Estado del servicio
```

### Ejemplos de Uso

#### Iniciar una Práctica

```bash
curl -X POST "http://localhost:8000/practice/start" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "soft_skill_id": 1,
    "scenario_id": 1
  }'
```

#### Enviar Práctica Completada

```bash
curl -X POST "http://localhost:8000/practice/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_input": "Mi respuesta al escenario...",
    "duration_seconds": 300
  }'
```

## 🧪 Testing

Ejecutar tests unitarios:

```bash
# Con pytest (local)
pytest tests/

# Con Docker
docker-compose exec api pytest tests/
```

## 🔧 Configuración

### Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `DATABASE_URL` | URL de conexión a PostgreSQL | `postgresql://postgres:postgres@localhost:5432/soft_skill_practice_db` |
| `FEEDBACK_LLM_SERVICE_URL` | URL del servicio LLM externo | `http://localhost:8001` |
| `SECRET_KEY` | Clave secreta para JWT | `your-secret-key-here` |

### Integración con Servicio LLM

El microservicio se integra con un servicio externo para generar feedback personalizado. El servicio debe exponer un endpoint:

```http
POST /generate-feedback
Content-Type: application/json

{
  "soft_skill": "Conflict Resolution",
  "scenario": "Asking for a raise",
  "user_response": "User's input...",
  "scores": {
    "clarity_score": 4,
    "empathy_score": 3,
    "assertiveness_score": 4,
    "listening_score": 3,
    "confidence_score": 4
  },
  "language": "es",
  "feedback_style": "constructive"
}
```

## 📊 Sistema de Puntos

- **Base:** 10 puntos por práctica completada
- **Multiplicador:** Basado en el puntaje general (1-5)
- **Fórmula:** `points = 10 * (overall_score / 3.0)`

## 🔄 Cálculo de Progreso

El progreso se calcula como:
- **Porcentaje:** `(prácticas_completadas / 10) * 100`
- Se considera 10 prácticas = 100% de dominio
- Se actualiza automáticamente al completar cada práctica

## 🚦 Estado del Proyecto

### ✅ Implementado

- [x] Modelos de datos completos
- [x] API REST con FastAPI
- [x] Gestión de sesiones de práctica
- [x] Sistema de scoring y feedback
- [x] Cálculo de progreso
- [x] Integración con servicio LLM
- [x] Docker y Docker Compose
- [x] Tests unitarios básicos
- [x] Documentación API

### 🔄 En Desarrollo

- [ ] Integración con EventBus para eventos
- [ ] Métricas y analytics avanzadas
- [ ] Cacheo de datos frecuentes
- [ ] Optimizaciones de performance

### 📋 Backlog

- [ ] Sistema de notificaciones
- [ ] Gamificación avanzada
- [ ] Reportes administrativos
- [ ] Migración de datos
- [ ] Monitoring y observabilidad

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit los cambios (`git commit -am 'Add nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 📞 Soporte

Para dudas o problemas:
- Crear un [Issue](issues) en GitHub
- Contactar al equipo de desarrollo

---

**Soft Skill Practice Service** - Desarrollando el futuro de la educación en habilidades blandas 🚀
