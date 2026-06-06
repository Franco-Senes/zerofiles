# test_zerofiles.py
# Unit tests for zerofiles library.

import unittest
from zerofiles import loads, dumps, ZeroFile, tokenize, Parser, format_zr, lint_zr

class TestZeroFiles(unittest.TestCase):
    def test_basic_parse(self):
        text = '{"name": "test", "value": 123}'
        zf = loads(text)
        self.assertEqual(zf.data, {"name": "test", "value": 123})

    def test_comments(self):
        text = """
        // This is a line comment
        {
            # Another line comment
            "key": "val", /* inline comment */
            "arr": [
                1, // value 1
                2  /* value 2 */
            ]
        }
        """
        zf = loads(text)
        self.assertEqual(zf.data, {"key": "val", "arr": [1, 2]})

    def test_relaxed_syntax(self):
        # trailing commas, single quotes, unquoted keys
        text = """
        {
            unquoted_key: 'single quoted val',
            'single_quoted_key': "double",
            array: [1, 2, 3,],
        }
        """
        zf = loads(text)
        self.assertEqual(zf.data, {
            "unquoted_key": "single quoted val",
            "single_quoted_key": "double",
            "array": [1, 2, 3]
        })

    def test_booleans_nulls(self):
        text = """
        {
            t1: true,
            t2: True,
            f1: false,
            f2: False,
            n1: null,
            n2: None,
        }
        """
        zf = loads(text)
        self.assertEqual(zf.data["t1"], True)
        self.assertEqual(zf.data["t2"], True)
        self.assertEqual(zf.data["f1"], False)
        self.assertEqual(zf.data["f2"], False)
        self.assertIsNone(zf.data["n1"])
        self.assertIsNone(zf.data["n2"])

    def test_metadata_extraction(self):
        text = """
        # @title: Sample Doc
        # @version: 2.0
        // @author: Franc
        
        {
            "foo": "bar"
        }
        """
        zf = loads(text)
        self.assertEqual(zf.metadata, {
            "title": "Sample Doc",
            "version": "2.0",
            "author": "Franc"
        })
        self.assertEqual(zf.data, {"foo": "bar"})

    def test_serialization(self):
        data = {
            "name": "Project",
            "values": [True, False, None],
            "complex key": "needs quotes",
            "clean_key": 42
        }
        meta = {"author": "Franc"}

        serialized = dumps(data, metadata=meta, indent=4)

        # Verify metadata headers are present
        self.assertIn("# @author: Franc", serialized)
        self.assertIn("# @date: ", serialized) # Auto-injected
        self.assertIn("# @version: 1.0", serialized) # Auto-injected

        # Verify unquoted key formatting in body
        self.assertIn("clean_key: 42", serialized)
        self.assertIn('"complex key": "needs quotes"', serialized)
        self.assertIn("name: \"Project\"", serialized)

        # Verify it parses back perfectly
        parsed = loads(serialized)
        self.assertEqual(parsed.data["name"], "Project")
        self.assertEqual(parsed.data["clean_key"], 42)
        self.assertEqual(parsed.data["complex key"], "needs quotes")
        self.assertEqual(parsed.data["values"], [True, False, None])
        self.assertEqual(parsed.metadata["author"], "Franc")

    def test_syntax_errors(self):
        # Unterminated string
        with self.assertRaises(SyntaxError):
            loads('{"key": "unterminated}')
        # Invalid char
        with self.assertRaises(SyntaxError):
            loads('{"key": @}')
        # Missing comma/brace
        with self.assertRaises(SyntaxError):
            loads('{"key": "val" "key2": "val"}')

    def test_formatter_preserves_comments(self):
        text = """# @title: Hello
// This is a comment
{
    name: "ZeroFiles Project", // inline comment
    /* block comment
       multiline */
    features: [
        'item1', // item comment
    ],
}"""
        formatted = format_zr(text)
        self.assertIn("// This is a comment", formatted)
        self.assertIn("name: \"ZeroFiles Project\", // inline comment", formatted)
        self.assertIn("/* block comment", formatted)
        self.assertIn("item1", formatted)
        self.assertIn("# @title: Hello", formatted)

    def test_linter(self):
        text = """
        {
            "name": 'single',
            'valid-id': 123
        }
        """
        issues = lint_zr(text)
        self.assertTrue(len(issues) >= 3)
        self.assertEqual(issues[0]['type'], 'warning')

if __name__ == '__main__':
    unittest.main()
