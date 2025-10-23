import sys
import json
from datetime import datetime
import os

# --- Configuration ---
# The file to store the tasks
TASK_FILE = 'tasks.json'

# --- Utility Functions ---

def load_tasks():
    """Loads tasks from the JSON file. Creates the file if it doesn't exist."""
    if not os.path.exists(TASK_FILE):
        return []
    try:
        with open(TASK_FILE, 'r') as f:
            # Handle empty file case
            content = f.read()
            return json.loads(content) if content else []
    except json.JSONDecodeError:
        # Handle invalid JSON content gracefully
        print(f"Error: {TASK_FILE} contains invalid JSON. Starting with an empty list.")
        return []
    except IOError as e:
        print(f"Error reading file {TASK_FILE}: {e}")
        return []

def save_tasks(tasks):
    """Saves the current list of tasks to the JSON file."""
    try:
        with open(TASK_FILE, 'w') as f:
            json.dump(tasks, f, indent=4)
    except IOError as e:
        print(f"Error writing to file {TASK_FILE}: {e}")

def get_next_id(tasks):
    """Calculates the next available unique ID."""
    if not tasks:
        return 1
    # Find the maximum existing ID and add 1
    return max(task['id'] for task in tasks) + 1

def find_task(tasks, task_id):
    """Finds a task by its ID."""
    try:
        task_id = int(task_id)
        return next((task for task in tasks if task['id'] == task_id), None)
    except ValueError:
        return None # Return None if ID is not a valid integer

def format_task(task):
    """Formats a single task for display."""
    # Use a descriptive status string and simplified date
    status_map = {
        'todo': '⚪ TODO',
        'in-progress': '🟡 IN-PROGRESS',
        'done': '🟢 DONE'
    }
    created_date = task['createdAt'][:10] # Get YYYY-MM-DD
    updated_date = task['updatedAt'][:16] # Get YYYY-MM-DD HH:MM

    return (
        f"[{task['id']:<3}] {status_map.get(task['status'], 'UNKNOWN'):<15} "
        f"Created: {created_date} | Updated: {updated_date} | "
        f"{task['description']}"
    )

# --- Command Handlers ---

def add_task(description):
    """Adds a new task."""
    tasks = load_tasks()
    now = datetime.now().isoformat()
    new_id = get_next_id(tasks)

    new_task = {
        'id': new_id,
        'description': description,
        'status': 'todo', # Default status
        'createdAt': now,
        'updatedAt': now
    }
    tasks.append(new_task)
    save_tasks(tasks)
    print(f"✅ Task added successfully (ID: {new_id})")

def update_task(task_id, new_description):
    """Updates the description of an existing task."""
    tasks = load_tasks()
    task = find_task(tasks, task_id)

    if task:
        task['description'] = new_description
        task['updatedAt'] = datetime.now().isoformat()
        save_tasks(tasks)
        print(f"✏️ Task {task_id} updated successfully.")
    else:
        print(f"❌ Error: Task with ID {task_id} not found.")

def delete_task(task_id):
    """Deletes a task by its ID."""
    tasks = load_tasks()
    # Note: find_task returns the item itself, we need to check if it exists
    task_to_delete = find_task(tasks, task_id)

    if task_to_delete:
        # Filter out the task to be deleted
        updated_tasks = [task for task in tasks if task['id'] != int(task_id)]
        save_tasks(updated_tasks)
        print(f"🗑️ Task {task_id} deleted successfully.")
    else:
        print(f"❌ Error: Task with ID {task_id} not found.")

def mark_task(task_id, new_status):
    """Marks a task as in-progress or done."""
    tasks = load_tasks()
    task = find_task(tasks, task_id)

    if task:
        task['status'] = new_status
        task['updatedAt'] = datetime.now().isoformat()
        save_tasks(tasks)
        print(f"🏷️ Task {task_id} marked as '{new_status}'.")
    else:
        print(f"❌ Error: Task with ID {task_id} not found.")

