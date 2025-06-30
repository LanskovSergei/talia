import os
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OUTLINE_API_KEY = os.getenv("OUTLINE_API_KEY")
OUTLINE_BASE_URL = os.getenv("OUTLINE_BASE_URL")

HEADERS = {
    "Authorization": f"Bearer {OUTLINE_API_KEY}",
    "Content-Type": "application/json"
}


def fetch_documents():
    print("📥 Получаем список документов из Outline...")
    response = httpx.post(
        f"{OUTLINE_BASE_URL}/documents.list",
        headers=HEADERS,
        json={"limit": 100}
    )
    response.raise_for_status()

    json_data = response.json()
    print("🔍 Ответ от API получен.")

    # Гибкая проверка: если data — словарь, ищем в нем "documents"
    if isinstance(json_data, dict) and "data" in json_data and "documents" in json_data["data"]:
        return json_data["data"]["documents"]

    # Иначе вернём всё как есть (возможно это уже список документов)
    if isinstance(json_data, list):
        return json_data

    raise ValueError("❌ Неподдерживаемый формат ответа от Outline API")


def fetch_content(doc_id: str):
    response = httpx.post(
        f"{OUTLINE_BASE_URL}/documents.info",
        headers=HEADERS,
        json={"id": doc_id}
    )
    response.raise_for_status()
    return response.json()["data"]["text"]


def save_documents():
    Path("docs").mkdir(parents=True, exist_ok=True)

    documents = fetch_documents()
    for doc in documents:
        title = doc.get("title", f"doc_{doc.get('id', '')}")
        title = title.strip().replace(" ", "_").replace("/", "_")
        doc_id = doc["id"]
        print(f"📄 Сохраняем: {title}")
        try:
            content = fetch_content(doc_id)
            with open(f"docs/{title[:64]}.txt", "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"⚠️ Ошибка при загрузке {title}: {e}")


if __name__ == "__main__":
    save_documents()

