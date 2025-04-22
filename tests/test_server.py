import sys
import os
import asyncio
import pytest

# Ensure src is in sys.path for import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from mcp_file_url_analyzer import server

@pytest.mark.asyncio
async def test_handle_list_resources_empty():
    resources = await server.handle_list_resources()
    assert isinstance(resources, list)
    assert len(resources) == 0

@pytest.mark.asyncio
async def test_add_and_read_note():
    await server.handle_call_tool('add-note', {'name': 'test', 'content': 'hello'})
    content = await server.handle_read_resource('note://internal/test')
    assert content == 'hello'

@pytest.mark.asyncio
async def test_handle_list_tools():
    tools = await server.handle_list_tools()
    assert any(t.name == 'add-note' for t in tools)

@pytest.mark.asyncio
async def test_analyze_path_file(tmp_path):
    file_path = tmp_path / 'test.txt'
    file_path.write_text('hello world')
    result = await server._analyze_path(str(file_path))
    assert result['type'] == 'text'
    assert 'hello' in result['preview']

@pytest.mark.asyncio
async def test_analyze_path_too_large(tmp_path):
    file_path = tmp_path / 'big.txt'
    file_path.write_bytes(b'a' * (server.MAX_FILE_SIZE + 1))
    result = await server._analyze_path(str(file_path))
    assert 'too large' in result['error']

@pytest.mark.asyncio
async def test_is_safe_url():
    assert not server.is_safe_url('http://localhost')
    assert not server.is_safe_url('http://127.0.0.1')
    assert server.is_safe_url('http://example.com')

# Note: For _analyze_url, you could mock httpx.AsyncClient for a real test.

@pytest.mark.asyncio
async def test_handle_read_resource_not_found():
    with pytest.raises(ValueError) as exc:
        await server.handle_read_resource('note://internal/doesnotexist')
    assert 'Note not found' in str(exc.value)

@pytest.mark.asyncio
async def test_handle_read_resource_invalid_uri():
    with pytest.raises(ValueError) as exc:
        await server.handle_read_resource('invalid://foo')
    assert 'Unsupported URI' in str(exc.value)

@pytest.mark.asyncio
async def test_handle_get_prompt_invalid():
    with pytest.raises(ValueError) as exc:
        await server.handle_get_prompt('not-a-prompt', None)
    assert 'Unknown prompt' in str(exc.value)

@pytest.mark.asyncio
async def test_handle_call_tool_invalid_tool():
    with pytest.raises(ValueError) as exc:
        await server.handle_call_tool('not-a-tool', {})
    assert 'Unknown tool' in str(exc.value)

@pytest.mark.asyncio
async def test_handle_call_tool_missing_args():
    with pytest.raises(ValueError) as exc:
        await server.handle_call_tool('add-note', None)
    assert 'Missing arguments' in str(exc.value)

@pytest.mark.asyncio
async def test_handle_call_tool_missing_name_or_content():
    with pytest.raises(ValueError) as exc:
        await server.handle_call_tool('add-note', {'name': '', 'content': ''})
    assert 'Missing name or content' in str(exc.value)

@pytest.mark.asyncio
async def test_analyze_url_invalid(monkeypatch):
    # Should reject unsafe URLs
    result = await server._analyze_url('http://localhost')
    assert 'security' in result['error'].lower()

@pytest.mark.asyncio
async def test_analyze_path_not_found():
    result = await server._analyze_path('/path/does/not/exist.txt')
    assert 'not found' in result['error'].lower()

@pytest.mark.asyncio
async def test_analyze_path_not_file_nor_dir(tmp_path):
    # Create a symlink to nowhere (broken symlink)
    broken = tmp_path / 'broken'
    broken.symlink_to('/does/not/exist')
    result = await server._analyze_path(str(broken))
    # Accept both possible error messages
    assert (
        'neither file nor directory' in result['error'].lower()
        or 'not found' in result['error'].lower()
    )
