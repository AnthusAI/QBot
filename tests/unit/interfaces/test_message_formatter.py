"""
Unit tests for message formatting functionality.

This test suite ensures that JSON parsing and message formatting work correctly,
particularly for LLM responses that may contain JSON with single quotes and apostrophes.
"""

import pytest
from qbot.interfaces.message_formatter import (
    format_llm_response,
    _extract_text_from_json,
    MessageSymbols
)


class TestExtractTextFromJson:
    """Test the _extract_text_from_json function with various JSON formats"""
    
    def test_extract_text_from_simple_json_double_quotes(self):
        """Test extraction from valid JSON with double quotes"""
        json_str = '{"text": "Hello world"}'
        result = _extract_text_from_json(json_str)
        assert result == "Hello world"
    
    def test_extract_text_from_simple_json_single_quotes(self):
        """Test extraction from Python dict format with single quotes"""
        json_str = "{'text': 'Hello world'}"
        result = _extract_text_from_json(json_str)
        assert result == "Hello world"
    
    def test_extract_text_with_apostrophes(self):
        """Test extraction when text content contains apostrophes"""
        json_str = "{'text': 'Let\\'s find the answer'}"
        result = _extract_text_from_json(json_str)
        assert result == "Let's find the answer"
    
    def test_extract_text_with_complex_content(self):
        """Test extraction with complex text content including punctuation"""
        json_str = "{'type': 'text', 'text': '- Great question—let\\'s find the most-rented films by customers in Florida.'}"
        result = _extract_text_from_json(json_str)
        assert result == "- Great question—let's find the most-rented films by customers in Florida."
    
    def test_extract_content_field(self):
        """Test extraction from 'content' field"""
        json_str = "{'content': 'This is content'}"
        result = _extract_text_from_json(json_str)
        assert result == "This is content"
    
    def test_extract_message_field(self):
        """Test extraction from 'message' field"""
        json_str = "{'message': 'This is a message'}"
        result = _extract_text_from_json(json_str)
        assert result == "This is a message"
    
    def test_extract_text_priority_order(self):
        """Test that 'text' field takes priority over other fields"""
        json_str = "{'text': 'Text field', 'content': 'Content field', 'message': 'Message field'}"
        result = _extract_text_from_json(json_str)
        assert result == "Text field"
    
    def test_extract_from_type_text_format(self):
        """Test extraction from {'type': 'text', 'text': '...'} format"""
        json_str = "{'type': 'text', 'text': 'The actual message'}"
        result = _extract_text_from_json(json_str)
        assert result == "The actual message"
    
    def test_extract_from_malformed_json_returns_original(self):
        """Test that malformed JSON returns the original string"""
        json_str = "{'malformed': json without quotes}"
        result = _extract_text_from_json(json_str)
        assert result == json_str
    
    def test_extract_from_non_json_returns_original(self):
        """Test that non-JSON strings return unchanged"""
        text = "This is just plain text"
        result = _extract_text_from_json(text)
        assert result == text
    
    def test_extract_from_empty_string(self):
        """Test that empty strings are handled correctly"""
        result = _extract_text_from_json("")
        assert result == ""
    
    def test_extract_from_none_returns_none(self):
        """Test that None input returns None"""
        result = _extract_text_from_json(None)
        assert result is None
    
    def test_extract_with_multiple_quotes_in_content(self):
        """Test extraction when content has multiple quotes"""
        json_str = "{'text': 'This has \\'multiple\\' quotes in \\'it\\''}"
        result = _extract_text_from_json(json_str)
        assert result == "This has 'multiple' quotes in 'it'"
    
    def test_extract_with_nested_json_content(self):
        """Test extraction when content itself looks like JSON"""
        json_str = "{'text': 'The result is {\"count\": 42}'}"
        result = _extract_text_from_json(json_str)
        assert result == 'The result is {"count": 42}'


