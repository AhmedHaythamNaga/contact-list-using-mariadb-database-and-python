import mariadb
import sys
import re
from tkinter import *
from tkinter import messagebox

rows = []
rowWithData = []
index = 0
contactList = None
logged_in_user_id = None
toggle_state = None
r = 0

def submit():
    global e, p, contactList, rows, logged_in_user_id
    passcode = p.get()
    mail = e.get()
    if passcode and mail:
        try:
            conn = mariadb.connect(
                user="root",
                password="ahmed2006",
                host="localhost",
                database="internship",
                port=3306
            )
            print("Connected to MariaDB!")
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE email=? AND password=?", (mail, passcode))
            logged_in_user_id = cur.fetchone()
            if logged_in_user_id:
                logged_in_user_id = logged_in_user_id[0]
            else:
                messagebox.showerror("Error", "Invalid email or password.")
                return
            cur.execute("SELECT * FROM contacts WHERE user_id=?", (logged_in_user_id,))
            rows = cur.fetchall()
            print("Fetched rows from contacts table:", rows)
            login.destroy()  # Destroy the login window
            if contactList:
                contactList.destroy()
            show_contact_list()
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB database: {e}")
            messagebox.showerror("Error", "Failed to connect to database. Please try again later.")
            sys.exit(1)
    else:
        messagebox.showerror("Error", "Email and Password are mandatory.")

def show_contact_list():
    global listbox, contactList
    if contactList:
        contactList.destroy()
    contactList = Tk()
    label = Label(contactList, text="Contact List")
    label.pack(side=TOP)
    listbox = Listbox(contactList)
    listbox.pack(side=LEFT, fill=BOTH, expand=True)
    for row in rows:
        listbox.insert(END, row[2].split()[0])
    listbox.bind('<<ListboxSelect>>', showdetails)
    add_button = Button(contactList, text="Add Contact", command=add_contact)
    add_button.pack(side=BOTTOM)
    delete_button = Button(contactList, text="Delete Contact", command=delete_contact)
    delete_button.pack(side=BOTTOM)
    contactList.mainloop()

def add_contact():
    global addContact, rows
    addContact = Tk()
    addContact.title("Add Contact")

    Label(addContact, text="Full Name *:").grid(row=0, column=0, sticky=W)
    full_name_entry = Entry(addContact)
    full_name_entry.grid(row=0, column=1)

    Label(addContact, text="Email (optional):").grid(row=1, column=0, sticky=W)
    email_entry = Entry(addContact)
    email_entry.grid(row=1, column=1)

    Label(addContact, text="Phone Number *:").grid(row=2, column=0, sticky=W)
    phone_entry = Entry(addContact)
    phone_entry.grid(row=2, column=1)

    save_button = Button(addContact, text="Save", command=lambda: save_new_contact(full_name_entry.get(), email_entry.get(), phone_entry.get()))
    save_button.grid(row=3, columnspan=2)

    addContact.mainloop()

def save_new_contact(full_name, email, phone):
    global rows
    if not full_name or not phone:
        messagebox.showerror("Error", "Full Name and Phone Number are mandatory fields.")
        return

    # Validate email format
    if email:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Error", "Invalid email format.")
            return

    # Validate phone number format (assuming international format)
    if not re.match(r"^\+\d{1,3}\d{9,15}$", phone):
        messagebox.showerror("Error", "Invalid phone number format.")
        return

    try:
        conn = mariadb.connect(
            user="root",
            password="ahmed2006",
            host="localhost",
            database="internship",
            port=3306
        )
        cur = conn.cursor()

        # Check if email already exists
        if email:
            cur.execute("SELECT * FROM contacts WHERE email=?", (email,))
            existing_email = cur.fetchone()
            if existing_email:
                messagebox.showerror("Error", "Email already exists.")
                return

        # Check if phone number already exists
        cur.execute("SELECT * FROM contacts WHERE phone=?", (phone,))
        existing_phone = cur.fetchone()
        if existing_phone:
            messagebox.showerror("Error", "Phone number already exists.")
            return

        # Insert new contact into database
        cur.execute("INSERT INTO contacts (user_id, name, email, phone) VALUES (?, ?, ?, ?)",
                    (logged_in_user_id, full_name, email, phone))
        conn.commit()
        print("New contact added successfully!")

        # Refresh contact list
        cur.execute("SELECT * FROM contacts WHERE user_id=?", (logged_in_user_id,))
        rows = cur.fetchall()
        show_contact_list()

    except mariadb.Error as e:
        print(f"Error adding new contact: {e}")
        messagebox.showerror("Error", "Failed to add new contact. Please try again later.")
    finally:
        conn.close()

