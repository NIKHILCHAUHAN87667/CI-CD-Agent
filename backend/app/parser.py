import re
from typing import List
from app.models import ErrorInfo, ErrorType


class ErrorParser:
    """Parse pytest output and extract structured error information"""
    
    def __init__(self):
        self.error_patterns = {
            ErrorType.SYNTAX: [
                r'SyntaxError',
                r"expected ':'",
                r'invalid syntax',
            ],
            ErrorType.INDENTATION: [
                r'IndentationError',
                r'unexpected indent',
                r'expected an indented block',
            ],
            ErrorType.IMPORT: [
                r'ModuleNotFoundError',
                r'No module named',
            ],
            ErrorType.TYPE_ERROR: [
                r'TypeError',
                r"name '(List|Dict|Set|Tuple|Optional|Union|Any|Callable)' is not defined",  # Specific typing types
                r"name '.*?' is not defined",  # Catches other undefined types
            ],
            ErrorType.LOGIC: [
                r'NameError',  # Now checked AFTER TYPE_ERROR
            ],
            ErrorType.LINTING: [
                r'unused import',
                r'imported but unused',
            ],
        }
        
        # Pattern to extract file and line number
        self.file_line_pattern = r'File "(.*?)", line (\d+)'
    
    def parse_errors(self, test_output: str, repo_path: str = None) -> List[ErrorInfo]:
        """Parse test output and return structured error information"""
        errors = []
        lines = test_output.split('\n')
        
        current_file = None
        current_line = None
        
        print(f"[PARSER] Parsing errors from test output (repo_path={repo_path})")
        
        for i, line in enumerate(lines):
            # Try to extract file and line number
            file_match = re.search(self.file_line_pattern, line)
            if file_match:
                current_file = file_match.group(1)
                current_line = int(file_match.group(2))
                
                print(f"[PARSER] Found file reference: {current_file}:{current_line}")
                
                # Skip frozen/built-in Python modules (these are cascade errors)
                if current_file.startswith('<frozen') or current_file.startswith('<'):
                    print(f"[PARSER] ❌ Skipped (frozen/builtin): {current_file}")
                    continue
                
                # CRITICAL: Only include errors from the actual repository
                # Skip system libraries, site-packages, Python stdlib
                import os
                
                # Check if path is absolute or relative
                is_absolute = os.path.isabs(current_file)
                
                if is_absolute:
                    # For absolute paths, check if they're in the repo
                    if repo_path:
                        normalized_file = os.path.normpath(current_file).lower()
                        normalized_repo = os.path.normpath(repo_path).lower()
                        print(f"[PARSER] ❌ Skipped (not in repo): {current_file}")
                            
                        # Skip if not in the repository
                        if not normalized_file.startswith(normalized_repo):
                            continue
                    else:
                        # Fallback: Skip common system paths
                        skip_patterns = [
                            'site-packages',
                            'Python313\\Lib',
                            'Python312\\Lib',
                            'Python311\\Lib',
                            'Python310\\Lib',
                            'dist-packages',
                            '/usr/lib/python',
                            '/usr/local/lib/python',
                            'AppData\\Roaming\\Python',
                            'AppData\\Local\\Programs\\Python'
                        ]
                        if any(pattern in current_file for pattern in skip_patterns):
                            print(f"[PARSER] ❌ Skipped (system path): {current_file}")
                            continue
                else:
                    # For relative paths, skip only obvious system patterns
                    # (most relative paths are from the repo itself)
                    skip_patterns = [
                        'site-packages',
                        'pytest',
                        'pluggy',
                        '_pytest',
                        'importlib',
                        'unittest'
                    ]
                    if any(pattern in current_file for pattern in skip_patterns):
                        print(f"[PARSER] ❌ Skipped (system module): {current_file}")
                        continue
                
                # Look ahead for error type
                error_type, error_message = self._identify_error_type(
                    line, lines[i:min(i+5, len(lines))]
                )
                
                if error_type and current_file and current_line:
                    print(f"[PARSER] ✅ Detected {error_type.value} error in {current_file}:{current_line}")
                    errors.append(ErrorInfo(
                        file=current_file,
                        line=current_line,
                        type=error_type,
                        message=error_message
                    ))
        
        print(f"[PARSER] Total errors detected: {len(errors)}")
        return errors
    
    def _identify_error_type(self, current_line: str, context_lines: List[str]) -> tuple:
        """Identify error type from line and context"""
        # Combine current line and next few lines for context
        combined_text = '\n'.join(context_lines)
        
        for error_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    # Extract error message
                    message_match = re.search(pattern, combined_text, re.IGNORECASE)
                    message = message_match.group(0) if message_match else combined_text[:100]
                    return error_type, message
        
        # If no match found
        return ErrorType.UNKNOWN, "Unknown error"
    
    def parse_pytest_summary(self, output: str) -> dict:
        """Extract summary information from pytest output"""
        summary = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
        }
        
        # Look for pytest summary line
        summary_pattern = r'(\d+) failed.*?(\d+) passed'
        match = re.search(summary_pattern, output)
        if match:
            summary["failed"] = int(match.group(1))
            summary["passed"] = int(match.group(2))
            summary["total_tests"] = summary["failed"] + summary["passed"]
        
        # Alternative pattern
        failed_only = re.search(r'(\d+) failed', output)
        if failed_only and not match:
            summary["failed"] = int(failed_only.group(1))
        
        passed_only = re.search(r'(\d+) passed', output)
        if passed_only and not match:
            summary["passed"] = int(passed_only.group(1))
            
        return summary
