import pytest
from pathlib import Path
from src.infrastructure.chat_store import CopilotChatStore


@pytest.fixture
def temp_chat_store(tmp_path: Path):
    store_file = tmp_path / "test_chats.json"
    return CopilotChatStore(file_path=store_file)


def test_chat_store_initialization(temp_chat_store):
    assert temp_chat_store.list_threads() == []


def test_chat_store_save_and_get(temp_chat_store):
    thread_id = "test-thread-1"
    messages = [
        {"role": "user", "content": "Investigação do SKU-00185"},
        {"role": "assistant", "content": "Aqui está a análise..."}
    ]
    saved = temp_chat_store.save_thread(thread_id, messages)
    assert saved["id"] == thread_id
    assert saved["title"] == "Investigação do SKU-00185"
    assert len(saved["messages"]) == 2

    retrieved = temp_chat_store.get_thread(thread_id)
    assert retrieved is not None
    assert retrieved["title"] == "Investigação do SKU-00185"
    assert retrieved["messages"] == messages


def test_chat_store_auto_title_truncation(temp_chat_store):
    thread_id = "test-thread-2"
    long_msg = "Por favor faça uma investigação super aprofundada de todos os produtos com descompasso de estoque e marketing"
    messages = [{"role": "user", "content": long_msg}]
    saved = temp_chat_store.save_thread(thread_id, messages)
    assert len(saved["title"]) <= 38
    assert saved["title"].endswith("...")


def test_chat_store_list_ordering(temp_chat_store):
    temp_chat_store.save_thread("t1", [{"role": "user", "content": "Primeira"}])
    temp_chat_store.save_thread("t2", [{"role": "user", "content": "Segunda"}])
    
    threads = temp_chat_store.list_threads()
    assert len(threads) == 2
    # The most recently updated should be first
    assert threads[0]["id"] == "t2"
    assert threads[1]["id"] == "t1"


def test_chat_store_delete_and_clear(temp_chat_store):
    temp_chat_store.save_thread("t1", [{"role": "user", "content": "Chat 1"}])
    temp_chat_store.save_thread("t2", [{"role": "user", "content": "Chat 2"}])

    assert temp_chat_store.delete_thread("t1") is True
    assert temp_chat_store.get_thread("t1") is None
    assert len(temp_chat_store.list_threads()) == 1

    temp_chat_store.clear_all()
    assert len(temp_chat_store.list_threads()) == 0
