import re

# Global variables to maintain editor state
content = ""           # Current text content
cursor = 0             # Cursor position (index of the character it's on)
cursor_enabled = False # Whether the cursor is displayed
undo_stack = []        # Stack to store previous states for undo
command_history = []   # History of executed commands for repeat

# Help text displayed when '?' is entered
help_text = """
? - display this help info
- - toggle row cursor on and off
h - move cursor left
l - move cursor right
A - move cursor to beginning of the line
$ - move cursor to end of the line
w - move cursor to beginning of next word
b - move cursor to beginning of previous word
i - insert <text> before cursor
a - append <text> after cursor
x - delete character at cursor
dw - delete word and trailing spaces at cursor
u - undo previous command
r - repeat last command
s - show content
q - quit program
"""
def save_state():
    """Save the current state (content and cursor) to the undo stack."""
    global undo_stack, content, cursor
    undo_stack.append((content, cursor))

def display_content():
    """Display the current content, with cursor in green if enabled."""
    if not cursor_enabled or not content:
        print(content)
    else:
        if cursor == len(content):  # Cursor at end
            print(content + '\033[42m' + ' ' + '\033[0m')
        elif 0 <= cursor < len(content):  # Cursor within content
            print(content[:cursor] + '\033[42m' + content[cursor] + '\033[0m' + content[cursor+1:])
        else:
            print(content)  # Fallback for invalid cursor

def next_word_start(content, cursor):
    """Find the starting index of the next word after the cursor."""
    if cursor >= len(content):
        return cursor
    # If cursor is on a non-space, skip to the end of the current word
    if not content[cursor].isspace():
        i = cursor + 1
        while i < len(content) and not content[i].isspace():
            i += 1
    else:
        i = cursor
    # Skip trailing spaces to find the next word's start
    while i < len(content) and content[i].isspace():
        i += 1
    if i < len(content):
        return i
    return cursor  # No next word, stay put

def previous_word_start(content, cursor):
    """Find the starting index of the previous word before the cursor."""
    if cursor <= 0:
        return 0
    # Find the first non-space character before the cursor
    i = cursor - 1
    while i >= 0 and content[i].isspace():
        i -= 1
    if i < 0:
        return 0
    # Find the start of that word
    while i > 0 and not content[i-1].isspace():
        i -= 1
    return i

def execute_command(command):
    """Execute the given command and update the editor state."""
    global content, cursor, cursor_enabled, undo_stack, command_history
    
    # Toggle cursor visibility
    if command == '-':
        save_state()
        cursor_enabled = not cursor_enabled
        command_history.append(command)
        return True
    
    # Move cursor left
    elif command == 'h':
        save_state()
        if cursor > 0:
            cursor -= 1
        command_history.append(command)
        return True
    
    # Move cursor right
    elif command == 'l':
        save_state()
        if content and cursor < len(content) - 1:
            cursor += 1
        command_history.append(command)
        return True
    
    # Move cursor to beginning
    elif command == 'A':
        save_state()
        cursor = 0
        command_history.append(command)
        return True
    
    # Move cursor to end
    elif command == '$':
        save_state()
        cursor = len(content) - 1 if content else 0
        command_history.append(command)
        return True
    
    # Move cursor to next word
    elif command == 'w':
        save_state()
        cursor = next_word_start(content, cursor)
        command_history.append(command)
        return True
    
    # Move cursor to previous word
    elif command == 'b':
        save_state()
        cursor = previous_word_start(content, cursor)
        command_history.append(command)
        return True
    
    # Insert text before cursor
    elif re.match(r'^i(.+)', command):
        text = re.match(r'^i(.+)', command).group(1)
        save_state()
        content = content[:cursor] + text + content[cursor:]
        # Cursor moves to the beginning of inserted text
        command_history.append(command)
        return True
    
    # Append text after cursor
    elif re.match(r'^a(.+)', command):
        text = re.match(r'^a(.+)', command).group(1)
        save_state()
        content = content[:cursor + 1] + text + content[cursor + 1:]
        cursor = cursor + len(text)  # Cursor moves to end of appended text
        command_history.append(command)
        return True
    
    # Delete character at cursor
    elif command == 'x' and content:
        save_state()
        content = content[:cursor] + content[cursor + 1:]
        cursor = min(cursor, len(content) - 1) if content else 0
        command_history.append(command)
        return True
    
    # Delete from cursor to start of next word or end
    elif command == 'dw':
        save_state()
        next_pos = next_word_start(content, cursor)
        if next_pos > cursor:
            content = content[:cursor] + content[next_pos:]
        else:
            content = content[:cursor]
        cursor = min(cursor, len(content) - 1) if content else 0
        command_history.append(command)
        return True
    
    # Undo last command
    elif command == 'u':
        if undo_stack:
            prev_content, prev_cursor = undo_stack.pop()
            content = prev_content
            cursor = prev_cursor
            if command_history:
                command_history.pop()
            return True
        return False  # Nothing to undo
    
    # Repeat last command
    elif command == 'r':
        if command_history:
            last_command = command_history[-1]
            save_state()
            execute_command(last_command)  # Re-execute the last command
            command_history.append(last_command)
            return True
        return False  # No command to repeat
    
    # Show content (displayed anyway, so just return True)
    elif command == 's':
        return True
    
    # Invalid command
    return False

# Main loop to run the editor
while True:
    print('>', end=' ')
    command = input().strip()
    
    if command == 'q':
        break
    elif command == '?':
        print(help_text)
    else:
        # Execute command and display content if successful
        if execute_command(command):
            display_content()