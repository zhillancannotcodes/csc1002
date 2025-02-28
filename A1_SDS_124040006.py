import re

content = []           # Current text content as list of characters
cursor = 0             # Cursor position (index of the character it's on, or len(content) if after last character)
cursor_enabled = False # Whether the cursor is displayed
undo_stack = []        # Stack to store previous states for undo
command_history = []   # History of executed commands for repeat

help_text = """
? - display this help info
. - toggle row cursor on and off
h - move cursor left
l - move cursor right
^ - move cursor to beginning of the line
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
    undo_stack.append((content.copy(), cursor))

def display_content():
    """Display the current content, with cursor in green if enabled."""
    if not cursor_enabled:
        print(''.join(content))
    else:
        if cursor == len(content):  # Cursor at end
            print(''.join(content) + '\033[42m' + ' ' + '\033[0m')
        elif 0 <= cursor < len(content):  # Cursor within content
            print(''.join(content[:cursor]) + '\033[42m' + content[cursor] + '\033[0m' + ''.join(content[cursor+1:]))
        else:
            print(''.join(content))  # Fallback for invalid cursor

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
    
    if command == '.':
        save_state()
        cursor_enabled = not cursor_enabled
        command_history.append(command)
        return True
    
    elif command == 'h':
        save_state()
        if cursor > 0:
            cursor -= 1
        command_history.append(command)
        return True
    
    elif command == 'l':
        save_state()
        if cursor < len(content):
            cursor += 1
        command_history.append(command)
        return True
    
    elif command == '^':
        save_state()
        cursor = 0
        command_history.append(command)
        return True
    
    elif command == '$':
        save_state()
        cursor = len(content) - 1 if content else 0
        command_history.append(command)
        return True
    
    elif command == 'w':
        save_state()
        cursor = next_word_start(content, cursor)
        command_history.append(command)
        return True
    
    elif command == 'b':
        save_state()
        cursor = previous_word_start(content, cursor)
        command_history.append(command)
        return True
    
    elif re.match(r'^i(.+)', command):
        text = re.match(r'^i(.+)', command).group(1)
        save_state()
        content[cursor:cursor] = list(text)
        # Cursor remains at the same position
        command_history.append(command)
        return True
    
    elif re.match(r'^a(.+)', command):
        text = re.match(r'^a(.+)', command).group(1)
        save_state()
        insert_pos = min(cursor + 1, len(content))
        content[insert_pos:insert_pos] = list(text)
        cursor = insert_pos + len(text) - 1 if text else cursor
        command_history.append(command)
        return True
    
    elif command == 'x' and 0 <= cursor < len(content):
        save_state()
        del content[cursor]
        if cursor >= len(content):
            cursor = len(content) - 1 if content else 0
        command_history.append(command)
        return True
    
    elif command == 'dw':
        save_state()
        if cursor < len(content):
            next_pos = next_word_start(content, cursor)
            if next_pos > cursor:
                del content[cursor:next_pos]
            else:
                del content[cursor:]
            if cursor >= len(content):
                cursor = len(content) - 1 if content else 0
        command_history.append(command)
        return True
    
    elif command == 'u':
        if undo_stack:
            prev_content, prev_cursor = undo_stack.pop()
            content = prev_content
            cursor = prev_cursor
            if command_history:
                command_history.pop()
            return True
        return False  # Nothing to undo
    
    elif command == 'r':
        if command_history:
            last_command = command_history[-1]
            save_state()
            execute_command(last_command)  # Re-execute the last command
            command_history.append(last_command)
            return True
        return False  # No command to repeat
    
    elif command == 's':
        return True
    
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
        if execute_command(command):
            display_content()
