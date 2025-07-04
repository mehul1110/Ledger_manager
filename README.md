# Bahi-Khata: Professional Bookkeeping Software

Bahi-Khata is a comprehensive, desktop-based bookkeeping application designed for small businesses and personal finance management. Built with Python, Tkinter, and MySQL, it provides a robust platform for managing financial transactions with a focus on accuracy, security, and user-friendliness.

## Key Features

- **Double-Entry Accounting:** Ensures financial integrity and accuracy for all transactions.
- **Transaction Approval Workflow:** A secure, two-step process for approving and finalizing payments and receipts.
- **Comprehensive Transaction Management:** Easily record, view, and manage payments, receipts, and general journal entries.
- **Financial Reporting:** Generate detailed reports, including a journal entry viewer and a monthly balance sheet.
- **Asset Tracking:**
    - **Fixed Deposits (FDs):** Track FD investments, including maturity dates and interest calculations.
    - **Property Management:** Manage property assets with automated depreciation calculations for non-expendable items.
- **User-Friendly Interface:** A clean, responsive, and modern GUI built with Tkinter.
- **Secure Database:** All financial data is securely stored in a MySQL database.

## Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.x**
- **MySQL Server**

## Installation and Setup

Follow these steps to get the Bahi-Khata application running on your local machine.

### 1. Clone the Repository

First, clone this repository to your local machine:
```bash
git clone <repository-url>
cd Ledger_manager
```

### 2. Set Up the Database

You need to create a database in your MySQL server and configure the connection.

1.  **Create a Database:** Connect to your MySQL server and create a new database. You can name it `bahi_khata` or any other name you prefer.
    ```sql
    CREATE DATABASE bahi_khata;
    ```
2.  **Run the Setup Script:** The `setup_bahi_khata.sql` file contains all the necessary table structures. Execute this script in your new database to create the tables. You can do this using a tool like MySQL Workbench or via the command line:
    ```bash
    mysql -u your_username -p bahi_khata < setup_bahi_khata.sql
    ```
3.  **Configure Connection:** Open the `db_connect.py` file and update the `db_config` dictionary with your MySQL username, password, and the database name you created.

### 3. Install Dependencies

Install the required Python packages using the `requirements.txt` file located in the root directory:
```bash
pip install -r requirements.txt
```

## Running the Application

Once the setup is complete, you can run the application with the following command:

```bash
python frontend/app.py
```

## Building the Executable

To create a standalone executable file for Windows, you can use the `setup_cxfreeze.py` script. This script utilizes `cx_Freeze` to package the application and all its dependencies into a single distributable folder.

1.  Ensure all dependencies from `requirements.txt` are installed.
2.  Run the setup script from your terminal:
    ```bash
    python setup_cxfreeze.py build
    ```
This will create a `build` directory containing a sub-directory (e.g., `exe.win-amd64-3.9`) which holds the executable (`BAHI-KHATA.exe`) and all necessary files.

---
We hope you find this application useful. Feel free to contribute to its development by forking the repository and submitting pull requests.
