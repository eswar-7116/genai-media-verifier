import os
import re

def remove_comments(content):
    lines = content.split('\n')
    cleaned = []
    in_docstring = False
    docstring_char = None
    
    for line in lines:
        stripped = line.lstrip()
        
        if not in_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                docstring_char = stripped[:3]
                if stripped.count(docstring_char) >= 2:
                    continue
                in_docstring = True
                continue
            
            if '#' in line:
                in_string = False
                quote_char = None
                new_line = ''
                for i, char in enumerate(line):
                    if char in ['"', "'"] and (i == 0 or line[i-1] != '\\'):
                        if not in_string:
                            in_string = True
                            quote_char = char
                        elif char == quote_char:
                            in_string = False
                    if char == '#' and not in_string:
                        break
                    new_line += char
                cleaned.append(new_line.rstrip())
            else:
                cleaned.append(line)
        else:
            if docstring_char in line:
                in_docstring = False
                continue
    
    return '\n'.join(cleaned)

files_to_process = [
    'D:\\genai-media-verifier\\backend\\models\\video\\comprehensive_detector.py',
    'D:\\genai-media-verifier\\backend\\models\\video\\compression_analyzer.py',
    'D:\\genai-media-verifier\\backend\\models\\video\\frame_extractor.py',
    'D:\\genai-media-verifier\\backend\\models\\video\\metadata_analyzer.py',
    'D:\\genai-media-verifier\\backend\\models\\video\\physics_checker.py',
    'D:\\genai-media-verifier\\backend\\models\\video\\physiological_analyzer.py',
    'D:\\genai-media-verifier\\backend\\models\\video\\quick_detector.py',
    'D:\\genai-media-verifier\\backend\\models\\video\\temporal_analyzer.py',
    'D:\\genai-media-verifier\\backend\\models\\video\\video_3d_model.py',
]

for filepath in files_to_process:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        cleaned = remove_comments(content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        
        print(f"Processed: {os.path.basename(filepath)}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

print("All video model files processed!")
