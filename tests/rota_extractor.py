import pdfplumber
from datetime import datetime, timedelta
from icalendar import Calendar, Event
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def extract_shifts_from_page(pdf_path, name):
    normalized_name = name.strip().lower()
    shifts = []
    
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        
        # Extract all tables from the page
        tables = page.extract_tables()
        
        # Process all tables
        all_rows = []
        for table in tables:
            all_rows.extend(table)
        
        # Find the row with the staff name (case-insensitive and partial match)
        staff_row = None
        for row in all_rows:
            for cell in row:
                if cell is not None and normalized_name in cell.strip().lower():
                    staff_row = row
                    break
            if staff_row:
                break
        
        if staff_row is None:
            print(f"Name '{name}' not found.")
            return
        
        # Extract final date from cell A2 (assuming it's the first cell of the second row)
        final_date_str = all_rows[1][0]  # Assuming A2 is in the second row and first column
        final_date = datetime.strptime(final_date_str, '%d/%m/%y')
        
        # Calculate the start date (Monday) of the week
        start_date = final_date - timedelta(days=final_date.weekday())
        
        # Extract the next 7 values after the staff name
        name_index = staff_row.index(next(cell for cell in staff_row if normalized_name in cell.strip().lower()))
        shift_values = staff_row[name_index+1:name_index+8]  # Get next 7 values
        
        # Create a new calendar
        cal = Calendar()
        
        # Add shifts as events to the calendar
        for i, value in enumerate(shift_values):
            shift_date = start_date + timedelta(days=i)
            shift_value = value.strip() if value else ''
            
            # Skip shifts containing "0.00 0.00"
            if "0.00 0.00" not in shift_value:
                parts = shift_value.split()
                
                if len(parts) >= 2:
                    start_time = parts[0]
                    end_time = parts[1]
                    
                    # Define event start time
                    event_start = datetime.combine(shift_date, datetime.strptime(start_time, '%H:%M').time())
                    
                    # If end time is earlier than start time, it means the shift ends after midnight
                    event_end = datetime.combine(shift_date, datetime.strptime(end_time, '%H:%M').time())
                    if event_end < event_start:
                        event_end += timedelta(days=1)
                    
                    # Create a new event
                    event = Event()
                    event.add('summary', f'{start_time}-{end_time}')
                    event.add('dtstart', event_start)
                    event.add('dtend', event_end)
                    cal.add_component(event)
        
        # Write the calendar to a file
        with open(f'{name}_shifts.ics', 'wb') as f:
            f.write(cal.to_ical())
        print(f"Calendar file '{name}_shifts.ics' created successfully.")

def main():
    # Hide the root window for file dialog
    Tk().withdraw()
    
    # Prompt user to select a PDF file
    pdf_path = askopenfilename(filetypes=[("PDF files", "*.pdf")], title="Select the PDF rota")
    
    # Check if the user selected a file
    if not pdf_path:
        print("No file selected. Exiting...")
        return
    
    name = input("Enter staff name: ")
    extract_shifts_from_page(pdf_path, name)

if __name__ == '__main__':
    main()
