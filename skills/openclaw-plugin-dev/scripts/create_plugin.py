#!/usr/bin/env python3
"""
OpenClaw Channel Plugin Generator

Generates a minimal, testable plugin template for a new channel.
Supports both Webhook and WebSocket modes.

Usage:
    python create_plugin.py --channel-id <id> --channel-label <label> [options]

Examples:
    # Webhook mode (default)
    python create_plugin.py --channel-id dingtalk --channel-label "钉钉"

    # WebSocket mode
    python create_plugin.py --channel-id feishu --channel-label "飞书" --mode websocket
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def to_class_name(channel_id: str) -> str:
    """Convert channel_id to PascalCase class name."""
    parts = re.split(r"[-_]", channel_id)
    return "".join(part.capitalize() for part in parts)


def load_template(template_path: str) -> str:
    """Load template file."""
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def replace_placeholders(template: str, context: dict) -> str:
    """Replace placeholders in template."""
    result = template
    for key, value in context.items():
        placeholder = "{{" + key + "}}"
        result = result.replace(placeholder, str(value))
    return result


def create_plugin(args):
    """Create plugin from template."""
    channel_id = args.channel_id.lower()
    channel_label = args.channel_label
    channel_class = to_class_name(channel_id)
    npm_scope = args.scope or f"@{channel_id}"
    mode = args.mode  # "webhook" or "websocket"
    output_dir = Path(args.output) / f"openclaw-plugin-{channel_id}"

    # Get template directory
    script_dir = Path(__file__).parent
    template_dir = script_dir.parent / "assets" / "template"

    # Prepare context
    context = {
        "CHANNEL_ID": channel_id,
        "CHANNEL_LABEL": channel_label,
        "CHANNEL_CLASS": channel_class,
        "NPM_SCOPE": npm_scope,
        "CHANNEL_ALIASES_JSON": json.dumps([channel_id]),
        "MODE": mode,
    }

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    tests_dir = output_dir / "tests"
    tests_dir.mkdir(exist_ok=True)

    # Common template file mappings
    common_templates = [
        ("package.json.template", "package.json"),
        ("openclaw.plugin.json.template", "openclaw.plugin.json"),
        ("index.js.template", "index.js"),
        ("channel.js.template", "channel.js"),
        ("logger.js.template", "logger.js"),
        ("utils.js.template", "utils.js"),
        ("README.md.template", "README.md"),
    ]

    # Mode-specific templates
    if mode == "websocket":
        mode_templates = [
            ("receive.websocket.js.template", "receive.websocket.js"),
            ("webhook.js.template", "webhook.js"),  # Still include basic webhook for reference
        ]
    else:  # webhook mode (default)
        mode_templates = [
            ("webhook.js.template", "webhook.js"),
        ]

    # Test templates
    test_templates = [
        ("tests/mock-runtime.js", "mock-runtime.js"),
        ("tests/channel.test.js.template", "channel.test.js"),
        ("tests/webhook.test.js.template", "webhook.test.js"),
    ]

    # Generate common files
    for template_name, output_name in common_templates:
        template_path = template_dir / template_name
        if template_path.exists():
            template_content = load_template(template_path)
            output_content = replace_placeholders(template_content, context)
            output_path = output_dir / output_name
            output_path.write_text(output_content, encoding="utf-8")
            print(f"✅ Created: {output_path}")
        else:
            print(f"⚠️  Template not found: {template_path}")

    # Generate mode-specific files
    for template_name, output_name in mode_templates:
        template_path = template_dir / template_name
        if template_path.exists():
            template_content = load_template(template_path)
            output_content = replace_placeholders(template_content, context)
            output_path = output_dir / output_name
            output_path.write_text(output_content, encoding="utf-8")
            print(f"✅ Created: {output_path}")
        else:
            print(f"⚠️  Template not found: {template_path}")

    # Generate test files
    for template_name, output_name in test_templates:
        if template_name.endswith(".template"):
            template_path = template_dir / template_name
        else:
            template_path = template_dir / template_name

        if template_path.exists():
            template_content = load_template(template_path)
            output_content = replace_placeholders(template_content, context)
            output_path = tests_dir / output_name
            output_path.write_text(output_content, encoding="utf-8")
            print(f"✅ Created: {output_path}")
        else:
            # Try with .template extension
            template_path_with_ext = template_dir / f"{output_name}.template"
            if template_path_with_ext.exists():
                template_content = load_template(template_path_with_ext)
                output_content = replace_placeholders(template_content, context)
                output_path = tests_dir / output_name
                output_path.write_text(output_content, encoding="utf-8")
                print(f"✅ Created: {output_path}")
            else:
                print(f"⚠️  Template not found: {template_name}")

    # Print summary
    print("\n" + "=" * 60)
    print("🎉 Plugin created successfully!")
    print("=" * 60)
    print(f"\n📁 Location: {output_dir.absolute()}")
    print(f"🔌 Mode: {mode.upper()}")
    print(f"\n📋 Next steps:")
    print(f"   1. cd {output_dir}")

    if mode == "websocket":
        print(f"   2. Install channel SDK: npm install @your-channel/sdk")
        print(f"   3. Review and fill in TODO sections in:")
        print(f"      - channel.js (outbound adapter, config schema)")
        print(f"      - receive.websocket.js (WebSocket connection, message handling)")
    else:
        print(f"   2. Review and fill in TODO sections in:")
        print(f"      - channel.js (outbound adapter, config schema)")
        print(f"      - webhook.js (message parsing, signature verification)")

    print(f"   4. Run tests: npm test")
    print(f"   5. Install to OpenClaw: openclaw plugins install {output_dir}")
    print(f"\n📚 Reference:")
    print(f"   - See references/channel-adapters.md for adapter patterns")
    if mode == "websocket":
        print(f"   - See references/websocket-mode.md for WebSocket guide")
    print(f"   - See references/testing.md for testing guide")
    print()

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Generate OpenClaw channel plugin template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Webhook mode (default)
  %(prog)s --channel-id dingtalk --channel-label "钉钉"

  # WebSocket mode
  %(prog)s --channel-id feishu --channel-label "飞书" --mode websocket

  # With custom scope
  %(prog)s --channel-id lark --channel-label "Lark" --scope @myorg --mode websocket
        """,
    )

    parser.add_argument(
        "--channel-id",
        required=True,
        help="通道唯一标识符（如 'dingtalk', 'feishu'）",
    )

    parser.add_argument(
        "--channel-label",
        required=True,
        help="通道显示名称（如 '钉钉', '飞书'）",
    )

    parser.add_argument(
        "--mode",
        choices=["webhook", "websocket"],
        default="webhook",
        help="连接模式：webhook（默认）或 websocket",
    )

    parser.add_argument(
        "--scope",
        help="npm scope（如 '@myorg'）。默认：@<channel-id>",
    )

    parser.add_argument(
        "--output",
        default=".",
        help="输出目录。默认：当前目录",
    )

    args = parser.parse_args()

    try:
        return create_plugin(args)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
