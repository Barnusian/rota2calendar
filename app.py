import pdfplumber
from flask import Flask, render_template, request, send_file
from datetime import datetime, timedelta
from icalendar import Calendar, Event
import io

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/whatisthis')
def what():
    return render_template('what.html')

@app.route('/howdoesthiswork')
def how():
    return render_template('how.html')

@app.route('/test')
def test():
        return render_template('testpage.html')

@app.route('/file_upload', methods=['POST', 'GET'])
def file_upload():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']
    if file.filename == '':
        return "No selected file"

    name = request.form.get('username')
    
    # Process the uploaded file directly
    ics_file = extract_shifts_from_pdf(file, name)
    
    # Send the .ics file as a downloadable attachment
    return send_file(ics_file, as_attachment=True, download_name="shifts.ics", mimetype="text/calendar")

def extract_shifts_from_pdf(pdf_file, name):
    normalized_name = name.strip().lower()
    shifts = []
    
    pdf_file.seek(0)  # Reset file pointer

    with pdfplumber.open(pdf_file) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()

        all_rows = []
        for table in tables:
            all_rows.extend(table)

        # Find the row with the staff name
        staff_row = None
        for row in all_rows:
            for cell in row:
                if cell and normalized_name in cell.strip().lower():
                    staff_row = row
                    break
            if staff_row:
                break

        if not staff_row:
            return "Name not found"

        final_date_str = all_rows[1][0]  # A2 cell
        final_date = datetime.strptime(final_date_str, '%d/%m/%y')
        start_date = final_date - timedelta(days=final_date.weekday())

        name_index = staff_row.index(next(cell for cell in staff_row if normalized_name in cell.strip().lower()))
        shift_values = staff_row[name_index+1:name_index+8]

        cal = Calendar()
        for i, value in enumerate(shift_values):
            shift_date = start_date + timedelta(days=i)
            shift_value = value.strip() if value else ''
            
            if "0.00 0.00" not in shift_value:
                parts = shift_value.split()
                if len(parts) >= 2:
                    start_time, end_time = parts[0], parts[1]
                    event_start = datetime.combine(shift_date, datetime.strptime(start_time, '%H:%M').time())
                    event_end = datetime.combine(shift_date, datetime.strptime(end_time, '%H:%M').time())
                    if event_end < event_start:
                        event_end += timedelta(days=1)

                    event = Event()
                    event.add('summary', f'{start_time}-{end_time}')
                    event.add('dtstart', event_start)
                    event.add('dtend', event_end)
                    cal.add_component(event)

        # Create an in-memory .ics file
        ics_data = io.BytesIO()
        ics_data.write(cal.to_ical())
        ics_data.seek(0)  # Reset buffer

        return ics_data  # Return file-like object

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
