import sys
sys.path.append('src')
from tools.file_parser import ResumeParser

parser = ResumeParser()
text = """John Doe
john.doe@email.com
+1-555-0123

SUMMARY
Experienced software engineer with 5+ years in Python development

EXPERIENCE
Tech Corp
Senior Software Engineer"""

lines = [line.strip() for line in text.split('\n') if line.strip()]
print('Lines:', lines)

current_section = None
summary_text = ""

for i, line in enumerate(lines):
    line_lower = line.lower()
    print(f'Line {i}: {repr(line)}, current_section: {current_section}')
    
    # Check for section headers
    if any(keyword in line_lower for keyword in ['summary', 'objective', 'profile']):
        current_section = 'summary'
        print('  -> Set current_section to summary')
        continue
    
    if any(keyword in line_lower for keyword in ['experience', 'work history', 'employment']):
        current_section = 'experience'
        print('  -> Set current_section to experience')
        continue
    
    # Process content based on current section
    if current_section == 'summary' and line and line.upper() not in ['SUMMARY', 'OBJECTIVE', 'PROFILE']:
        summary_text += line + " "
        print(f'  -> Adding to summary: {line}')
    else:
        print('  -> Not adding to summary')

print('Final summary:', repr(summary_text.strip()))

# Test the actual method
result = parser._extract_resume_data_from_text(text)
print('Method result summary:', repr(result['summary']))
