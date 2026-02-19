import os
import re
from typing import Optional
from app.models import ErrorInfo, ErrorType


class FixEngine:
    """Apply rule-based fixes to common errors"""
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
    
    def apply_fix(self, error: ErrorInfo) -> bool:
        """Apply fix based on error type. Returns True if fix was applied."""
        try:
            if error.type == ErrorType.LINTING:
                return self._fix_linting(error)
            elif error.type == ErrorType.SYNTAX:
                return self._fix_syntax(error)
            elif error.type == ErrorType.INDENTATION:
                return self._fix_indentation(error)
            elif error.type == ErrorType.IMPORT:
                return self._fix_import(error)
            elif error.type == ErrorType.LOGIC:
                return self._fix_logic(error)
            elif error.type == ErrorType.TYPE_ERROR:
                return self._fix_type_error(error)
            else:
                return False
        except Exception as e:
            print(f"Error applying fix: {e}")
            return False
    
    def _fix_linting(self, error: ErrorInfo) -> bool:
        """Remove unused imports"""
        file_path = os.path.join(self.repo_path, error.file)
        
        if not os.path.exists(file_path):
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if error.line <= len(lines):
            # Check if line contains import statement
            line_content = lines[error.line - 1]
            if 'import' in line_content.lower():
                # Remove the line
                del lines[error.line - 1]
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                return True
        
        return False
    
    def _fix_syntax(self, error: ErrorInfo) -> bool:
        """Fix syntax errors like missing colons"""
        file_path = os.path.join(self.repo_path, error.file)
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if error.line > len(lines) or error.line < 1:
            print(f"Line {error.line} out of range (file has {len(lines)} lines)")
            return False
        
        line = lines[error.line - 1]
        original_line = line
        
        # Check if this is a function/class definition missing colon
        if ('def ' in line or 'class ' in line or 'if ' in line or 
            'for ' in line or 'while ' in line or 'elif ' in line or 'else' in line):
            
            # Split code and comment parts
            if '#' in line:
                code_part = line.split('#', 1)[0].rstrip()
                comment_part = ' #' + line.split('#', 1)[1]
            else:
                code_part = line.rstrip()
                comment_part = ''
            
            # Check if code part (not comment) ends with colon
            if not code_part.endswith(':'):
                # Add colon after code, before comment
                lines[error.line - 1] = code_part + ':' + comment_part + '\n'
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                print(f"✓ Added colon: '{original_line.strip()}' -> '{lines[error.line - 1].strip()}'")
                return True
        
        print(f"Could not fix syntax error on line {error.line}: {line.strip()}")
        return False
    
    def _fix_indentation(self, error: ErrorInfo) -> bool:
        """Fix indentation errors by looking at context"""
        file_path = os.path.join(self.repo_path, error.file)
        
        if not os.path.exists(file_path):
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if error.line > len(lines) or error.line < 1:
            return False
        
        # Replace tabs with 4 spaces first
        fixed = False
        if '\t' in lines[error.line - 1]:
            lines[error.line - 1] = lines[error.line - 1].replace('\t', '    ')
            fixed = True
        
        # Smart indent fix: look at previous line for context
        current_line = lines[error.line - 1]
        current_stripped = current_line.lstrip()
        
        if error.line > 1 and current_stripped:
            prev_line = lines[error.line - 2]
            prev_stripped = prev_line.lstrip()
            
            # Get previous line's indentation
            prev_indent = len(prev_line) - len(prev_stripped)
            current_indent = len(current_line) - len(current_stripped)
            
            # If previous line ends with : (block start), current should be +4 indented
            if prev_stripped.rstrip().endswith(':'):
                expected_indent = prev_indent + 4
                if current_indent != expected_indent:
                    lines[error.line - 1] = ' ' * expected_indent + current_stripped
                    print(f"✓ Fixed indentation: {current_indent} -> {expected_indent} spaces")
                    fixed = True
            # If current line is under-indented compared to context
            elif current_indent < prev_indent:
                # Use same indentation as previous line
                lines[error.line - 1] = ' ' * prev_indent + current_stripped
                print(f"✓ Fixed indentation: {current_indent} -> {prev_indent} spaces")
                fixed = True
        
        if fixed:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
        
        return False
    
    def _fix_import(self, error: ErrorInfo) -> bool:
        """Fix import errors by removing problematic imports"""
        file_path = os.path.join(self.repo_path, error.file)
        
        if not os.path.exists(file_path):
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Extract module name from error
        module_match = re.search(r"No module named '(.*?)'", error.message)
        if not module_match:
            module_match = re.search(r"ModuleNotFoundError.*'(.*?)'", error.message)
        
        if module_match:
            module_name = module_match.group(1)
            
            # Find and comment out the import line
            for i, line in enumerate(lines):
                if f'import {module_name}' in line or f'from {module_name}' in line:
                    lines[i] = f'# {line}'  # Comment out instead of removing
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    return True
        
        return False
    
    def _fix_logic(self, error: ErrorInfo) -> bool:
        """Fix NameError by initializing undefined variables"""
        file_path = os.path.join(self.repo_path, error.file)
        
        if not os.path.exists(file_path):
            return False
        
        # Extract variable name
        var_match = re.search(r"name '(.*?)' is not defined", error.message)
        if not var_match:
            return False
        
        var_name = var_match.group(1)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if error.line <= len(lines):
            # Get indentation of current line
            current_line = lines[error.line - 1]
            indent = len(current_line) - len(current_line.lstrip())
            
            # Insert variable initialization before the error line
            init_line = ' ' * indent + f'{var_name} = None  # AI-AGENT: Auto-initialized\n'
            lines.insert(error.line - 1, init_line)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
        
        return False
    
    def _fix_type_error(self, error: ErrorInfo) -> bool:
        """Fix type annotation errors - add missing imports"""
        file_path = os.path.join(self.repo_path, error.file)
        
        if not os.path.exists(file_path):
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            content = ''.join(lines)
        
        # Extract the undefined name from error message
        undefined_name = None
        
        # Check if error is about undefined name (like List, Dict, Optional, etc.)
        if 'is not defined' in error.message or 'not defined' in error.message:
            # Extract the undefined name
            match = re.search(r"name '(\w+)' is not defined", error.message)
            if not match:
                match = re.search(r"'(\w+)' is not defined", error.message)
            
            if match:
                undefined_name = match.group(1)
        
        # If we couldn't find it in the error message, scan the entire file for typing annotations
        if not undefined_name:
            # Look for type annotations using common typing names that aren't imported
            typing_names = {'List', 'Dict', 'Optional', 'Set', 'Tuple', 'Union', 'Any', 'Callable'}
            
            # Check what's already imported
            imported_types = set()
            from_typing_pattern = r'from typing import (.+)'
            for line in lines:
                typing_match = re.match(from_typing_pattern, line)
                if typing_match:
                    imports = typing_match.group(1)
                    imported_types.update(imp.strip() for imp in imports.split(','))
            
            # Find which typing names are used but not imported
            for name in typing_names:
                # Check if name is used in type annotations but not imported
                if not re.search(rf'\bfrom typing import.*\b{name}\b', content):
                    # Look for usage patterns
                    if re.search(rf'\b{name}\[', content) or re.search(rf': {name}\b', content):
                        undefined_name = name
                        break
        
        if undefined_name:
            print(f"Detected undefined type: {undefined_name}")
            
            # Common typing imports
            typing_names = ['List', 'Dict', 'Optional', 'Set', 'Tuple', 'Union', 'Any', 'Callable']
            
            if undefined_name in typing_names:
                # Find where to add the import
                import_line = -1
                last_import = -1
                
                for i, line in enumerate(lines):
                    if line.startswith('from typing import'):
                        # Check if already imported
                        if re.search(rf'\b{undefined_name}\b', line):
                            print(f"Type {undefined_name} already imported")
                            return False  # Already imported
                        import_line = i
                        break
                    elif line.startswith('import ') or line.startswith('from '):
                        last_import = i
                
                if import_line >= 0:
                    # Append to existing typing import
                    lines[import_line] = lines[import_line].rstrip().rstrip(',') + f', {undefined_name}\n'
                    print(f"✓ Appended to existing typing import: {undefined_name}")
                else:
                    # Add new import after last import or at top
                    insert_pos = last_import + 1 if last_import >= 0 else 0
                    lines.insert(insert_pos, f'from typing import {undefined_name}\n')
                    print(f"✓ Added new typing import: {undefined_name}")
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                return True
        
        return False