def list_tasks(status_filter=None):
    """Lists all tasks or tasks filtered by status."""
    tasks = load_tasks()

    # Apply filter if provided
    if status_filter and status_filter in ['todo', 'in-progress', 'done']:
        filtered_tasks = [task for task in tasks if task['status'] == status_filter]
        print(f"\n--- Tasks: {status_filter.upper()} ({len(filtered_tasks)}) ---")
    else:
        filtered_tasks = tasks
        print(f"\n--- All Tasks ({len(filtered_tasks)}) ---")
    
    if not filtered_tasks:
        print("No tasks found.")
        return

    # Sort tasks by ID
    filtered_tasks.sort(key=lambda t: t['id'])
    
    for task in filtered_tasks:
        print(format_task(task))
    print("-" * 60)

# --- Main CLI Logic ---

def print_help():
    """Prints the usage instructions."""
    print("\n📚 Task Tracker CLI Usage:")
    print("--------------------------------------------------------------------------------------------------")
    print("  task-cli <command> [arguments]")
    print("--------------------------------------------------------------------------------------------------")
    print("  add <description>                 : Add a new task.")
    print('                                      Example: task-cli add "Buy milk"')
    print("  update <id> <new_description>     : Update a task's description.")
    print('                                      Example: task-cli update 1 "Buy milk and eggs"')
    print("  delete <id>                       : Delete a task.")
    print("                                      Example: task-cli delete 1")
    print("  mark-in-progress <id>             : Mark a task as 'in-progress'.")
    print("                                      Example: task-cli mark-in-progress 1")
    print("  mark-done <id>                    : Mark a task as 'done'.")
    print("                                      Example: task-cli mark-done 1")
    print("  list                              : List all tasks.")
    print("                                      Example: task-cli list")
    print("  list <status>                     : List tasks by status (todo, in-progress, done).")
    print("                                      Example: task-cli list done")
    print("  help                              : Show this help message.")
    print("--------------------------------------------------------------------------------------------------")

def main():
    """The main function to process command-line arguments."""
    # sys.argv is a list of command-line arguments: [script_name, command, arg1, arg2, ...]
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    command = sys.argv[1].lower()
    
    # Simple input validation and command routing
    try:
        if command == 'add':
            if len(sys.argv) != 3: raise ValueError("Usage: task-cli add \"<description>\"")
            add_task(sys.argv[2])

        elif command == 'update':
            if len(sys.argv) != 4: raise ValueError("Usage: task-cli update <id> \"<new_description>\"")
            update_task(sys.argv[2], sys.argv[3])

        elif command == 'delete':
            if len(sys.argv) != 3: raise ValueError("Usage: task-cli delete <id>")
            delete_task(sys.argv[2])

        elif command == 'mark-in-progress':
            if len(sys.argv) != 3: raise ValueError("Usage: task-cli mark-in-progress <id>")
            mark_task(sys.argv[2], 'in-progress')

        elif command == 'mark-done':
            if len(sys.argv) != 3: raise ValueError("Usage: task-cli mark-done <id>")
            mark_task(sys.argv[2], 'done')

        elif command == 'list':
            # 'list' command can be followed by a status filter or nothing
            if len(sys.argv) == 2:
                list_tasks() # List all
            elif len(sys.argv) == 3:
                status = sys.argv[2].lower().replace('_', '-') # Handle todo/in_progress/in-progress
                if status == 'todotask': # handle the example's 'todotask' misnomer
                    status = 'todo'
                elif status == 'not-done': # A common synonym for 'todo' and 'in-progress' combined, but we'll treat it as 'todo' for simplicity based on the list examples
                    status = 'todo'
                
                # Check for valid status filters
                if status in ['done', 'todo', 'in-progress']:
                    list_tasks(status)
                else:
                    raise ValueError("Invalid status filter. Use 'done', 'todo', or 'in-progress'.")
            else:
                raise ValueError("Usage: task-cli list [status]")

        elif command == 'help':
            print_help()

        else:
            print(f"❌ Error: Unknown command '{command}'. Use 'task-cli help' for usage.")
            sys.exit(1)

    except ValueError as e:
        print(f"❌ Error: Invalid arguments. {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()