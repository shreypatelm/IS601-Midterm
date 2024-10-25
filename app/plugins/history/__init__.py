import os
import logging  # Ensure logging is imported
import pandas as pd
from tabulate import tabulate
from app.commands import Command

class HistoryCommand(Command):
    def __init__(self, command_handler, history_file='history.log', csv_file='history.csv'):
        self.command_handler = command_handler
        self.history_file = history_file
        self.csv_file = csv_file  # New variable to handle CSV file path
        self.load_history()

    def execute(self, *args):
        if len(args) == 0:
            print("Usage: history [save|clear|show|delete <index>]")
            return
        
        command = args[0]
        
        if command == "show":
            self.show_history()
        elif command == "clear":
            self.clear_history()
        elif command == "save":
            self.save_history()
        elif command == "delete" and len(args) > 1:
            try:
                index = int(args[1]) - 1  # Convert to zero-indexed
                self.delete_history_entry(index)
            except ValueError:
                print("Invalid index. Usage: history delete <index>")
        else:
            print("Unknown history command.")

    def load_history(self):
        """Load history from the history file."""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as file:
                self.command_handler.history = [line.strip() for line in file]
        else:
            self.command_handler.history = []

    def save_history(self):
        """Save the current history to a CSV file in table format."""
        history_data = []

        for i, entry in enumerate(self.command_handler.history, start=1):
            parts = entry.split(" = ")
            operation = parts[0] if parts else ""
            result = parts[1] if len(parts) > 1 else ""

            # Split the operation to get operands
            operands = operation.split()
            if len(operands) == 3:  # Format: operation operand1 operand2
                operation_type = operands[0]
                operand1 = operands[1]
                operand2 = operands[2]
            else:
                operation_type = operand1 = operand2 = ""

            # Append row data
            history_data.append({
                "No.": i,
                "Operation": operation_type,
                "Operand 1": operand1,
                "Operand 2": operand2,
                "Result": result
            })

        # Create a DataFrame from the history data
        df = pd.DataFrame(history_data)

        # Save to CSV file in table format
        df.to_csv(self.csv_file, index=False)
        logging.info("History saved to %s.", self.csv_file)  # Log the saving of history
        print(f"History saved to {self.csv_file}.")

    def clear_history(self):
        """Clear the history in memory and in the file."""
        self.command_handler.history = []
        open(self.history_file, 'w').close()  # Clear the file content
        self.save_history()  # Update the CSV after clearing
        logging.info("History cleared.")  # Log the clearing of history
        print("History cleared.")

    def show_history(self):
        """Show the command history in a tabular format."""
        if self.command_handler.history:
            # Prepare data for the DataFrame
            data = []
            for entry in self.command_handler.history:
                # Split the entry into command, operands, and result
                parts = entry.split(' = ')
                command_part = parts[0].strip()
                result_part = parts[1].strip() if len(parts) > 1 else "N/A"
                
                # Further split command_part to get operation and operands
                command_parts = command_part.split()
                operation = command_parts[0]
                operand1 = command_parts[1] if len(command_parts) > 1 else "N/A"
                operand2 = command_parts[2] if len(command_parts) > 2 else "N/A"
                
                # Append the row to data
                data.append([operation, operand1, operand2, result_part])
            
            # Create a DataFrame
            df = pd.DataFrame(data, columns=["Operation", "Operand 1", "Operand 2", "Result"])
            
            # Display the DataFrame as a pretty table with index starting from 1
            print(tabulate(df, headers='keys', tablefmt='pretty', showindex=[i + 1 for i in range(len(data))], numalign="center"))
        else:
            print("No command history found.")

    def delete_history_entry(self, index):
        """Delete a specific entry from the history by index."""
        if 0 <= index < len(self.command_handler.history):
            removed_command = self.command_handler.history.pop(index)
            self.save_history()  # Update the file after deletion
            logging.info("Deleted entry: %s", removed_command)  # Log the deleted entry
            print(f"Deleted entry: {removed_command}")
        else:
            print("Invalid index.")
            
