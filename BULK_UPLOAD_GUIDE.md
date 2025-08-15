# Student Bulk Upload Feature Guide

## Overview
The bulk upload feature allows administrators to import multiple student records at once using CSV or Excel files through the Django admin panel.

## Access
1. Login to Django admin panel (`/admin/`)
2. Navigate to **Core** > **Scholarship Students**
3. Click the **"Bulk Upload Students"** button in the top toolbar

## Features

### ✅ **File Support**
- **CSV files** (.csv)
- **Excel files** (.xlsx, .xls) - requires pandas library

### ✅ **User Interface**
- **Drag & Drop** file upload
- **Template Download** with sample data
- **Progress tracking** during upload
- **Detailed error reporting** with row-level feedback
- **Success/failure notifications**

### ✅ **Data Validation**
- **Required field validation**
- **Date format parsing** (YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY)
- **Choice field validation** (gender, class, status)
- **Program lookup and validation**
- **Numeric field validation**

## CSV Template Fields

### Required Fields (*)
- `full_name` * - Student's full name
- `date_of_birth` * - Birth date (YYYY-MM-DD format)
- `gender` * - male/female
- `school_name` * - Name of the school
- `school_address` * - Complete school address
- `current_class` * - Education level (see choices below)
- `scholarship_amount` * - Amount in numbers (e.g., 50000.00)
- `scholarship_start_date` * - Start date (YYYY-MM-DD)
- `guardian_name` * - Parent/Guardian name
- `guardian_relationship` * - Relationship (Father, Mother, etc.)
- `guardian_phone` * - Guardian's phone number
- `guardian_address` * - Guardian's complete address

### Optional Fields
- `phone_number` - Student/guardian phone
- `email` - Student/guardian email
- `program` - Program name (must exist in system)
- `scholarship_end_date` - End date (YYYY-MM-DD)
- `scholarship_status` - active/completed/suspended/discontinued
- `notes` - Additional information

## Education Level Choices
Use these exact values for `current_class`:
- `primary_1` to `primary_6`
- `jss_1` to `jss_3`
- `sss_1` to `sss_3`
- `university_year_1` to `university_year_4`
- `postgraduate`

## Upload Process
1. **Download Template** - Get the CSV template with proper headers
2. **Fill Data** - Add student information following the format
3. **Upload File** - Drag & drop or select your completed CSV/Excel file
4. **Review Results** - Check success/error messages
5. **Verify Data** - Review imported students in the admin list

## Error Handling
- **Row-level validation** with specific error messages
- **Transaction safety** - all records imported or none
- **Error limits** - prevents import if too many errors
- **Detailed reporting** - shows exactly what went wrong

## Sample Data
```csv
full_name,date_of_birth,gender,school_name,current_class,scholarship_amount,scholarship_start_date,guardian_name,guardian_relationship,guardian_phone,guardian_address
John Doe,2010-05-15,male,Sample Primary School,primary_5,50000.00,2024-01-15,Jane Doe,Mother,+234-123-456-789,123 Home Street, Lagos
```

## Admin Features
- **Bulk actions** for status updates
- **Advanced filtering** and search
- **Export capabilities**
- **User tracking** - records who imported each student

## Technical Notes
- Uses Django transactions for data integrity
- Supports multiple date formats
- Validates against model constraints
- Optimized for large datasets
- Secure admin-only access

## Troubleshooting

### Common Issues
1. **Date format errors** - Use YYYY-MM-DD format
2. **Invalid class values** - Use exact choices from the list
3. **Missing required fields** - Ensure all required fields are filled
4. **File encoding issues** - Save CSV as UTF-8

### Support
Contact the development team for technical issues or feature requests.