class TestFormatLlmResponse:
    """Test the format_llm_response function with various input formats"""
    
    def test_format_simple_json_response(self):
        """Test formatting of simple JSON response"""
        json_str = "{'text': 'Hello world'}"
        result = format_llm_response(json_str)
        assert result == f"{MessageSymbols.AI_RESPONSE} Hello world"
    
    def test_format_type_text_json_response(self):
        """Test formatting of {'type': 'text', 'text': '...'} format"""
        json_str = "{'type': 'text', 'text': 'The actual message'}"
        result = format_llm_response(json_str)
        assert result == f"{MessageSymbols.AI_RESPONSE} The actual message"
    
    def test_format_response_with_apostrophes(self):
        """Test formatting when response contains apostrophes"""
        json_str = "{'type': 'text', 'text': '- Great question—let\\'s find the most-rented films by customers in Florida.'}"
        result = format_llm_response(json_str)
        expected = f"{MessageSymbols.AI_RESPONSE} - Great question—let's find the most-rented films by customers in Florida."
        assert result == expected
    
    def test_format_already_formatted_response(self):
        """Test that already formatted responses are not double-formatted"""
        already_formatted = f"{MessageSymbols.AI_RESPONSE} This is already formatted"
        result = format_llm_response(already_formatted)
        assert result == already_formatted
    
    def test_format_tool_call_response(self):
        """Test that tool call responses are not double-formatted"""
        tool_call = f"{MessageSymbols.TOOL_CALL} Calling database query"
        result = format_llm_response(tool_call)
        assert result == tool_call
    
    def test_format_tool_result_response(self):
        """Test that tool result responses are not double-formatted"""
        tool_result = f"{MessageSymbols.TOOL_RESULT} Query completed"
        result = format_llm_response(tool_result)
        assert result == tool_result
    
    def test_format_plain_text_response(self):
        """Test formatting of plain text responses"""
        text = "This is just plain text"
        result = format_llm_response(text)
        assert result == f"{MessageSymbols.AI_RESPONSE} {text}"
    
    def test_format_empty_response(self):
        """Test formatting of empty responses"""
        result = format_llm_response("")
        assert result == f"{MessageSymbols.AI_RESPONSE} No response"
    
    def test_format_none_response(self):
        """Test formatting of None responses"""
        result = format_llm_response(None)
        assert result == f"{MessageSymbols.AI_RESPONSE} No response"
    
    def test_format_response_with_query_details(self):
        """Test formatting of responses with tool call details"""
        response_with_details = """{'text': 'Here is the answer'}

--- Query Details ---
Query: SELECT * FROM films
Result: 1000 films found"""
        
        result = format_llm_response(response_with_details)
        assert result == f"{MessageSymbols.AI_RESPONSE} Here is the answer"
    
    def test_format_malformed_json_as_plain_text(self):
        """Test that malformed JSON is treated as plain text"""
        malformed = "{'malformed': json without quotes}"
        result = format_llm_response(malformed)
        assert result == f"{MessageSymbols.AI_RESPONSE} {malformed}"
    
    def test_format_valid_json_with_double_quotes(self):
        """Test formatting of valid JSON with double quotes"""
        json_str = '{"text": "Hello from JSON"}'
        result = format_llm_response(json_str)
        assert result == f"{MessageSymbols.AI_RESPONSE} Hello from JSON"
    
    def test_format_json_with_content_field(self):
        """Test formatting of JSON with 'content' field"""
        json_str = "{'content': 'This is the content'}"
        result = format_llm_response(json_str)
        assert result == f"{MessageSymbols.AI_RESPONSE} This is the content"
    
    def test_format_json_with_message_field(self):
        """Test formatting of JSON with 'message' field"""
        json_str = "{'message': 'This is the message'}"
        result = format_llm_response(json_str)
        assert result == f"{MessageSymbols.AI_RESPONSE} This is the message"


