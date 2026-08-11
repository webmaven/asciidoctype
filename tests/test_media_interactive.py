from asciidoctrine.lark_parser import parse_to_ast
from asciidoctrine.resolver import ASGResolver, WorkspaceCatalog

from asciidoctype import AsciiDoctypeRenderer


def test_render_audio_and_video_html5():
    text = """
audio::sound.mp3[]

video::clip.mp4[]
"""
    catalog = WorkspaceCatalog()
    ast = parse_to_ast(text)
    asg = ASGResolver(catalog, "test.adoc").resolve(ast)

    renderer = AsciiDoctypeRenderer(target_format="html5")
    output = renderer.render(asg)

    assert '<div class="audioblock">' in output
    assert '<audio src="sound.mp3" controls="controls">' in output
    assert '<div class="videoblock">' in output
    assert '<video src="clip.mp4" controls="controls">' in output


def test_render_collapsible_xhtml():
    renderer = AsciiDoctypeRenderer(target_format="xhtml")
    node = {
        "name": "collapsible",
        "type": "block",
        "title": [{"name": "text", "type": "string", "value": "Details Title"}],
        "blocks": [
            {
                "name": "paragraph",
                "type": "block",
                "inlines": [
                    {"name": "text", "type": "string", "value": "Collapsible content text."}
                ],
            }
        ],
    }
    output = renderer.render(node)

    assert '<details class="collapsible">' in output
    assert "<summary" in output
    assert "Details Title" in output
    assert "<p>Collapsible content text.</p>" in output