def showdetails(event=None):
    global index, rowWithData, contactDetail, toggle_state, name_entry, email_entry, phone_entry, r
    if listbox.curselection():
        index = listbox.curselection()[0]
        r = 0
        contactDetail = Tk()
        Label(contactDetail, text="Contact Detail").pack(side=TOP)

        try:
            conn = mariadb.connect(
                user="root",
                password="ahmed2006",
                host="localhost",
                database="internship",
                port=3306
            )
            cur = conn.cursor()
            cur.execute("SELECT * FROM contacts WHERE user_id=? LIMIT ?,1", (logged_in_user_id, index))
            rowWithData = cur.fetchone()

            Label(contactDetail, text="Name:").pack()
            name_entry = Entry(contactDetail)
            name_entry.insert(END, rowWithData[2])
            name_entry.pack()
            name_entry.config(state=DISABLED)

            Label(contactDetail, text="Email:").pack()
            email_entry = Entry(contactDetail)
            email_entry.insert(END, rowWithData[3])
            email_entry.pack()
            email_entry.config(state=DISABLED)

            Label(contactDetail, text="Phone:").pack()
            phone_entry = Entry(contactDetail)
            phone_entry.insert(END, rowWithData[4])
            phone_entry.pack()
            phone_entry.config(state=DISABLED)

            toggle_state = BooleanVar()
            toggle_button = Checkbutton(contactDetail, text="Enable Editing", variable=toggle_state, command=toggle_editing)
            toggle_button.pack()

            save_button = Button(contactDetail, text="Save", command=save)
            save_button.pack()

            contactDetail.mainloop()

        except mariadb.Error as e:
            print(f"Error fetching contact details from database: {e}")
            sys.exit(1)

def toggle_editing():
    global name_entry, email_entry, phone_entry, r
    r += 1
    if r % 2 != 0:
        name_entry.config(state=NORMAL)
        email_entry.config(state=NORMAL)
        phone_entry.config(state=NORMAL)
    else:
        name_entry.config(state=DISABLED)
        email_entry.config(state=DISABLED)
        phone_entry.config(state=DISABLED)

def save():
    global name_entry, email_entry, phone_entry, rowWithData, listbox, index, rows

    updated_name = name_entry.get().strip()
    updated_email = email_entry.get().strip()
    updated_phone = phone_entry.get().strip()

    if not updated_name or not updated_phone:
        messagebox.showerror("Error", "Full Name and Phone Number are mandatory fields.")
        return

    if updated_email:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", updated_email):
            messagebox.showerror("Error", "Invalid email format.")
            return

    if not re.match(r"^\+\d{1,3}\d{9,15}$", updated_phone):
        messagebox.showerror("Error", "Invalid phone number format.")
        return

    try:
        conn = mariadb.connect(
            user="root",
            password="ahmed2006",
            host="localhost",
            database="internship",
            port=3306
        )
        cur = conn.cursor()
        cur.execute("UPDATE contacts SET name=?, email=?, phone=? WHERE id=?",
                    (updated_name, updated_email, updated_phone, rowWithData[0]))
        conn.commit()
        print("Contact details updated successfully!")

        # Update the contact list
        rows[index] = (rowWithData[0], logged_in_user_id, updated_name, updated_email, updated_phone)
        listbox.delete(index)
        listbox.insert(index, updated_name.split()[0])

    except mariadb.Error as e:
        print(f"Error updating contact details: {e}")
        messagebox.showerror("Error", "Failed to update contact details. Please try again later.")
    finally:
        conn.close()

def delete_contact():
    global index, rows, listbox

    if not listbox.curselection():
        return

    try:
        conn = mariadb.connect(
            user="root",
            password="ahmed2006",
            host="localhost",
            database="internship",
            port=3306
        )
        cur = conn.cursor()
        cur.execute("DELETE FROM contacts WHERE id=?", (rows[index][0],))
        conn.commit()
        print("Contact deleted successfully!")


        listbox.delete(index)
        rows.pop(index)


        if contactDetail:
            contactDetail.destroy()

    except mariadb.Error as e:
        print(f"Error deleting contact: {e}")
        messagebox.showerror("Error", "Failed to delete contact. Please try again later.")
    finally:
        conn.close()


login = Tk()
Label(login, text="Email:").pack(side=LEFT)
e = Entry(login)
e.pack(side=LEFT)
Label(login, text="Password:").pack(side=LEFT)
p = Entry(login, show="*")
p.pack(side=LEFT)
Button(login, text="Submit", command=submit).pack(side=RIGHT)

login.mainloop()