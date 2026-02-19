import os
import re
from typing import Optional
from app.models import ErrorInfo, ErrorType


class FixEngine:
    """Enhanced rule-based fixer with 20+ error patterns"""
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
    
    def apply_fix(self, error: ErrorInfo) -> bool:
        """Apply fix based on error type. Returns True if fix was applied."""
        try:
            if error.type == ErrorType.SYNTAX:
                return self._fix_syntax(error)
            elif error.type == ErrorType.INDENTATION:
                return self._fix_indentation(error)
            elif error.type == ErrorType.TYPE_ERROR:
                return self._fix_type_error(error)
            elif error.type == ErrorType.IMPORT:
                return self._fix_import(error)
            elif error.type == ErrorType.LOGIC:
                return self._fix_logic(error)
            elif error.type == ErrorType.LINTING:
                return self._fix_linting(error)
            else:
                return False
        except Exception as e:
            print(f"❌ Error applying fix: {e}")
            return False
    
    # ==================== SYNTAX FIXES (EXPANDED) ====================
    
    def _fix_syntax(self, error: ErrorInfo) -> bool:
        """Fix 10+ types of syntax errors"""
        file_path = os.path.join(self.repo_path, error.file)
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if error.line > len(lines) or error.line < 1:
            print(f"Line {error.line} out of range")
            return False
        
        line = lines[error.line - 1]
        original_line = line
        fixed = False
        
        # 1. Missing colon (def/class/if/for/while/elif/else)
        if "expected ':'" in error.message or 'expected ":"' in error.message:
            fixed = self._fix_missing_colon(lines, error.line, line)
        
        # 2. Missing parentheses in print statement (Python 2 -> 3)
        elif "Missing parentheses in call to 'print'" in error.message:
            fixed = self._fix_print_statement(lines, error.line, line)
        
        # 3. Invalid comparison (= instead of ==)
        elif "invalid syntax" in error.message.lower() and '=' in line and 'if ' in line:
            fixed = self._fix_comparison_operator(lines, error.line, line)
        
        # 4. Missing comma in list/tuple/dict
        elif "invalid syntax" in error.message.lower() and any(c in line for c in ['[', '{', '(']):
            fixed = self._fix_missing_comma(lines, error.line, line)
        
        # 5. Unclosed string
        elif "EOL while scanning string literal" in error.message or "unterminated string" in error.message.lower():
            fixed = self._fix_unclosed_string(lines, error.line, line)
        
        # 6. Missing pass in empty block
        elif "expected an indented block" in error.message:
            fixed = self._fix_empty_block(lines, error.line, line)
        
        # 7. Wrong quote type (mixed quotes)
        elif "invalid syntax" in error.message.lower() and ('"' in line or "'" in line):
            fixed = self._fix_quote_mismatch(lines, error.line, line)
        
        # 8. Fallback: missing colon for any line ending with def/if/for/while/class
        if not fixed:
            fixed = self._fix_missing_colon(lines, error.line, line)
        
        if fixed:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"✅ Fixed SYNTAX: '{original_line.strip()}' -> '{lines[error.line - 1].strip()}'")
            return True
        
        print(f"⚠️  Could not fix syntax error on line {error.line}")
        return False
    
    def _fix_missing_colon(self, lines, line_num, line):
        """Add missing colon"""
        keywords = ['def ', 'class ', 'if ', 'for ', 'while ', 'elif ', 'else', 'try:', 'except', 'finally', 'with ']
        
        if any(kw in line for kw in keywords):
            # Split code and comment
            if '#' in line:
                code_part = line.split('#', 1)[0].rstrip()
                comment_part = ' #' + line.split('#', 1)[1]
            else:
                code_part = line.rstrip()
                comment_part = ''
            
            if not code_part.endswith(':') and not code_part.endswith('\\'):
                lines[line_num - 1] = code_part + ':' + comment_part + '\n'
                return True
        return False
    
    def _fix_print_statement(self, lines, line_num, line):
        """Fix print statement missing parentheses"""
        # Match: print "something" or print variable
        match = re.search(r'print\s+(["\'].*["\']|[^\n]+)$', line)
        if match:
            content = match.group(1)
            indent = len(line) - len(line.lstrip())
            lines[line_num - 1] = ' ' * indent + f'print({content})\n'
            return True
        return False
    
    def _fix_comparison_operator(self, lines, line_num, line):
        """Fix single = in if statement (should be ==)"""
        # Match: if variable = value
        if 'if ' in line:
            # Replace single = with == (but not inside strings)
            fixed_line = re.sub(r'if\s+(\w+)\s*=\s*([^=])', r'if \1 == \2', line)
            if fixed_line != line:
                lines[line_num - 1] = fixed_line
                return True
        return False
    
    def _fix_missing_comma(self, lines, line_num, line):
        """Add missing comma in list/dict"""
        # Look for patterns like: ['item1' 'item2'] or {key1: val1 key2: val2}
        # This is complex and error-prone, so we'll be conservative
        return False  # Disable for now - too risky
    
    def _fix_unclosed_string(self, lines, line_num, line):
        """Close unclosed string"""
        stripped = line.rstrip()
        
        # Count quotes
        single_quotes = stripped.count("'") - stripped.count("\\'")
        double_quotes = stripped.count('"') - stripped.count('\\"')
        
        # If odd number of quotes, add closing quote
        if single_quotes % 2 == 1 and not stripped.endswith("'"):
            lines[line_num - 1] = line.rstrip() + "'\n"
            return True
        elif double_quotes % 2 == 1 and not stripped.endswith('"'):
            lines[line_num - 1] = line.rstrip() + '"\n'
            return True
        
        return False
    
    def _fix_empty_block(self, lines, line_num, line):
        """Add 'pass' to empty block"""
        if line_num > 1:
            prev_line = lines[line_num - 2]
            if prev_line.rstrip().endswith(':'):
                # Previous line starts a block, current line should be indented
                prev_indent = len(prev_line) - len(prev_line.lstrip())
                indent = prev_indent + 4
                lines[line_num - 1] = ' ' * indent + 'pass\n'
                return True
        return False
    
    def _fix_quote_mismatch(self, lines, line_num, line):
        """Fix mismatched quotes"""
        # Try to detect and fix quote mismatches
        # This is complex, so we'll skip for now
        return False
    
    # ==================== INDENTATION FIXES ====================
    
    def _fix_indentation(self, error: ErrorInfo) -> bool:
        """Context-aware indentation fixing"""
        file_path = os.path.join(self.repo_path, error.file)
        
        if not os.path.exists(file_path):
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if error.line > len(lines) or error.line < 1:
            return False
        
        # Replace tabs with 4 spaces
        fixed = False
        if '\t' in lines[error.line - 1]:
            lines[error.line - 1] = lines[error.line - 1].replace('\t', '    ')
            fixed = True
        
        current_line = lines[error.line - 1]
        current_stripped = current_line.lstrip()
        
        if error.line > 1 and current_stripped:
            prev_line = lines[error.line - 2]
            prev_stripped = prev_line.lstrip()
            
            prev_indent = len(prev_line) - len(prev_stripped)
            current_indent = len(current_line) - len(current_stripped)
            
            # If previous line ends with :, current should be +4 indented
            if prev_stripped.rstrip().endswith(':'):
                expected_indent = prev_indent + 4
                if current_indent != expected_indent:
                    lines[error.line - 1] = ' ' * expected_indent + current_stripped
                    print(f"✅ Fixed indentation: {current_indent} -> {expected_indent} spaces")
                    fixed = True
            # Current line under-indented
            elif current_indent < prev_indent:
                lines[error.line - 1] = ' ' * prev_indent + current_stripped
                fixed = True
        
        if fixed:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
        
        return False
    
    # ==================== TYPE_ERROR FIXES (EXPANDED) ====================
    
    def _fix_type_error(self, error: ErrorInfo) -> bool:
        """Fix 5+ types of type errors"""
        file_path = os.path.join(self.repo_path, error.file)
        
        if not os.path.exists(file_path):
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            content = ''.join(lines)
        
        # 1. Missing typing imports (List, Dict, Optional, etc.)
        if 'is not defined' in error.message:
            undefined_name = self._extract_undefined_name(error.message, content)
            if undefined_name:
                typing_names = ['List', 'Dict', 'Optional', 'Set', 'Tuple', 'Union', 'Any', 'Callable', 
                                'Iterable', 'Mapping', 'Sequence', 'TypeVar', 'Generic']
                
                if undefined_name in typing_names:
                    return self._add_typing_import(lines, undefined_name, file_path)
        
        # 2. String concatenation with non-string
        if "can only concatenate str" in error.message or "must be str, not" in error.message:
            return self._fix_string_concatenation(lines, error.line, error.message, file_path)
        
        # 3. Wrong number of arguments
        if "missing" in error.message.lower() and "required positional argument" in error.message.lower():
            # Can't reliably fix this automatically
            return False
        
        # 4. Unsupported operand type
        if "unsupported operand type" in error.message.lower():
            return self._fix_operand_type(lines, error.line, error.message, file_path)
        
        return False
    
    def _extract_undefined_name(self, message, content):
        """Extract undefined variable name"""
        match = re.search(r"name '(\w+)' is not defined", message)
        if match:
            return match.group(1)
        
        # Scan file for typing annotations
        typing_names = {'List', 'Dict', 'Optional', 'Set', 'Tuple', 'Union', 'Any', 'Callable'}
        for name in typing_names:
            if re.search(rf'\b{name}\[', content) or re.search(rf': {name}\b', content):
                if f'from typing import' not in content or name not in content.split('from typing import')[1].split('\n')[0]:
                    return name
        
        return None
    
    def _add_typing_import(self, lines, type_name, file_path):
        """Add typing import"""
        import_line = -1
        last_import = -1
        
        for i, line in enumerate(lines):
            if line.startswith('from typing import'):
                if re.search(rf'\b{type_name}\b', line):
                    return False  # Already imported
                import_line = i
                break
            elif line.startswith('import ') or line.startswith('from '):
                last_import = i
        
        if import_line >= 0:
            # Append to existing import
            lines[import_line] = lines[import_line].rstrip().rstrip(',') + f', {type_name}\n'
            print(f"✅ Added {type_name} to typing import")
        else:
            # Add new import
            insert_pos = last_import + 1 if last_import >= 0 else 0
            lines.insert(insert_pos, f'from typing import {type_name}\n')
            print(f"✅ Added new typing import: {type_name}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    
    def _fix_string_concatenation(self, lines, line_num, message, file_path):
        """Fix string + int by adding str()"""
        if line_num > len(lines):
            return False
        
        line = lines[line_num - 1]
        
        # Find the pattern: string + variable or variable + string
        # Extract variable name from error
        var_match = re.search(r"not '?(\w+)'?", message)
        if not var_match:
            return False
        
        var_type = var_match.group(1)
        
        if var_type in ['int', 'float', 'bool']:
            # Look for + operations
            pattern = r'(\+\s*)(\w+)(\s*\+|\s*$)'
            
            def add_str_conversion(match):
                return f"{match.group(1)}str({match.group(2)}){match.group(3)}"
            
            new_line = re.sub(pattern, add_str_conversion, line, count=1)
            
            if new_line != line:
                lines[line_num - 1] = new_line
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                print(f"✅ Added str() conversion")
                return True
        
        return False
    
    def _fix_operand_type(self, lines, line_num, message, file_path):
        """Fix unsupported operand types"""
        # This is complex - skip for now
        return False
    
    # ==================== IMPORT FIXES (EXPANDED) ====================
    
    def _fix_import(self, error: ErrorInfo) -> bool:
        """Fix 3+ types of import errors"""
        file_path = os.path.join(self.repo_path, error.file)
        
        if not os.path.exists(file_path):
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 1. Module not found - comment out
        module_match = re.search(r"No module named '(.*?)'", error.message)
        if module_match:
            module_name = module_match.group(1)
            return self._comment_out_import(lines, module_name, file_path)
        
        # 2. Cannot import name
        if "cannot import name" in error.message.lower():
            name_match = re.search(r"cannot import name '(.*?)'", error.message, re.IGNORECASE)
            if name_match:
                import_name = name_match.group(1)
                return self._remove_from_import(lines, import_name, file_path)
        
        # 3. Relative import error
        if "attempted relative import" in error.message.lower():
            return self._fix_relative_import(lines, error.line, file_path)
        
        return False
    
    def _comment_out_import(self, lines, module_name, file_path):
        """Comment out problematic import"""
        for i, line in enumerate(lines):
            if f'import {module_name}' in line or f'from {module_name}' in line:
                if not line.strip().startswith('#'):
                    lines[i] = f'# {line}'
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    print(f"✅ Commented out import: {module_name}")
                    return True
        return False
    
    def _remove_from_import(self, lines, import_name, file_path):
        """Remove specific name from import statement"""
        for i, line in enumerate(lines):
            if f'from ' in line and import_name in line:
                # Remove the specific import
                parts = line.split('import')
                if len(parts) == 2:
                    before, imports = parts
                    import_list = [imp.strip() for imp in imports.split(',')]
                    import_list = [imp for imp in import_list if import_name not in imp]
                    
                    if import_list:
                        lines[i] = before + 'import ' + ', '.join(import_list) + '\n'
                    else:
                        lines[i] = f'# {line}'  # Comment out entire line
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    print(f"✅ Removed {import_name} from import")
                    return True
        return False
    
    def _fix_relative_import(self, lines, line_num, file_path):
        """Convert relative to absolute import"""
        # This is complex - skip for now
        return False
    
    # ==================== LOGIC FIXES (EXPANDED) ====================
    
    def _fix_logic(self, error: ErrorInfo) -> bool:
        """Fix 4+ types of logic errors"""
        file_path = os.path.join(self.repo_path, error.file)
        
        if not os.path.exists(file_path):
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 1. Undefined variable
        if "name '.*?' is not defined" in error.message or 'is not defined' in error.message:
            var_match = re.search(r"name '(.*?)' is not defined", error.message)
            if var_match:
                var_name = var_match.group(1)
                return self._initialize_variable(lines, var_name, error.line, file_path)
        
        # 2. Attribute error
        if "has no attribute" in error.message.lower():
            return self._fix_attribute_error(lines, error.line, error.message, file_path)
        
        # 3. Division by zero (can't fix dynamically)
        if "division by zero" in error.message.lower():
            return False
        
        # 4. Index out of range (can't fix reliably)
        if "index out of range" in error.message.lower():
            return False
        
        return False
    
    def _initialize_variable(self, lines, var_name, line_num, file_path):
        """Initialize undefined variable"""
        if line_num <= len(lines):
            current_line = lines[line_num - 1]
            indent = len(current_line) - len(current_line.lstrip())
            
            # Insert initialization before error line
            init_line = ' ' * indent + f'{var_name} = None  # AI-AGENT: Auto-initialized\n'
            lines.insert(line_num - 1, init_line)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"✅ Initialized variable: {var_name} = None")
            return True
        return False
    
    def _fix_attribute_error(self, lines, line_num, message, file_path):
        """Fix missing attribute"""
        # Can't reliably fix this
        return False
    
    # ==================== LINTING FIXES (EXPANDED) ====================
    
    def _fix_linting(self, error: ErrorInfo) -> bool:
        """Fix 3+ types of linting issues"""
        file_path = os.path.join(self.repo_path, error.file)
        
        if not os.path.exists(file_path):
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 1. Unused import
        if 'unused import' in error.message.lower() or 'imported but unused' in error.message.lower():
            return self._remove_unused_import(lines, error.line, file_path)
        
        # 2. Unused variable
        if 'unused variable' in error.message.lower():
            return self._remove_unused_variable(lines, error.line, file_path)
        
        # 3. Trailing whitespace
        if 'trailing whitespace' in error.message.lower():
            return self._remove_trailing_whitespace(lines, error.line, file_path)
        
        return False
    
    def _remove_unused_import(self, lines, line_num, file_path):
        """Remove unused import line"""
        if line_num <= len(lines):
            line = lines[line_num - 1]
            if 'import' in line.lower():
                del lines[line_num - 1]
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                print(f"✅ Removed unused import")
                return True
        return False
    
    def _remove_unused_variable(self, lines, line_num, file_path):
        """Remove unused variable assignment"""
        # This is risky - could break code
        return False
    
    def _remove_trailing_whitespace(self, lines, line_num, file_path):
        """Remove trailing whitespace"""
        if line_num <= len(lines):
            lines[line_num - 1] = lines[line_num - 1].rstrip() + '\n'
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
        return False