class TestMessageFormatterEdgeCases:
    """Test edge cases and regression scenarios"""
    
    def test_regression_single_quotes_with_apostrophes(self):
        """Regression test for the specific issue that was fixed"""
        # This is the exact format that was causing issues
        problematic_json = "{'type': 'text', 'text': '- Great question—let\\'s find the most-rented films by customers in Florida.'}"
        
        # Should extract the text content, not return raw JSON
        extracted = _extract_text_from_json(problematic_json)
        assert extracted == "- Great question—let's find the most-rented films by customers in Florida."
        
        # Should format properly with AI response symbol
        formatted = format_llm_response(problematic_json)
        expected = f"{MessageSymbols.AI_RESPONSE} - Great question—let's find the most-rented films by customers in Florida."
        assert formatted == expected
        
        # Should NOT contain the raw JSON
        assert "{'type':" not in formatted
        assert "'text':" not in formatted
    
    def test_multiple_apostrophes_in_content(self):
        """Test content with multiple apostrophes"""
        json_str = "{'text': 'Here\\'s what we\\'ll find: it\\'s working!'}"
        result = format_llm_response(json_str)
        expected = f"{MessageSymbols.AI_RESPONSE} Here's what we'll find: it's working!"
        assert result == expected
    
    def test_quotes_and_apostrophes_mixed(self):
        """Test content with both quotes and apostrophes"""
        json_str = "{'text': 'The film \\'Casablanca\\' won\\'t be in the \"top 10\" list.'}"
        result = format_llm_response(json_str)
        expected = f"{MessageSymbols.AI_RESPONSE} The film 'Casablanca' won't be in the \"top 10\" list."
        assert result == expected
    
    def test_json_with_unicode_characters(self):
        """Test JSON with unicode characters"""
        json_str = "{'text': 'Here are the results: café, naïve, résumé'}"
        result = format_llm_response(json_str)
        expected = f"{MessageSymbols.AI_RESPONSE} Here are the results: café, naïve, résumé"
        assert result == expected
    
    def test_json_with_newlines_in_content(self):
        """Test JSON with newlines in the text content"""
        json_str = "{'text': 'Line 1\\nLine 2\\nLine 3'}"
        result = format_llm_response(json_str)
        expected = f"{MessageSymbols.AI_RESPONSE} Line 1\nLine 2\nLine 3"
        assert result == expected
    
    def test_very_long_content(self):
        """Test with very long content to ensure no truncation issues"""
        long_text = "This is a very long message. " * 100
        json_str = f"{{'text': '{long_text}'}}"
        result = format_llm_response(json_str)
        expected = f"{MessageSymbols.AI_RESPONSE} {long_text}"
        assert result == expected
    
    def test_empty_json_object(self):
        """Test empty JSON object"""
        json_str = "{}"
        result = format_llm_response(json_str)
        # Should treat as plain text since no extractable content
        assert result == f"{MessageSymbols.AI_RESPONSE} {{}}"
    
    def test_json_with_only_type_field(self):
        """Test JSON with only 'type' field, no content"""
        json_str = "{'type': 'text'}"
        result = format_llm_response(json_str)
        # Should treat as plain text since no extractable content
        assert result == f"{MessageSymbols.AI_RESPONSE} {{'type': 'text'}}"


class TestMessageSymbols:
    """Test that message symbols are correctly defined and used"""
    
    def test_message_symbols_exist(self):
        """Test that all required message symbols are defined"""
        assert hasattr(MessageSymbols, 'AI_RESPONSE')
        assert hasattr(MessageSymbols, 'TOOL_CALL')
        assert hasattr(MessageSymbols, 'TOOL_RESULT')
        assert hasattr(MessageSymbols, 'USER_MESSAGE')
    
    def test_message_symbols_are_unique(self):
        """Test that message symbols are unique"""
        symbols = [
            MessageSymbols.AI_RESPONSE,
            MessageSymbols.TOOL_CALL,
            MessageSymbols.TOOL_RESULT,
            MessageSymbols.USER_MESSAGE
        ]
        assert len(symbols) == len(set(symbols)), "Message symbols should be unique"
    
    def test_ai_response_symbol_used_correctly(self):
        """Test that AI response symbol is used in formatted responses"""
        result = format_llm_response("Test message")
        assert result.startswith(MessageSymbols.AI_RESPONSE)
