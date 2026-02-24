import os
import re

def remove_all_comments(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    cleaned_lines = []
    in_docstring = False
    docstring_char = None
    
    for line in lines:
        stripped = line.lstrip()
        
        if not in_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                docstring_char = stripped[:3]
                if stripped.count(docstring_char) >= 2 and len(stripped) > 6:
                    continue
                in_docstring = True
                continue
            
            if '#' in line:
                in_string = False
                quote_char = None
                new_line = ''
                escape_next = False
                
                for i, char in enumerate(line):
                    if escape_next:
                        new_line += char
                        escape_next = False
                        continue
                    
                    if char == '\\':
                        escape_next = True
                        new_line += char
                        continue
                    
                    if char in ['"', "'"]:
                        if not in_string:
                            in_string = True
                            quote_char = char
                        elif char == quote_char:
                            in_string = False
                            quote_char = None
                        new_line += char
                        continue
                    
                    if char == '#' and not in_string:
                        break
                    
                    new_line += char
                
                cleaned_lines.append(new_line.rstrip())
            else:
                cleaned_lines.append(line.rstrip())
        else:
            if docstring_char in line:
                in_docstring = False
                continue
    
    return '\n'.join(cleaned_lines)

files = [
    'D:\\genai-media-verifier\\backend\\models\\video\\physiological_analyzer.py',
    'D:\\genai-media-verifier\\backend\\models\\video\\quick_detector.py',
    'D:\\genai-media-verifier\\backend\\models\\video\\temporal_analyzer.py',
    'D:\\genai-media-verifier\\backend\\models\\video\\video_3d_model.py',
    'D:\\genai-media-verifier\\backend\\models\\video\\comprehensive_detector.py'
]

for filepath in files:
    try:
        print(f"Processing {os.path.basename(filepath)}...")
        cleaned_content = remove_all_comments(filepath)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        print(f"  Done!")
    except Exception as e:
        print(f"  Error: {e}")

print("\nAll remaining files processed!")
