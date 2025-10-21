# TTS API

Универсальное API для генерации речи из текста с поддержкой различных TTS движков и клонирования голоса.

## Особенности

- **Мультиязычность**: Поддержка 17+ языков (EN, ES, FR, DE, IT, PT, PL, TR, RU, NL, CS, AR, ZH-CN, JA, HU, KO, HI)
- **Голосовое клонирование**: Возможность клонировать голос из reference аудио
- **Расширяемая архитектура**: Легко добавить новые TTS движки (Coqui xTTS, ElevenLabs, Azure, etc.)
- **REST API**: Простые HTTP эндпоинты с FastAPI
- **Docker**: Готовая контейнеризация для развертывания

## Быстрый старт

### Быстрый старт

#### Linux/Mac
1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd xTTSv2
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Скопируйте пример конфигурации:
```bash
cp .env.example .env
```

5. Запустите приложение:
```bash
python main.py
```

Для тестирования структуры без TTS зависимостей:
```bash
python test_app.py
```

#### Windows (PowerShell)
Запустите готовый скрипт:
```powershell
.\start.ps1
```

Или вручную:
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python main.py
```

API будет доступен на http://localhost:34765

### Docker запуск

```bash
# Скопируйте конфигурацию
cp .env.example .env

# Запустите с Docker Compose
docker-compose up --build
```

## Конфигурация

Создайте файл `.env` на основе `.env.example`:

```env
# TTS Engine Configuration
TTS_ENGINE=coqui_xtts
MODEL_NAME=tts_models/multilingual/multi-dataset/xtts_v2
DEVICE=cpu

# API Configuration
HOST=0.0.0.0
PORT=34765
DEBUG=false

# Output Configuration
OUTPUT_DIR=outputs
DEFAULT_LANGUAGE=en
DEFAULT_SPEAKER=Daisy Studious
DEFAULT_FORMAT=wav
```

## API Эндпоинты

### Health Check
```http
GET /health
```

Проверка состояния сервиса.

### Получить список голосов
```http
GET /voices
```

Возвращает доступные предопределенные голоса.

### Получить список языков
```http
GET /languages
```

Возвращает поддерживаемые языки.

### Генерация речи
```http
POST /tts
Content-Type: multipart/form-data

text=Hello World
language=en
speaker=Daisy Studious
output_format=wav
```

**Параметры:**
- `text` (обязательный): Текст для озвучивания
- `language` (опциональный): Код языка (по умолчанию: en)
- `speaker` (опциональный): Имя голоса для предопределенных голосов
- `speaker_wav` (опциональный): Путь к reference аудио для клонирования
- `output_format` (опциональный): wav или mp3 (по умолчанию: wav)

### Клонирование голоса
```http
POST /clone
Content-Type: multipart/form-data

file=<audio_file>
text=Hello World
language=en
output_format=wav
```

**Параметры:**
- `file` (обязательный): Reference аудио файл (wav/mp3)
- `text` (обязательный): Текст для озвучивания
- `language` (опциональный): Код языка
- `output_format` (опциональный): Формат вывода

## Примеры использования

### Python клиент

```python
import requests

# Генерация речи
response = requests.post(
    "http://localhost:34765/tts",
    data={
        "text": "Привет, мир!",
        "language": "ru",
        "speaker": "Daisy Studious"
    }
)

with open("output.wav", "wb") as f:
    f.write(response.content)
```

### cURL примеры

```bash
# Health check
curl http://localhost:34765/health

# Получить голоса
curl http://localhost:34765/voices

# Генерация речи
curl -X POST http://localhost:34765/tts \
  -F "text=Hello World" \
  -F "language=en" \
  -o output.wav

# Клонирование голоса
curl -X POST http://localhost:34765/clone \
  -F "file=@reference.wav" \
  -F "text=Hello from cloned voice" \
  -F "language=en" \
  -o cloned.wav
```

## Архитектура

```
project/
├── config.py          # Конфигурация из .env
├── main.py           # FastAPI приложение
├── requirements.txt  # Зависимости
├── Dockerfile        # Контейнер
├── docker-compose.yml
├── .env.example      # Пример конфигурации
├── .gitignore        # Исключаемые файлы
└── modules/
    ├── tts.py        # Абстракция TTS движков
    └── utils.py      # Вспомогательные функции
```

## Расширение

### Добавление нового TTS движка

1. Создайте класс в `modules/tts.py`, наследующий `TTSBase`
2. Реализуйте методы: `initialize()`, `generate_speech()`, `get_voices()`, `get_languages()`
3. Добавьте движок в словарь `TTSEngine.ENGINES`
4. Обновите конфигурацию в `.env`

### Поддерживаемые движки

- **coqui_xtts**: Coqui xTTS v2 (текущий)
- *(Планируется)*: ElevenLabs, Azure Cognitive Services, Google TTS

## Производительность

- Первый запрос может занять время из-за загрузки модели
- Рекомендуется использовать GPU для лучшей производительности (установите `DEVICE=cuda` в .env)
- Модель кэшируется после первого использования

## Безопасность

- API не требует аутентификации по умолчанию
- Для продакшена добавьте `API_KEY` в .env и реализуйте проверку
- Ограничьте размер загружаемых файлов
- Настройте cleanup старых файлов

## Лицензия

[Укажите лицензию]

## Contributing

[Инструкции для контрибьюторов]
