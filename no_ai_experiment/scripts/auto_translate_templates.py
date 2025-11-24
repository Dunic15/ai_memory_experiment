#!/usr/bin/env python3
"""
Auto-Translation Template Wrapper (PROPERLY FIXED)
Adds {{ tr('...') }} with CORRECT Jinja2 syntax
"""

import re
import os
import sys

def wrap_text_in_tr(html_content):
    """
    Wraps English text in {{ tr('...') }} with proper Jinja2 syntax
    """
    
    modified = html_content
    
    # Helper function to escape single quotes in the text
    def escape_quotes(text):
        # Replace single quotes with double quotes inside tr()
        return text.replace("'", '"')
    
    # 1. Title tags
    def replace_title(match):
        text = match.group(1).strip()
        return f'<title>{{{{ tr("{escape_quotes(text)}") }}}}</title>'
    
    modified = re.sub(r'<title>([^<{]+)</title>', replace_title, modified)
    
    # 2. Headers (h1-h6)
    for level in range(1, 7):
        def replace_header(match):
            text = match.group(1).strip()
            return f'<h{level}>{{{{ tr("{escape_quotes(text)}") }}}}</h{level}>'
        
        modified = re.sub(rf'<h{level}>([^<{{]+)</h{level}>', replace_header, modified)
    
    # 3. Labels
    def replace_label(match):
        attrs = match.group(1)
        text = match.group(2).strip()
        asterisk = match.group(3)
        return f'<label{attrs}>{{{{ tr("{escape_quotes(text)}") }}}}{asterisk}</label>'
    
    modified = re.sub(r'<label([^>]*)>([^<{]+?)(\*?)</label>', replace_label, modified)
    
    # 4. Paragraphs
    def replace_p(match):
        attrs = match.group(1)
        text = match.group(2).strip()
        return f'<p{attrs}>{{{{ tr("{escape_quotes(text)}") }}}}</p>'
    
    modified = re.sub(r'<p([^>]*)>([^<{]+)</p>', replace_p, modified)
    
    # 5. Buttons
    def replace_button(match):
        attrs = match.group(1)
        text = match.group(2).strip()
        return f'<button{attrs}>{{{{ tr("{escape_quotes(text)}") }}}}</button>'
    
    modified = re.sub(r'<button([^>]*)>([^<{]+)</button>', replace_button, modified)
    
    # 6. Select options
    def replace_option(match):
        value = match.group(1)
        text = match.group(2).strip()
        return f'<option value="{value}">{{{{ tr("{escape_quotes(text)}") }}}}</option>'
    
    modified = re.sub(r'<option value="([^"]*)">([^<{]+)</option>', replace_option, modified)
    
    # 7. Strong/Bold
    def replace_strong(match):
        text = match.group(1).strip()
        return f'<strong>{{{{ tr("{escape_quotes(text)}") }}}}</strong>'
    
    modified = re.sub(r'<strong>([^<{]+?)</strong>', replace_strong, modified)
    
    return modified

def process_template(file_path, dry_run=True):
    """Process a single template file"""
    print(f"\n{'='*60}")
    print(f"Processing: {file_path}")
    print('='*60)
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        original = f.read()
    
    if '{{ tr(' in original or '{{ t(' in original:
        print("⚠️  File already has {{ tr() }} - skipping to avoid double-wrapping")
        return False
    
    modified = wrap_text_in_tr(original)
    
    if modified == original:
        print("ℹ️  No changes needed")
        return False
    
    print("\n✨ Sample changes:")
    print("-" * 60)
    
    orig_lines = original.split('\n')
    mod_lines = modified.split('\n')
    
    shown = 0
    for i, (o, m) in enumerate(zip(orig_lines, mod_lines), 1):
        if o != m and shown < 3:
            print(f"Line {i}:")
            print(f"  Before: {o.strip()[:70]}")
            print(f"  After:  {m.strip()[:70]}")
            shown += 1
    
    if shown == 3:
        print("... (more changes below)")
    print("-" * 60)
    
    if dry_run:
        print("\n⚠️  DRY RUN - no changes made")
        return False
    
    backup = file_path + '.backup'
    with open(backup, 'w', encoding='utf-8') as f:
        f.write(original)
    print(f"\n💾 Backup: {backup}")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(modified)
    print(f"✅ Updated: {file_path}")
    
    return True

def main():
    print("""
╔═══════════════════════════════════════════════╗
║   Auto-Translation Wrapper (FIXED VERSION)    ║
╚═══════════════════════════════════════════════╝
""")
    
    dry_run = '--apply' not in sys.argv
    
    if dry_run:
        print("🔍 DRY RUN MODE - Preview only")
        print("   Use --apply to make actual changes\n")
    else:
        print("⚠️  APPLY MODE - Will modify files!")
        if input("Continue? (y/n): ").lower() != 'y':
            return
    
    if not os.path.exists('templates'):
        print("❌ templates/ directory not found")
        print("   Run from project root")
        return
    
    files = [f for f in os.listdir('templates') if f.endswith('.html')]
    
    if not files:
        print("❌ No HTML files found")
        return
    
    print(f"Found {len(files)} files:\n")
    for i, f in enumerate(files, 1):
        print(f"  {i}. {f}")
    
    print("\n" + "="*60)
    print("Process:")
    print("  1. All files")
    print("  2. Select specific")
    print("  3. Just login.html (recommended)")
    
    choice = input("\nChoice (1/2/3): ").strip()
    
    to_process = []
    if choice == '1':
        to_process = files
    elif choice == '2':
        nums = input("File numbers (e.g., 1 3 5): ").strip().split()
        try:
            to_process = [files[int(n)-1] for n in nums]
        except:
            print("❌ Invalid")
            return
    elif choice == '3':
        to_process = ['login.html'] if 'login.html' in files else []
    
    if not to_process:
        print("❌ Nothing selected")
        return
    
    print(f"\nProcessing {len(to_process)} file(s)...")
    
    processed = 0
    skipped = 0
    
    for fname in to_process:
        try:
            if process_template(os.path.join('templates', fname), dry_run):
                processed += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"❌ Error in {fname}: {e}")
            skipped += 1
    
    print("\n" + "="*60)
    print("DONE!")
    print("="*60)
    print(f"Modified: {processed}, Skipped: {skipped}")
    
    if dry_run:
        print("\nTo apply: python3", sys.argv[0], "--apply")
    else:
        print("\n✅ Files updated!")
        print("\nNext:")
        print("  1. Restart server: python app.py")
        print("  2. Test in incognito")
        print("  3. Select Chinese")
        print("  4. Should auto-translate! 🎉")

if __name__ == '__main__':
    main()
